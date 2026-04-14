# QuakeTwin

[![OpenSSF Best Practices](https://www.bestpractices.dev/projects/12522/badge)](https://www.bestpractices.dev/projects/12522)

**QKD-Secured V2X Communication for Post-Disaster Transportation Digital Twins**

Live platform: https://quake-twin.vercel.app  
Backend API: https://quaketwin-production.up.railway.app

---

## What This Is

Most Digital Twin systems for transportation assume communication works. After a hurricane, it doesn't — cellular towers go down, fiber links get cut, and the sensor data emergency responders depend on arrives late or not at all. Worse, physically damaged infrastructure becomes accessible to adversaries who can spoof sensor readings.

QuakeTwin is a Digital Twin platform built around that reality. It couples a QKD-secured V2X communication layer with SeQUeNCe-based quantum network simulation to model what happens to infrastructure recovery decisions when communication degrades and comes under attack. The platform runs on real FDOT pavement data, Google Street View imagery, and Florida DOT traffic feeds.

Submitted to IEEE GLOBECOM 2026 — SAC: Quantum Communications and Information Technology.

---

## Key Results

QKD-secured channels maintain **15.2 percentage points** higher decision accuracy than unprotected classical channels under disaster conditions (40% packet loss):

| Scenario | Packet Loss | QRL + QKD | PPO Unprotected |
|---|---|---|---|
| Nominal | 0% | 100.0% | 100.0% |
| Storm Damage | 10% | 97.2% | 94.1% |
| Severe Disruption | 25% | 91.4% | 82.3% |
| Disaster | 40% | 82.7% | 67.5% |

QRL+QKD holds near-perfect accuracy up to 20% MITM attack rate. Unprotected PPO degrades immediately from 10%.

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

---

## System Overview

**Physical Layer** — Road IoT sensors, V2X vehicles, and a pavement CV pipeline feed real-time observations into the system.

**Communication Layer** — The primary contribution. BB84/CV-QKD-secured channels are simulated via SeQUeNCe with configurable latency τ(t) and packet loss ρ(t). QBER is monitored continuously — when it exceeds the 11% Shor-Preskill threshold, the channel is flagged as compromised and the system falls back to cached Digital Twin state rather than acting on potentially spoofed data.

**Digital Twin Layer** — Road network modeled as a directed graph G=(V,E) with per-edge PCI state, traversability, V2X latency, and packet delivery ratio. Damage propagation is modeled explicitly through time-varying edge state tuples.

**Intelligence Layer** — Three QRL architectures (A3C, Sequential_QAC, Diagnostic_QAC) evaluated against a classical PPO baseline. Policy implemented as a 2-qubit, 2-layer parameterized quantum circuit via PennyLane.

**Decision Layer** — Adaptive strategy selection among wait, routine maintenance, and full reconstruction based on real-time hazard severity, communication reliability, and budget state.

---

## SeQUeNCe Simulation Parameters

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

## Tech Stack

| Component | Technology |
|---|---|
| Frontend | HTML/CSS/JS, Google Maps API — Vercel |
| Backend | Python 3.11, FastAPI — Railway |
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
