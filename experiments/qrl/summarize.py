"""Turn results/*.json into summary tables (mean +/- 95% CI over seeds) and figures."""
from __future__ import annotations

import json
from pathlib import Path

import numpy as np
import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

R = Path(__file__).parent / "results"


def ci(xs):
    xs = np.asarray(xs, dtype=float)
    if len(xs) < 2:
        return float(xs.mean()), 0.0
    from scipy import stats
    h = stats.t.ppf(0.975, len(xs) - 1) * xs.std(ddof=1) / np.sqrt(len(xs))
    return float(xs.mean()), float(h)


def fmt(m, h, pct=True):
    return f"{100*m:.1f} ± {100*h:.1f}" if pct else f"{m:.2f} ± {h:.2f}"


def ablation():
    d = json.loads((R / "ablation.json").read_text())
    runs = d["runs"]
    kinds = ["QRL", "PPO-small", "PPO"]
    settings = ["no_comm_dt", "comm_aware", "comm_aware_secure"]
    lines = ["# Ablation (decision accuracy %, mean ± 95% CI over seeds)\n"]
    summary = {}
    for scen in ["baseline", "low", "medium", "high", "disaster"]:
        lines.append(f"\n## stress = {scen}\n\n| setting | " + " | ".join(kinds) + " |\n|---|---|---|---|")
        for s in settings:
            row = [s]
            for k in kinds:
                xs = [r["eval"]["stress"][scen]["accuracy"] for r in runs if r["kind"] == k and r["setting"] == s]
                if not xs:
                    row.append("-"); continue
                m, h = ci(xs); row.append(fmt(m, h) + f" (n={len(xs)})")
                summary[(scen, s, k)] = (m, h)
            lines.append("| " + " | ".join(row) + " |")
    for sweep, key, label in [("packet_loss", "packet_loss", "packet loss"), ("attack", "attack_rate", "MITM attack rate"),
                              ("latency", "latency_ms", "latency (ms)")]:
        lines.append(f"\n## {label} sweep, setting = comm_aware_secure vs no_comm_dt\n")
        lines.append("| config | " + " | ".join(str(i) for i in range(len(runs[0]["eval"][sweep]))) + " |")
        for s in ["no_comm_dt", "comm_aware_secure"]:
            for k in kinds:
                sel = [r for r in runs if r["kind"] == k and r["setting"] == s]
                if not sel:
                    continue
                cells = []
                for i in range(len(sel[0]["eval"][sweep])):
                    m, h = ci([r["eval"][sweep][i]["accuracy"] for r in sel]); cells.append(fmt(m, h))
                lines.append(f"| {s} / {k} | " + " | ".join(cells) + " |")
    params = {k: next(r["params"] for r in runs if r["kind"] == k) for k in kinds if any(r["kind"] == k for r in runs)}
    lines.append(f"\nActor parameter counts: {params}\n")
    (R / "ablation_summary.md").write_text("\n".join(lines))

    # figure: stress scenarios, three settings, three agents
    scen = ["baseline", "low", "medium", "high", "disaster"]
    fig, axes = plt.subplots(1, 3, figsize=(12, 3.4), sharey=True)
    for ax, s in zip(axes, settings):
        for k, mk in zip(kinds, ["o", "s", "^"]):
            ms = [summary.get((c, s, k), (np.nan, 0)) for c in scen]
            ax.errorbar(range(5), [m for m, _ in ms], yerr=[h for _, h in ms], marker=mk, capsize=3, label=k)
        ax.set_xticks(range(5)); ax.set_xticklabels(scen, rotation=20)
        ax.set_title(s.replace("_", " ")); ax.grid(alpha=.3)
    axes[0].set_ylabel("decision accuracy"); axes[0].legend()
    fig.suptitle("Combined stress: trained QRL vs PPO under three communication settings (mean ± 95% CI)")
    fig.tight_layout(); fig.savefig(R / "ablation_stress.png", dpi=300)

    # learning curves (comm_aware_secure)
    fig, ax = plt.subplots(figsize=(5, 3.2))
    for k in kinds:
        sel = [np.array([c[0] for c in r["curve"]]) for r in runs if r["kind"] == k and r["setting"] == "comm_aware_secure"]
        if not sel:
            continue
        L = min(len(x) for x in sel); A = np.stack([x[:L] for x in sel])
        sm = np.convolve(A.mean(0), np.ones(25) / 25, mode="valid")
        ax.plot(sm, label=k)
    ax.set_xlabel("episode"); ax.set_ylabel("training return (25-ep avg)"); ax.grid(alpha=.3); ax.legend()
    fig.tight_layout(); fig.savefig(R / "learning_curves.png", dpi=300)


def qubits():
    d = json.loads((R / "qubits.json").read_text())
    runs = d["runs"]
    lines = ["# Qubit / depth sweep (comm_aware_secure), accuracy % mean ± 95% CI\n",
             "| qubits | layers | params (circuit / total) | baseline | medium | disaster | train s |", "|---|---|---|---|---|---|---|"]
    for nq in [2, 4, 6]:
        for nl in [1, 2, 3]:
            sel = [r for r in runs if r["n_qubits"] == nq and r["n_layers"] == nl]
            if not sel:
                continue
            cells = []
            for sc in ["baseline", "medium", "disaster"]:
                m, h = ci([r["eval"]["stress"][sc]["accuracy"] for r in sel]); cells.append(fmt(m, h))
            p = sel[0]["params"]; ts = np.mean([r["train_seconds"] for r in sel])
            lines.append(f"| {nq} | {nl} | {p['circuit']} / {p['total']} | " + " | ".join(cells) + f" | {ts:.0f} |")
    (R / "qubits_summary.md").write_text("\n".join(lines))


if __name__ == "__main__":
    for f in (ablation, qubits):
        try:
            f(); print("ok", f.__name__)
        except FileNotFoundError:
            print("missing results for", f.__name__)
