# QuakeTwin: trained QRL vs. PPO experiments

This folder contains the trained-policy experiments for the OJVT revision.
Unlike `clean/ai/qkd_sequence_simulation.py`, whose `QRLDecisionModel` and
`PPODecisionModel` are fixed formulas, every agent here is **trained with PPO**
and evaluated greedily on held-out seeds.

## Files

| File | What it is |
|---|---|
| `qt_env.py` | Post-hurricane recovery environment (15 road segments by default, random or spatially concentrated damage) and the communication channel (packet loss, latency, MITM, BB84 QBER check). |
| `qt_agents.py` | `QRLActor` (PennyLane circuit), `MLPActor` (classical baseline), shared critic, PPO training, evaluation. |
| `run_experiments.py` | `ablation` (R1 7.2 / R2-2), `qubits` (R1 6.2 / R2-6), `smoke`. |
| `summarize.py` | Builds `results/*_summary.md` tables (mean ± 95% CI) and figures. |

## The QRL actor (for Table II)

| Stage | Detail |
|---|---|
| Input | Per-segment features from the DT: observed condition, hazard, traffic importance, and (comm-aware only) report age and verification flag. 5 features, or 3 without the Communication DT. One shared policy decides for every segment at every step. |
| Preprocessing | Linear layer (trainable) maps the features to one angle per qubit; `angle = π·tanh(Wx+b)`. |
| Data encoding | `RY(angle_q)` on qubit q. Encoding angles are computed from the input, not trained directly. |
| Variational layer (×L) | Trainable `RX(θ)`, `RY(φ)` on every qubit, then a CNOT chain (0→1, 1→2, …). |
| Measurement | ⟨Z⟩ on every qubit. |
| Action mapping | Linear head (trainable) → softmax over {wait, routine repair, full reconstruction}. |
| Default size | 2 qubits, 2 layers: 8 circuit + 12 encoder + 9 head = 29 trainable parameters (comm-aware input). |
| Simulator | PennyLane `default.qubit`, exact expectation values, no hardware noise. |

Baselines: `PPO-small` is an MLP with 4 hidden units (about the same parameter count as the QRL actor);
`PPO` is an MLP with 64 hidden units. All three use the same critic, PPO update (γ=0.99, GAE λ=0.95,
clip 0.2, 4 epochs, minibatch 512, 8 parallel episodes per update), 1,000 training episodes of 12 steps,
and 15 road segments.

## Communication settings in the ablation

| Setting | Observation | Security layer |
|---|---|---|
| `no_comm_dt` | condition, hazard, importance only | off: tampered reports are accepted |
| `comm_aware` | + report age + verification flag | off |
| `comm_aware_secure` | + report age + verification flag | on: attacked reports detected by the BB84 QBER check (>11% on 64 test bits) are discarded and the DT keeps the last verified value |

Training draws packet loss, attack rate and latency per episode from {0, .1, .25, .4},
{0, .1, .2, .3} and {0, 250, 500, 1000} ms. Evaluation uses fixed conditions, including the
manuscript's five combined-stress scenarios.

## Modeling limits (state these in the paper)

* The security layer abstracts QKD detection as a QBER test; authenticated encryption from PQC-derived keys
  would reject tampered packets too. The QKD-only / PQC-only / hybrid comparison (R1 5.1) is not modeled here.
* Decision accuracy is the share of all (segment, step) decisions that match a severity rule applied to the
  **true** condition: full reconstruction below 0.4, routine repair below 0.7, otherwise wait. Every segment is
  scored at every step, so corrupted data changes what the agent sees, never which decisions are scored.
* Environment dynamics: hazard-driven decay plus random new damage (5% per segment per step).
* Simulation only. No physical quantum hardware or field deployment.

## Reproduce

```bash
pip install torch pennylane numpy scipy matplotlib
python run_experiments.py ablation
python run_experiments.py qubits
python summarize.py
```
