"""
Post-hurricane road-recovery environment with a degraded, attackable
communication channel between the road sensors and the Digital Twin.

Everything the agent observes passes through `Channel`, so packet loss,
latency, and man-in-the-middle tampering change what the policy sees,
while rewards and decision accuracy are always computed on the TRUE state.

Modeling assumptions (state these in the paper):
  * Each road segment i has a true condition c_i in [0,1] (1 = intact),
    a hazard level h_i in [0,1], and a fixed traffic importance w_i.
  * A segment is inaccessible when c_i < 0.4.
  * Packet loss and latency make the DT keep an older (stale) report.
  * An active MITM rewrites a segment's reported condition. With the
    security layer OFF the rewritten value is accepted. With it ON, an
    attacked key block is detected when the measured BB84 QBER on a
    64-bit test sample exceeds 11% (intercept-resend raises the error rate
    by ~25%); detected reports are discarded and the DT keeps its last
    verified value. Undetected attacks (sampling luck) still get through.
"""
from __future__ import annotations

import numpy as np

ACTIONS = ["wait", "routine", "full"]
ACTION_COST = np.array([0.0, 1.0, 3.0])
QBER_THRESHOLD = 0.11
TEST_BITS = 64


class Channel:
    """Sensor -> Communication DT -> Computational DT delivery model."""

    def __init__(self, rng, packet_loss=0.0, latency_ms=0.0, attack_rate=0.0,
                 secure=False, base_qber=0.02, step_ms=250.0, qkd_avail=1.0,
                 refresh_ms=None, first_refresh_ms=None, refresh_every=50):
        self.rng = rng
        # refresh_ms: time the hop is busy for one hybrid key refresh (key exchange plus
        # authentication, compute and transmission). While busy, messages queue behind it,
        # so delivery lag is raised for every step until busy_ms is used up, not only the
        # step the refresh starts in -- a refresh can take several step_ms at a slow link
        # rate. first_refresh_ms covers round 1 when it differs (ML-DSA in round 1,
        # QKD-keyed MAC afterwards). None (default) keeps earlier results unchanged.
        self.refresh_ms, self.first_refresh_ms, self.refresh_every = refresh_ms, first_refresh_ms, refresh_every
        self.latency_ms, self.step_ms, self.busy_ms, self.refreshes = latency_ms, step_ms, 0.0, 0
        # qkd_avail < 1 models QKD-only operation: with probability 1 - qkd_avail
        # the feeder hop has no QKD key for a message, so it cannot be sent securely.
        # The default (1.0) draws no random number, so earlier results are unchanged.
        self.qkd_avail = qkd_avail
        self.packet_loss = packet_loss
        self.lag = int(latency_ms // step_ms)          # steps of delay
        self.attack_rate = attack_rate
        self.secure = secure
        self.base_qber = base_qber
        self.stats = dict(sent=0, dropped=0, attacked=0, detected=0, tampered_in=0)

    def reset(self):
        """Clear per-episode state (refresh cadence, busy time, counters) so a new
        episode doesn't inherit a mid-refresh hop or stale stats from the last one."""
        self.busy_ms, self.refreshes = 0.0, 0
        self.lag = int(self.latency_ms // self.step_ms)
        self.stats = dict(sent=0, dropped=0, attacked=0, detected=0, tampered_in=0)

    def new_step(self):
        """Called once per environment step, before any deliver() calls. Consumes
        one step_ms of any outstanding refresh busy time and recomputes lag from
        what remains, so a refresh that takes several steps keeps the hop delayed
        across all of them, not just the step it started in. self.lag is set ONLY
        here, so every segment in a step sees the same lag regardless of delivery
        order; a refresh triggered mid-step (in deliver()) adds to busy_ms for the
        *next* step's new_step() to pick up, rather than changing lag retroactively
        for segments already delivered or still to come in the step it fires in."""
        if self.busy_ms > 0:
            self.busy_ms = max(0.0, self.busy_ms - self.step_ms)
        self.lag = int((self.latency_ms + self.busy_ms) // self.step_ms)

    def deliver(self, true_c, history):
        """Return (reported_condition, fresh, verified, exposed_lag) for one segment.

        `history` holds this segment's true conditions for the last steps, so
        latency can return a delayed value. The value lookup is always clamped to
        available history; exposed_lag is what the caller should report as the
        "age" of that value. When no refresh_ms is configured (the default),
        exposed_lag is the raw, unclamped self.lag, exactly as before this
        feature existed, so runs with refresh_ms=None are bit-for-bit unchanged.
        When refresh_ms is set, exposed_lag is clamped the same way the value
        lookup is, since lag can then run well past the available history and an
        unclamped age would overstate how stale the returned value really is.
        """
        self.stats["sent"] += 1
        if self.refresh_ms is not None and (self.stats["sent"] - 1) % self.refresh_every == 0:
            first = self.refreshes == 0 and self.first_refresh_ms is not None
            self.busy_ms += self.first_refresh_ms if first else self.refresh_ms
            self.refreshes += 1
        if self.rng.random() < self.packet_loss:
            self.stats["dropped"] += 1
            return None, False, None, self.lag
        if self.secure and self.qkd_avail < 1.0 and self.rng.random() > self.qkd_avail:
            self.stats["dropped"] += 1
            return None, False, None, self.lag   # no key material: message held back
        value_lag = min(self.lag, len(history) - 1)
        value = history[-1 - value_lag]
        exposed_lag = value_lag if self.refresh_ms is not None else self.lag
        if self.rng.random() < self.attack_rate:
            self.stats["attacked"] += 1
            if self.secure:
                qber_true = min(0.5, self.base_qber + 0.25)
                errors = self.rng.binomial(TEST_BITS, qber_true)
                if errors / TEST_BITS > QBER_THRESHOLD:
                    self.stats["detected"] += 1
                    return None, False, "detected", exposed_lag  # discarded, keep last verified
            # attacker reports a damaged road as fine and vice versa
            self.stats["tampered_in"] += 1
            tampered = float(np.clip(1.0 - value + self.rng.normal(0, 0.05), 0, 1))
            # the DT cannot tell an undetected attack from a clean report
            return tampered, exposed_lag == 0, self.secure, exposed_lag
        # `verified` only means "passed the security check"; without the
        # security layer nothing can be verified
        return float(value), exposed_lag == 0, self.secure, exposed_lag


class RecoveryEnv:
    """Post-hurricane recovery with one decision per road segment per step.

    At every step the Computational DT holds an observed state for each of
    the n segments; one shared policy chooses wait / routine / full for each
    segment. Decision accuracy is scored for EVERY segment at every step
    against the TRUE condition, so communication errors change what the
    agent sees but never which decisions are scored.
    """

    def __init__(self, n_segments=15, horizon=12, lam=0.5, shock_p=0.05,
                 damage="random", comm_aware=True, rng=None, **channel_kw):
        self.n = n_segments
        self.T = horizon
        self.lam = lam
        self.shock_p = shock_p
        self.damage = damage
        self.comm_aware = comm_aware
        self.rng = rng or np.random.default_rng()
        self.channel = Channel(self.rng, **channel_kw)
        self.obs_dim = 5 if comm_aware else 3

    def _init_damage(self):
        pos = self.rng.random((self.n, 2))
        if self.damage == "concentrated":
            center = self.rng.random(2)
            d = np.linalg.norm(pos - center, axis=1)
            severity = np.exp(-(d ** 2) / (2 * 0.2 ** 2))
            c = 1.0 - 0.9 * severity + self.rng.normal(0, 0.05, self.n)
        else:
            c = self.rng.uniform(0.1, 1.0, self.n)
        self.c = np.clip(c, 0.05, 1.0)
        self.h = np.clip(1.0 - self.c + self.rng.normal(0, 0.1, self.n), 0, 1)
        self.w = self.rng.uniform(0.3, 1.0, self.n)

    def reset(self):
        self._init_damage()
        self.channel.reset()
        self.t = 0
        self.hist = [[x] for x in self.c]
        self.c_obs = self.c.copy()          # DT starts synchronized
        self.age = np.zeros(self.n)
        self.verified = np.full(self.n, 1.0 if self.channel.secure else 0.0)
        self.cost = 0.0
        return self._observe()

    def _sync(self):
        self.channel.new_step()
        for i in range(self.n):
            v, fresh, ver, used_lag = self.channel.deliver(self.c[i], self.hist[i])
            if v is None:
                self.age[i] += 1
                if ver == "detected":
                    self.verified[i] = 0.0      # DT knows this report was rejected
                continue
            self.c_obs[i] = v
            self.age[i] = 0 if fresh else used_lag
            self.verified[i] = 1.0 if ver else 0.0   # always 0 without security

    def _observe(self):
        self._sync()
        cols = [self.c_obs, self.h, self.w]
        if self.comm_aware:
            cols += [np.minimum(self.age, 10) / 10.0, self.verified]
        return np.stack(cols, axis=1).astype(np.float32)      # (n, obs_dim)

    @staticmethod
    def oracle_action(c):
        """Reference decision on the TRUE condition (decision accuracy)."""
        return np.where(c < 0.4, 2, np.where(c < 0.7, 1, 0))

    def step(self, a):
        a = np.asarray(a, dtype=int)
        before = self.c.copy()
        target = self.oracle_action(before)
        correct = (a == target)

        cost = ACTION_COST[a]
        self.cost += float(cost.sum())
        self.c = np.where(a == 1, np.minimum(1.0, self.c + 0.25), self.c)
        self.c = np.where(a == 2, 1.0, self.c)
        gain = self.c - before

        # Eq. (reward), per segment: R = R_general + lambda * R_specific
        r_general = self.w * gain - 0.1 * cost
        r_specific = np.where(correct, 1.0,
                     np.where((target == 2) & (a == 0), -1.0,
                     np.where((before >= 0.7) & (a > 0), -0.5, -0.25)))
        reward = r_general + self.lam * r_specific

        # after-effects: hazard-driven decay plus occasional new damage
        decay = 0.02 * self.h * self.rng.random(self.n)
        shock = (self.rng.random(self.n) < self.shock_p) * self.rng.uniform(0.3, 0.6, self.n)
        self.c = np.clip(self.c - decay - shock, 0.0, 1.0)
        self.h = np.clip(self.h * 0.97 + 0.5 * shock, 0, 1)
        for j in range(self.n):
            self.hist[j].append(self.c[j])
            if len(self.hist[j]) > self.T + 1:  # never clamp within one episode's own length
                self.hist[j].pop(0)

        self.t += 1
        done = self.t >= self.T
        obs = self._observe()
        info = dict(correct=int(correct.sum()), decisions=self.n)
        if done:
            info.update(health=float(self.c.mean()),
                        accessible=float((self.c >= 0.4).mean()),
                        cost=float(self.cost))
        return obs, reward.astype(np.float32), done, info
