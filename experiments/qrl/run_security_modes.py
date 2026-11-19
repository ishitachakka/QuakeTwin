"""R1 5.1 / 5.2: QKD-only vs PQC-only vs hybrid QKD+PQC, downstream decision accuracy.

Modeling (stated in the paper):
  * PQC-only and hybrid: tampered reports are rejected (AEAD tag / QBER check),
    and key establishment never blocks a message (ML-KEM is always available).
    In this decision model the two are therefore identical; QKD's extra value in the
    hybrid (long-term confidentiality, detection of passive eavesdropping) does not
    change what the Computational DT sees and is discussed qualitatively.
  * QKD-only: tampering is rejected, but with probability 1 - a the feeder hop has no
    QKD key for a message (key rate below demand), so the report is held back.
    a (key availability) is swept as a controlled parameter, not mapped to a hurricane level.
  * No security: reports are accepted as received.
"""
import json, sys, time
from pathlib import Path
import numpy as np, torch
from qt_agents import evaluate, train_ppo
from run_experiments import make_actor, LOSS, ATTACK, LATENCY, STRESS

torch.set_num_threads(1)
OUT = Path(__file__).parent / "results"
AVAIL = [1.0, 0.8, 0.6, 0.4, 0.2]

def sampler(secure, avail_choices=None):
    def f(rng):
        c = dict(packet_loss=float(rng.choice(LOSS)), attack_rate=float(rng.choice(ATTACK)),
                 latency_ms=float(rng.choice(LATENCY)), secure=secure)
        if avail_choices:
            c["qkd_avail"] = float(rng.choice(avail_choices))
        return c
    return f

MODES = {  # name: (secure, training availability choices, evaluated availability)
    "none": (False, None, [1.0]),
    "pqc_or_hybrid": (True, None, [1.0]),
    "qkd_only": (True, AVAIL, AVAIL),
}

def main(seeds=range(5), episodes=1000, eval_seeds=list(range(20))):
    runs = []
    env_kw = dict(n_segments=15, comm_aware=True)
    for mode, (secure, tr_av, ev_av) in MODES.items():
        for kind in ["QRL", "PPO"]:
            for s in seeds:
                actor = make_actor(kind, 5); t0 = time.time()
                train_ppo(actor, 5, env_kw, sampler(secure, tr_av), seed=s, episodes=episodes)
                ev = {}
                for sc in ["baseline", "medium", "disaster"]:
                    for a in ev_av:
                        cond = dict(STRESS[sc], secure=secure)
                        if a < 1.0: cond["qkd_avail"] = a
                        ev[f"{sc}_{a}"] = evaluate(actor, env_kw, cond, eval_seeds)
                runs.append(dict(mode=mode, kind=kind, seed=s, train_seconds=time.time()-t0, eval=ev))
                print(mode, kind, s, {k: round(v["accuracy"], 3) for k, v in ev.items() if k.startswith("medium")}, flush=True)
                (OUT / "security_modes.json").write_text(json.dumps(dict(avail=AVAIL, runs=runs)))

# Key-refresh cost, pinned to the paper's key-exchange/authentication table (Table 4: mean, both
# sides, measured on a four-core ARM64 Linux VM). experiments/crypto/bench_kex_auth.py measures
# the same quantities with the same methodology, but running it on a different machine gives
# different absolute numbers -- this repo has no ARM64 run of it, so these constants are the
# paper's published values, typed in directly, not read from that script's own output, so the
# sweep below matches what the paper reports.
# QuakeTwin's hybrid takes K_QKD from the QKD buffer and runs one ML-KEM-768 exchange per refresh
# (HKDF is negligible), so PQC-only and hybrid pay the same key-exchange cost. They differ in
# authentication: without QKD key material, PQC-only signs every refresh with ML-DSA; the hybrid
# signs the first round with ML-DSA and then uses a MAC keyed with QKD key material.
# A QKD key shortfall never blocks a message in either mode because ML-KEM is always available.
KEX = (0.1335, 2272)          # ms, bytes
MLDSA = (1.2033, 5261)        # signature + public key
MAC = (0.0078, 32)            # QKD-keyed MAC
LINK_KBPS = [1000, 100, 20]   # link rate during the refresh, swept as a controlled parameter


def refresh_ms(auth, kbps):
    return KEX[0] + auth[0] + (KEX[1] + auth[1]) * 8 / kbps   # bytes*8 / (kbit/s) = ms


HYBRID = {  # name: (auth in round 1, auth in later rounds)
    "pqc_only_mldsa_every_refresh": (MLDSA, MLDSA),
    "hybrid_mldsa_first_round": (MLDSA, MAC),
}


def hybrid_cond(name, kbps):
    first, later = HYBRID[name]
    return dict(refresh_ms=refresh_ms(later, kbps), first_refresh_ms=refresh_ms(first, kbps))


def hybrid_main(seeds=range(5), episodes=1000, eval_seeds=list(range(20))):
    runs = []
    env_kw = dict(n_segments=15, comm_aware=True)
    for name in HYBRID:
        base = sampler(True)
        train_sampler = lambda rng, base=base, name=name: dict(base(rng), **hybrid_cond(name, float(rng.choice(LINK_KBPS))))
        for kind in ["QRL", "PPO"]:
            for s in seeds:
                actor = make_actor(kind, 5); t0 = time.time()
                train_ppo(actor, 5, env_kw, train_sampler, seed=s, episodes=episodes)
                ev = {f"{sc}_{k}": evaluate(actor, env_kw, dict(STRESS[sc], secure=True, **hybrid_cond(name, k)), eval_seeds)
                      for sc in ["baseline", "medium", "disaster"] for k in LINK_KBPS}
                runs.append(dict(mode=name, kind=kind, seed=s, train_seconds=time.time() - t0, eval=ev))
                print(name, kind, s, {k: round(v["accuracy"], 3) for k, v in ev.items() if k.startswith("medium")}, flush=True)
                (OUT / "security_modes_hybrid.json").write_text(json.dumps(dict(link_kbps=LINK_KBPS, runs=runs)))


if __name__ == "__main__":
    if sys.argv[1:] == ["hybrid"]:
        hybrid_main()
    elif not sys.argv[1:]:
        main()
    else:
        sys.exit(f"usage: {sys.argv[0]} [hybrid]")
