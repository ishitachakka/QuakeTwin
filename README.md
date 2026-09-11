# QuakeTwin

[![OpenSSF Best Practices](https://www.bestpractices.dev/projects/12522/badge)](https://www.bestpractices.dev/projects/12522)

**QKD-Secured V2X Communication for Post-Disaster Transportation Digital Twins**

Live platform: https://quake-twin.vercel.app  
Backend API: https://quaketwin.onrender.com

---

## What This Is

Most Digital Twin systems for transportation assume communication works. After a hurricane, it doesn't — cellular towers go down, fiber links get cut, and the sensor data emergency responders depend on arrives late or not at all. Worse, physically damaged infrastructure becomes accessible to adversaries who can spoof sensor readings.

QuakeTwin is a Digital Twin platform built around that reality. It couples a QKD-secured V2X communication layer with a SeQUeNCe-inspired quantum network simulation to model what happens to infrastructure recovery decisions when communication degrades and comes under attack. The platform runs on real FDOT pavement data, Google Street View imagery, and Florida DOT traffic feeds.

Submitted to IEEE GLOBECOM 2026 — SAC: Quantum Communications and Information Technology.

---

## Key Results

Results below are taken directly from `clean/ai/experiment_results_v2.json` (the committed output of `qkd_sequence_simulation.py`, seed 42, 10 runs) — every number here is reproducible by re-running that script.

**QKD channel protection under MITM attack** (same QRL decision model, with vs. without QKD-protected transmission):

| Attack Rate | Without QKD | With QKD |
|---|---|---|
| 10% | 94.5% | 100.0% |
| 20% | 88.0% | 100.0% |
| 30% | 82.9% | 97.4% |

**Latency tolerance** (QRL vs. PPO decision models):

| Latency | QRL | PPO |
|---|---|---|
| 500ms | 100.0% | 100.0% |
| 750ms | 100.0% | 96.5% |
| 1000ms | 96.5% | 96.2% |

> **Note:** A previous version of this README (and the packet-loss/"disaster" figures quoted in early paper drafts — 82.7% vs. 67.5% at 40% packet loss, "15.2 percentage points") do **not** reproduce from this code. Re-running `packet_loss_sweep` shows no degradation at any loss level (both models stay at 100%), and the closest matching `combined_stress` scenario actually shows **PPO outperforming QRL** (54.8% vs. 75.9% at the "disaster" setting). Those numbers have been removed until there's a real, reproducible result to report.
>
> Also worth knowing if you're citing this repo: `QRLDecisionModel` and `PPODecisionModel` in `qkd_sequence_simulation.py` are **not** trained RL policies and don't run any quantum circuit — they're fixed formulas that map transmission fidelity to a classification accuracy, using different hand-picked constants for each model. Where one model "beats" the other in a given experiment, that reflects which constants happen to favor it under that scenario, not a demonstrated learning or quantum advantage.

---

## Repository Structure

```
QuakeTwin/
├── clean/
│   ├── api/
│   │   └── main.py                       # FastAPI backend
│   ├── ai/
│   │   └── qkd_sequence_simulation.py    # BB84/CV-QKD + SeQUeNCe experiments
│   ├── figures/                          # Experiment figures (300 DPI)
│   │   ├── fig1_latency_sweep.png
│   │   ├── fig2_attack_security.png
│   │   ├── fig3_lambda_sensitivity.png
│   │   └── fig4_combined_stress.png
│   └── web/
│       └── index.html                    # Frontend dashboard
├── experiment_results_v2.json            # Full output (6 experiments, 10 runs each)
├── requirements.txt
└── README.md
```

---

## Running Locally

### Backend

```bash
cd clean
pip install -r requirements.txt
python -m uvicorn api.main:app --reload --port 8000
```

API docs at `http://localhost:8000/docs`

### Frontend

```bash
cd clean/web
python -m http.server 8080
```

Open `http://localhost:8080`

### QKD Simulation

```bash
cd clean/ai
python3 qkd_sequence_simulation.py
```

Runs 6 experiments across 10 independent seeds: latency sweep, MITM attack security, lambda sensitivity, combined stress, packet loss degradation, and SeQUeNCe channel sensitivity. Results saved to `experiment_results_v2.json`.

### Environment Variables

Create a `.env` file in the root:

```
GOOGLE_MAPS_API_KEY=your_key
```

## Quantum Network Simulation Setup

The communication layer is implemented in `clean/ai/qkd_sequence_simulation.py`
— a self-contained, SeQUeNCe-inspired discrete-event simulation of a
QKD-secured sensor-to-backend channel. It does not link against the
external `sequence` PyPI package or build an explicit multi-node router
graph; instead it models channel conditions and the BB84 protocol
directly in Python (no extra install beyond `requirements.txt`).

### Core Components

- **`NetworkCondition`** — one-way latency, packet loss rate, jitter,
  and bandwidth for a given channel state.
- **`BB84Protocol`** — simplified BB84 key exchange: Alice/Bob/Eve bases,
  basis sifting, QBER estimation on a test subset, and a Shor-Preskill
  secure-key-rate calculation.
- **`QKDChannel`** — combines a `NetworkCondition` with `BB84Protocol`,
  refreshing the shared key every 50 transmissions and modeling MITM
  tamper success/failure based on measured QBER.
- **`QRLDecisionModel`** / **`PPODecisionModel`** — decision-quality
  proxies that convert transmission fidelity into classification
  accuracy, confidence, global efficiency, and local safety scores.

### Key Parameters (as implemented)

| Parameter | Value | Where |
|---|---|---|
| BB84 raw key length | 256 bits | `BB84Protocol.raw_key_length` |
| QBER security threshold | 0.11 (Shor-Preskill bound) | `BB84Protocol.SECURITY_THRESHOLD_QBER` |
| Key refresh interval | every 50 transmissions | `QKDChannel._key_refresh_interval` |
| Sensor readings per run | 200 | `n_readings` in `run_experiments()` |
| Independent seeded runs per config | 10 | `n_runs` in `run_experiments()` |
| Global seed | 42 | `np.random.seed(42)` / `random.seed(42)` |
| Confidence intervals | 95%, t-distribution across the 10 runs | `confidence_interval_95()` |

### Run the Full Simulation

```bash
cd clean/ai
python3 qkd_sequence_simulation.py
```

This calls `run_experiments(n_readings=200, n_runs=10)`, which runs six
experiments, each swept across the 10 seeded runs above:

1. **Latency sweep** — 10–1000ms, QRL vs. PPO accuracy
2. **Packet loss sweep** — 0–50% loss, QRL vs. PPO accuracy
3. **MITM security experiment** — 0–100% attack rate, QKD vs. no-QKD
   accuracy and tamper rate
4. **Combined stress test** — five scenarios (baseline → disaster)
   mixing latency, packet loss, and attack rate
5. **PPO lambda sweep** — GAE λ ∈ {0.1, 0.5, 1.0, 2.0} across three
   network conditions (clean/degraded/attacked), vs. QRL
6. **SeQUeNCe sensitivity** — packet loss sweep vs. the QRL/PPO
   accuracy and safety gap

Results (mean, std, 95% CI per configuration) are saved to
`experiment_results_v2.json`, plus a timestamped copy.

### QKD Protocol Details

- **Protocol:** BB84, simulated end-to-end (basis generation, sifting,
  QBER estimation, intercept-resend eavesdropping model)
- **QBER monitoring:** per-key-block — a channel is flagged insecure
  when QBER ≥ 11% (Shor-Preskill bound)
- **Fallback:** when the channel is insecure or a packet is dropped,
  the decision model falls back to a lower-confidence classification
  rather than trusting the reading
- **Key outputs:** per-transmission latency, delivery/tamper rates,
  and downstream QRL/PPO decision accuracy, confidence, global
  efficiency, and local safety

---

## System Overview

**Physical Layer** — Road IoT sensors, V2X vehicles, and a pavement CV pipeline feed real-time observations into the system.

**Communication Layer** — The primary contribution. BB84/CV-QKD-secured channels model configurable latency τ(t) and packet loss ρ(t) (see [Quantum Network Simulation Setup](#quantum-network-simulation-setup) for the implementation actually in this repo). QBER is monitored continuously — when it exceeds the 11% Shor-Preskill threshold, the channel is flagged as compromised and the system falls back to cached Digital Twin state rather than acting on potentially spoofed data.

**Digital Twin Layer** — Road network modeled as a directed graph G=(V,E) with per-edge PCI state, traversability, V2X latency, and packet delivery ratio. Damage propagation is modeled explicitly through time-varying edge state tuples.

**Intelligence Layer** — Three QRL architectures (A3C, Sequential_QAC, Diagnostic_QAC) evaluated against a classical PPO baseline. Policy implemented as a 2-qubit, 2-layer parameterized quantum circuit via PennyLane.

**Decision Layer** — Adaptive strategy selection among wait, routine maintenance, and full reconstruction based on real-time hazard severity, communication reliability, and budget state.

---

## SeQUeNCe Simulation Parameters (Companion VTC Paper)

> **Note:** This table describes the larger-scale SeQUeNCe topology used
> in our companion IEEE VTC submission, not the simulation shipped in
> this repo. `clean/ai/qkd_sequence_simulation.py` does not build a
> multi-router topology or call the `sequence` package — see
> [Quantum Network Simulation Setup](#quantum-network-simulation-setup)
> above for what's actually implemented here.

| Parameter | Value |
|---|---|
| Topology | 101-router star network |
| Channel attenuation | 10⁻⁵ to 10⁻² dB/m |
| Memory efficiency | 0.9 |
| Coherence time | 0.5s |
| Fidelity threshold | 0.85–0.95 |
| Detector efficiency | 0.8 |

The 101-router star topology approximates hub-and-spoke disaster response coordination — centralized emergency management interacting with distributed vehicle and sensor nodes across a damaged road network.

---

## Security

QuakeTwin has undergone STRIDE-based threat modeling 
covering five trust zones from untrusted edge sensors 
to QRL model inputs. Key findings:

- Critical API endpoints identified for authentication 
  hardening (JWT + API keys on all POST routes)
- BB84 QKD existing as primary MITM mitigation 
  (QBER threshold 11%)
- Fusion consensus (2-of-3 source agreement) proposed 
  for Sybil attack resilience
- Immutable audit log proposed for replay attack detection

See `/security/threat_model.png` for the full 
STRIDE diagram.

---

## Expected Results Under Attack Scenarios

Based on STRIDE threat modeling and the QKD channel simulation above:

| Attack Scenario | Without QKD | With QKD |
|---|---|---|
| Active MITM (20% rate) | 88% accuracy | 100% accuracy |
| Replay attack | Stale DT state | Detected via QBER |
| DoS on RSU channel | Communication blackout | Fallback to cached DT state |

The MITM row is verified against `experiment_results_v2.json` (see [Key Results](#key-results)). The replay-attack and DoS rows describe intended design behavior rather than a benchmarked metric — there's no dedicated replay or DoS experiment in `qkd_sequence_simulation.py` yet.

QKD QBER threshold: 11% (Shor-Preskill bound)  
When exceeded: automatic fallback to cached DT state

---

## Tech Stack

| Component | Technology |
|---|---|
| Frontend | HTML/CSS/JS, Google Maps API — Vercel |
| Backend | Python 3.11, FastAPI — Render |
| QKD/Simulation | SeQUeNCe, BB84/CV-QKD protocol |
| QRL | PennyLane, PyTorch |
| Data | FDOT pavement data, RescueNet, FL DOT 511 API |

---

## Authors

Ishita Chakkalakkal, Gabriella Vallar, Brenton Stevenson, Sean Peppers, Jieyi Bao, Chengyi Qu  
Florida Gulf Coast University

---

## License

MIT
