"""
QuakeTwin experiments with TRAINED policies.

  python run_experiments.py ablation   # R1 7.2 / R2-2: QRL vs PPO x comm setting
  python run_experiments.py qubits     # R1 6.2 / R2-6: qubits x layers sweep
  python run_experiments.py smoke      # 1-minute check that everything runs

Results go to results/<mode>.json with per-seed values, so every number in
the paper can be traced back to a file.
"""
from __future__ import annotations

import json
import sys
import time
from pathlib import Path

import numpy as np
import torch

from qt_agents import MLPActor, QRLActor, evaluate, train_ppo

torch.set_num_threads(1)
OUT = Path(__file__).parent / "results"
OUT.mkdir(exist_ok=True)

# Training covers a range of degradation so one policy is evaluated everywhere.
LOSS = [0.0, 0.1, 0.25, 0.4]
ATTACK = [0.0, 0.1, 0.2, 0.3]
LATENCY = [0.0, 250.0, 500.0, 1000.0]

COMM_SETTINGS = {
    # name: (comm_aware observation, security layer)
    "no_comm_dt": (False, False),
    "comm_aware": (True, False),
    "comm_aware_secure": (True, True),
}

# Evaluation conditions
PACKET_LOSS_SWEEP = [dict(packet_loss=p, attack_rate=0.0, latency_ms=0.0) for p in [0.0, 0.1, 0.25, 0.4]]
ATTACK_SWEEP = [dict(packet_loss=0.0, attack_rate=a, latency_ms=0.0) for a in [0.0, 0.1, 0.2, 0.3, 0.5]]
LATENCY_SWEEP = [dict(packet_loss=0.0, attack_rate=0.0, latency_ms=l) for l in [0.0, 250.0, 500.0, 750.0, 1000.0]]
STRESS = {  # same scenario definitions as the manuscript's combined-stress figure
    "baseline": dict(latency_ms=10.0, packet_loss=0.0, attack_rate=0.0),
    "low": dict(latency_ms=100.0, packet_loss=0.05, attack_rate=0.1),
    "medium": dict(latency_ms=300.0, packet_loss=0.15, attack_rate=0.3),
    "high": dict(latency_ms=600.0, packet_loss=0.25, attack_rate=0.5),
    "disaster": dict(latency_ms=1000.0, packet_loss=0.4, attack_rate=0.8),
}


def sampler(secure):
    def f(rng):
        return dict(packet_loss=float(rng.choice(LOSS)), attack_rate=float(rng.choice(ATTACK)),
                    latency_ms=float(rng.choice(LATENCY)), secure=secure)
    return f


def make_actor(kind, obs_dim, n_qubits=2, n_layers=2):
    if kind == "QRL":
        return QRLActor(obs_dim, n_qubits, n_layers)
    if kind == "PPO-small":
        return MLPActor(obs_dim, hidden=4)
    if kind == "PPO":
        return MLPActor(obs_dim, hidden=64)
    raise ValueError(kind)


def run_one(kind, setting, seed, episodes, eval_seeds, n_qubits=2, n_layers=2, full_eval=True):
    aware, secure = COMM_SETTINGS[setting]
    env_kw = dict(n_segments=15, comm_aware=aware)
    obs_dim = 5 if aware else 3
    actor = make_actor(kind, obs_dim, n_qubits, n_layers)
    t0 = time.time()
    curve = train_ppo(actor, obs_dim, env_kw, sampler(secure), seed=seed, episodes=episodes)
    train_s = time.time() - t0
    ev = {}
    if full_eval:
        ev["packet_loss"] = [evaluate(actor, env_kw, dict(c, secure=secure), eval_seeds) for c in PACKET_LOSS_SWEEP]
        ev["attack"] = [evaluate(actor, env_kw, dict(c, secure=secure), eval_seeds) for c in ATTACK_SWEEP]
        ev["latency"] = [evaluate(actor, env_kw, dict(c, secure=secure), eval_seeds) for c in LATENCY_SWEEP]
    ev["stress"] = {k: evaluate(actor, env_kw, dict(c, secure=secure), eval_seeds) for k, c in STRESS.items()}
    return dict(kind=kind, setting=setting, seed=seed, n_qubits=n_qubits, n_layers=n_layers,
                params=actor.param_report(), train_seconds=train_s, curve=curve, eval=ev)


def save(name, runs, meta):
    (OUT / f"{name}.json").write_text(json.dumps(dict(meta=meta, runs=runs)))


def main(mode):
    eval_seeds = list(range(20))
    if mode == "smoke":
        r = run_one("QRL", "comm_aware_secure", 0, 16, eval_seeds[:2], full_eval=False)
        print("smoke ok", r["params"], r["eval"]["stress"]["medium"])
        return
    if mode == "ablation":
        seeds, episodes = list(range(10)), 1000
        runs = []
        meta = dict(seeds=seeds, episodes=episodes, eval_seeds=eval_seeds, n_segments=15,
                    train_conditions=dict(loss=LOSS, attack=ATTACK, latency=LATENCY))
        for setting in COMM_SETTINGS:
            for kind in ["QRL", "PPO-small", "PPO"]:
                for s in seeds:
                    r = run_one(kind, setting, s, episodes, eval_seeds)
                    runs.append(r)
                    print(f"{setting:18s} {kind:9s} seed={s} stress-medium acc="
                          f"{r['eval']['stress']['medium']['accuracy']:.3f} ({r['train_seconds']:.0f}s)", flush=True)
                    save("ablation", runs, meta)
    if mode == "qubits":
        seeds, episodes = list(range(5)), 1000
        runs = []
        meta = dict(seeds=seeds, episodes=episodes, eval_seeds=eval_seeds, setting="comm_aware_secure")
        for nq in [2, 4, 6]:
            for nl in [1, 2, 3]:
                for s in seeds:
                    r = run_one("QRL", "comm_aware_secure", s, episodes, eval_seeds, nq, nl, full_eval=False)
                    runs.append(r)
                    print(f"qubits={nq} layers={nl} seed={s} medium acc="
                          f"{r['eval']['stress']['medium']['accuracy']:.3f} params={r['params']['total']} "
                          f"({r['train_seconds']:.0f}s)", flush=True)
                    save("qubits", runs, meta)


if __name__ == "__main__":
    main(sys.argv[1] if len(sys.argv) > 1 else "smoke")
