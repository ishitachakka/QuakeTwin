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

if __name__ == "__main__":
    main()
