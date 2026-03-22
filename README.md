# 🌍 QuakeTwin  
### Communication-Aware Digital Twin for Disaster-Resilient Infrastructure Systems  

🚀 **Live Demo (Frontend):** https://quake-twin.vercel.app/

---

## 🧠 Overview

**QuakeTwin** is a communication-aware Digital Twin platform designed for **post-disaster infrastructure monitoring and decision-making**.

The system integrates:

- 🌍 **Digital Twin modeling of transportation infrastructure**
- ⚛️ **Quantum Reinforcement Learning (QRL)** for risk-aware decision making
- 📡 **Communication-aware simulation (SeQUeNCe – in progress)**
- 🔐 **Quantum Key Distribution (QKD) concepts for secure data exchange**
- 🛣️ **Computer Vision for pavement condition analysis**
- 🚦 **Real-time traffic data integration (Florida DOT 511 API)**

---

## 🎯 Research Motivation

Traditional Digital Twin systems assume:

❌ Perfect communication  
❌ Reliable infrastructure  
❌ Secure data transfer  

However, in **post-disaster environments**, these assumptions break down.

QuakeTwin addresses this gap by introducing:

> **Communication-aware + security-aware Digital Twin modeling**

---

## 🔬 Research Contributions (In Progress)

This project explores:

### 1. Communication-Aware Digital Twins
- Modeling network conditions (latency, packet loss, node failure)
- Evaluating impact on decision-making

### 2. Quantum Reinforcement Learning (QRL)
- Risk classification using parameterized quantum circuits
- Adaptive decision policies under uncertainty

### 3. Secure Communication via QKD (Conceptual Integration)
- Secure key exchange mechanisms
- Detection of adversarial interference

### 4. Integration with SeQUeNCe (Planned)
- Discrete-event simulation of quantum networks
- Modeling communication constraints in disaster scenarios

---

## 🏗️ System Architecture

```

Sensors / Data Sources
↓
Computer Vision + Traffic APIs
↓
(QKD-Secured Communication Layer – Conceptual)
↓
Network Simulation (SeQUeNCe – In Progress)
↓
Quantum Reinforcement Learning (QRL)
↓
Digital Twin State Update
↓
Web Dashboard Visualization

```

---

## ⚙️ Core Features

### 🛣️ Pavement Condition Analysis
- Google Street View image ingestion
- Crack detection (edge-based)
- Texture + brightness analysis
- PCI (Pavement Condition Index) scoring

---

### 🚦 Real-Time Traffic Monitoring
- Florida DOT 511 API integration
- Incident detection (accidents, closures, construction)
- Geographic filtering (15-mile radius)

---

### ⚛️ QRL-Based Risk Classification
- 2-qubit quantum circuit model
- Risk levels:
  - 🟢 NORMAL
  - 🟡 WATCH
  - 🟠 CONGESTED
  - 🔴 CRITICAL
- Confidence scoring + adaptive learning

---

### 🗺️ Interactive Dashboard
- Split-screen view (Map + Street View)
- Click-to-analyze infrastructure
- Real-time overlays
- Mobile responsive UI

---

## 🔐 Communication & Security Layer (Research Focus)

QuakeTwin is being extended to include:

### 📡 Network Modeling
- Latency simulation
- Packet loss modeling
- Node failure scenarios

### 🔐 Security Modeling
- Spoofed sensor data attacks
- Communication interception
- Denial-of-service scenarios

### ⚛️ Quantum Security (QKD – Conceptual)
- Secure key distribution
- Eavesdropping detection
- Trusted communication channels

---

## 📊 Research Goals

- Evaluate how communication degradation impacts:
  - decision accuracy
  - response time
  - system reliability  

- Compare:
  - QRL vs classical RL (planned)
  - secure vs insecure communication

---

## 📁 Project Structure

```

clean/
├── api/                # Backend (FastAPI)
├── ai/                 # QRL and ML models
├── models/             # Infrastructure schemas
├── web/                # Frontend dashboard

````

---

## 🚀 Running the Project

### 1. Clone Repository
```bash
git clone https://github.com/ishitachakka/QuakeTwin.git
cd QuakeTwin
````

---

### 2. Setup Environment

```bash
python3 -m venv venv
source venv/bin/activate
```

---

### 3. Install Dependencies

```bash
cd clean
pip install -r requirements-backend-only.txt
```

---

### 4. Configure API Keys

Create `.env`:

```
GOOGLE_MAPS_API_KEY=your_key
```

---

### 5. Run Backend

```bash
python -m uvicorn api.main:app --reload --port 8000
```

---

### 6. Run Frontend

```bash
cd web
python -m http.server 8080
```

---

### 7. Access

* Frontend → [http://localhost:8080](http://localhost:8080)
* Backend → [http://localhost:8000/docs](http://localhost:8000/docs)

---

## 🛠️ Technologies Used

### Backend

* Python 3.11
* FastAPI
* NumPy / PIL

### Frontend

* HTML / CSS / JavaScript
* Google Maps API

### AI / ML

* Quantum Reinforcement Learning (custom)
* Computer Vision pipeline

### External APIs

* Google Street View API
* Florida DOT 511 API

---

## 🗺️ Roadmap

* [ ] SeQUeNCe network integration
* [ ] QKD simulation integration
* [ ] Classical RL baseline (PPO)
* [ ] Communication-aware reward modeling
* [ ] Sensitivity analysis (latency, loss)
* [ ] Multi-run evaluation + metrics
* [ ] Disaster simulation scenarios

---

## ⚠️ Current Limitations

* Communication layer is currently **assumed ideal**
* QKD integration is **conceptual**
* No classical RL baseline yet
* Limited experimental evaluation

---

## 📚 Research Context

This project is being developed toward submission to:

> **IEEE GLOBECOM 2026 – Quantum Communications and Information Technology Symposium**

---

## 👥 Team

* Ishita Chakkalakkal
* Gabriella Vallar

---

## 📄 License

MIT License

---

## 💡 Acknowledgments

* Florida Gulf Coast University
* Google Maps Platform
* Florida DOT
* Open-source contributors

---

## 📞 Contact

For questions or collaboration:

* GitHub Issues
* Email: ijchakkalakkal8062@eagle.fgcu.edu

---

## 🚀 QuakeTwin

> *Bridging Digital Twins, Quantum Intelligence, and Secure Communication for Disaster-Resilient Systems*
