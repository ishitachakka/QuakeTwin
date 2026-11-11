# Scale / damage-pattern (trained at 15 segments, random damage; comm_aware_secure). accuracy %, mean ± 95% CI over 5 seeds

| network | damage | stress | QRL | PPO-small | PPO |
|---|---|---|---|---|---|
| 15 | random | baseline | 92.1 ± 3.6 | 85.7 ± 5.9 | 91.5 ± 3.4 |
| 15 | random | medium | 73.6 ± 2.7 | 70.1 ± 3.0 | 76.2 ± 2.7 |
| 15 | random | disaster | 49.1 ± 2.3 | 47.5 ± 2.4 | 50.8 ± 1.4 |
| 15 | concentrated | baseline | 96.2 ± 1.4 | 93.2 ± 2.8 | 96.0 ± 1.3 |
| 15 | concentrated | medium | 81.1 ± 0.5 | 80.1 ± 1.0 | 82.2 ± 1.4 |
| 15 | concentrated | disaster | 70.3 ± 0.4 | 70.1 ± 0.6 | 70.1 ± 0.5 |
| 100 | random | baseline | 92.8 ± 3.4 | 88.0 ± 4.4 | 92.4 ± 2.8 |
| 100 | random | medium | 76.4 ± 1.7 | 73.4 ± 3.2 | 77.7 ± 1.7 |
| 100 | random | disaster | 49.8 ± 1.9 | 48.3 ± 2.5 | 51.2 ± 1.1 |
| 100 | concentrated | baseline | 96.9 ± 1.3 | 93.1 ± 3.8 | 96.7 ± 0.9 |
| 100 | concentrated | medium | 84.6 ± 1.0 | 83.2 ± 1.7 | 85.4 ± 1.1 |
| 100 | concentrated | disaster | 68.2 ± 0.8 | 67.9 ± 0.6 | 68.7 ± 0.3 |
| 200 | random | baseline | 92.8 ± 3.3 | 87.5 ± 4.7 | 92.4 ± 2.9 |
| 200 | random | medium | 76.1 ± 1.9 | 73.2 ± 3.1 | 77.6 ± 1.9 |
| 200 | random | disaster | 52.6 ± 1.8 | 50.4 ± 2.8 | 53.5 ± 1.0 |
| 200 | concentrated | baseline | 96.7 ± 1.6 | 92.5 ± 3.9 | 96.4 ± 1.1 |
| 200 | concentrated | medium | 84.7 ± 1.2 | 83.1 ± 2.1 | 85.6 ± 1.2 |
| 200 | concentrated | disaster | 67.9 ± 1.0 | 67.3 ± 1.0 | 68.7 ± 0.8 |