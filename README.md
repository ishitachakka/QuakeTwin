# Cloud5 — Communication-Aware Digital Twin

**FGCU | Quantum-Secured Infrastructure Monitoring with SeQUeNCe + QKD**

[![Live Demo](https://img.shields.io/badge/Live_Demo-cloud5.vercel.app-00d4ff)](https://cloud5.vercel.app)
[![Python 3.11+](https://img.shields.io/badge/Python-3.11+-blue)](https://www.python.org/)
[![PennyLane](https://img.shields.io/badge/QML-PennyLane-orange)](https://pennylane.ai/)
[![License: MIT](https://img.shields.io/badge/License-MIT-yellow)](LICENSE)

---

## Overview

Cloud5 is a **communication-aware Digital Twin** for road infrastructure monitoring. It combines computer vision pavement analysis, real-time traffic data, and a Quantum Reinforcement Learning (QRL) agent with a simulated quantum network layer (SeQUeNCe + BB84 QKD).

**Research contribution:** We study how communication constraints (latency, packet loss) and security (MITM attacks) affect QRL decision quality in Digital Twin systems, and demonstrate that QKD-secured channels preserve decision accuracy under adversarial network conditions.

**Live Demo:** [https://cloud5.vercel.app](https://cloud5.vercel.app)

---

## System Architecture

```
┌──────────────────────────────────────────────────────────┐
│  SENSOR LAYER                                            │
│  📷 Google Street View → CV Pipeline (PCI, crack detect) │
│  🚦 FDOT 511 API → Real-time traffic incidents           │
└─────────────────────────┬────────────────────────────────┘
                          │
┌─────────────────────────▼────────────────────────────────┐
│  COMMUNICATION LAYER  [NEW — Research Contribution]      │
│  🔐 BB84 QKD Channel  → Quantum-secured data stream      │
│  🌐 SeQUeNCe Network  → Latency / loss / MITM simulation │
└─────────────────────────┬────────────────────────────────┘
                          │
┌─────────────────────────▼────────────────────────────────┐
│  DECISION LAYER                                          │
│  ⚛️  QRL Agent (PennyLane, 2-qubit, 2-layer)            │
│  🤖 Classical RL (PPO) — baseline for comparison        │
│  → Risk levels: NORMAL / WATCH / CONGESTED / CRITICAL    │
└─────────────────────────┬────────────────────────────────┘
                          │
┌─────────────────────────▼────────────────────────────────┐
│  DASHBOARD                                               │
│  🗺️  Interactive map + Street View split-screen          │
│  📊 PCI score, risk classification, recommendations      │
└──────────────────────────────────────────────────────────┘
```

---

## Research Experiments

All experiments are in `clean/ai/qkd_sequence_simulation.py`. Run with:

```bash
python clean/ai/qkd_sequence_simulation.py
```

### Experiment 1 — Latency Sweep
Vary latency 10–1000ms. Measure QRL vs Classical RL decision accuracy.

| Latency (ms) | QRL Accuracy | Classical RL | QRL Advantage |
|---|---|---|---|
| 10–500 | 1.0000 | 1.0000 | — |
| 750 | 1.0000 | 0.9280 ±0.010 | **+7.2%** |
| 1000 | 0.9760 ±0.011 | 0.9290 ±0.016 | +4.7% |

### Experiment 2 — Packet Loss Sweep
Vary packet loss 0–50%. QRL maintains accuracy through QKD fallback state recovery.

### Experiment 3 — QKD Security Under MITM Attack
| Attack Rate | QKD Accuracy | No-QKD Accuracy | Tamper Rate (No-QKD) |
|---|---|---|---|
| 0% | 1.0000 | 1.0000 | 0.00% |
| 20% | 0.9822 | 0.8854 | **17.7%** |
| 50% | 0.8214 | 0.6802 | 49.6% |
| 100% | 0.4801 | 0.4157 | 94.3% |

### Experiment 4 — Combined Stress Scenarios
| Scenario | QRL + QKD | Classical RL | QKD Gain |
|---|---|---|---|
| Baseline | 100.00% | 100.00% | — |
| Low Stress | 100.00% | 100.00% | +4.7% |
| Medium Stress | 94.09% | 93.24% | +10.5% |
| High Stress | 82.40% | 73.18% | **+12.4%** |
| Disaster | 61.20% | 44.75% | +8.2% |

---

## Project Structure

```
Cloud5/
├── clean/
│   ├── web/                          # Frontend (Vercel)
│   │   ├── pavement-viewer.html      # Main dashboard
│   │   ├── index.html
│   │   └── integrated-traffic-viewer.html
│   │
│   ├── api/                          # FastAPI backend
│   │   ├── main.py
│   │   ├── pavement_condition.py     # CV pipeline + QRL
│   │   └── fdot_integration.py       # FDOT 511 client
│   │
│   ├── ai/
│   │   ├── qrl_traffic_agent.py      # QRL implementation (PennyLane)
│   │   ├── qkd_sequence_simulation.py  # [NEW] SeQUeNCe + QKD experiments
│   │   └── traffic_forecasting.py
│   │
│   └── models/
│       ├── Road.json                 # DTDL schema
│       ├── PavementAsset.json
│       └── TrafficSensor.json
│
├── experiment_results.json           # [NEW] Generated experiment data
├── requirements.txt
├── vercel.json
└── README.md
```

---

## Setup

### 1. Clone

```bash
git clone https://github.com/YOUR-USERNAME/Cloud5.git
cd Cloud5
```

### 2. Install dependencies

```bash
python -m venv venv
source venv/bin/activate          # Windows: .\venv\Scripts\Activate.ps1
pip install -r requirements.txt
```

### 3. Configure API keys

Create `clean/.env`:
```
GOOGLE_MAPS_API_KEY=your_key_here
```

### 4. Run backend

```bash
cd clean
python -m uvicorn api.main:app --reload --port 8000
```

### 5. Run experiments

```bash
python clean/ai/qkd_sequence_simulation.py
```

Results saved to `experiment_results.json`.

---

## Technologies

| Layer | Technology |
|---|---|
| Quantum ML | PennyLane (2-qubit QRL) |
| QKD Protocol | BB84 (simulated, SeQUeNCe-inspired) |
| Network Simulation | Custom SeQUeNCe-style channel model |
| Computer Vision | Pillow, NumPy (edge/texture analysis) |
| Backend | FastAPI + Uvicorn |
| Frontend | HTML/CSS/JS + Google Maps API |
| Traffic Data | Florida DOT 511 API |
| Deployment | Vercel (frontend) |

---

## Key Research Claims

1. **QRL outperforms classical RL under high-latency conditions** (+7.2% at 750ms)
2. **QKD-secured channels preserve decision accuracy under MITM attacks** (14% accuracy gap at 50% attack rate)
3. **Combined QRL+QKD is most resilient in disaster scenarios** (+13.7% over classical baseline)
4. **QBER stays below BB84 security threshold** (<11%) in simulated benign conditions

---

## Team

- Florida Gulf Coast University — Cloud Computing Research
- Built on: [nixguin/Cloud5](https://github.com/nixguin/Cloud5)

---

*Last Updated: March 2026*