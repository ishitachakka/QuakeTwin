# Security modes (R1 5.1/5.2): decision accuracy %, mean ± 95% CI over seeds

QKD-only: a = probability the feeder hop has QKD key for a message. PQC-only and hybrid are identical in this decision model.

| mode | agent | stress | a=1 | a=0.8 | a=0.6 | a=0.4 | a=0.2 |
|---|---|---|---|---|---|---|---|
| none | QRL | baseline | 79.6 ± 6.8 | - | - | - | - |
| none | QRL | medium | 69.6 ± 8.9 | - | - | - | - |
| none | QRL | disaster | 41.9 ± 10.6 | - | - | - | - |
| none | PPO | baseline | 90.1 ± 3.4 | - | - | - | - |
| none | PPO | medium | 59.2 ± 0.3 | - | - | - | - |
| none | PPO | disaster | 26.5 ± 0.8 | - | - | - | - |
| pqc_or_hybrid | QRL | baseline | 92.5 ± 3.2 | - | - | - | - |
| pqc_or_hybrid | QRL | medium | 74.6 ± 1.9 | - | - | - | - |
| pqc_or_hybrid | QRL | disaster | 50.4 ± 2.3 | - | - | - | - |
| pqc_or_hybrid | PPO | baseline | 92.0 ± 3.0 | - | - | - | - |
| pqc_or_hybrid | PPO | medium | 76.4 ± 1.9 | - | - | - | - |
| pqc_or_hybrid | PPO | disaster | 52.6 ± 1.6 | - | - | - | - |
| qkd_only | QRL | baseline | 91.5 ± 1.4 | 88.7 ± 1.3 | 85.2 ± 1.2 | 79.7 ± 1.0 | 74.0 ± 0.6 |
| qkd_only | QRL | medium | 75.5 ± 1.3 | 73.8 ± 1.0 | 71.6 ± 1.0 | 69.9 ± 1.1 | 67.8 ± 1.1 |
| qkd_only | QRL | disaster | 51.3 ± 2.5 | 52.3 ± 1.6 | 55.5 ± 1.5 | 59.6 ± 0.6 | 64.6 ± 1.6 |
| qkd_only | PPO | baseline | 90.3 ± 0.4 | 87.7 ± 0.6 | 84.7 ± 0.6 | 79.8 ± 0.7 | 74.8 ± 1.3 |
| qkd_only | PPO | medium | 77.9 ± 1.5 | 75.4 ± 1.1 | 73.1 ± 0.5 | 72.4 ± 1.3 | 69.8 ± 1.2 |
| qkd_only | PPO | disaster | 54.1 ± 2.6 | 53.5 ± 2.0 | 56.9 ± 2.0 | 61.9 ± 2.5 | 66.4 ± 1.4 |