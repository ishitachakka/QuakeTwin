# Ablation (decision accuracy %, mean ± 95% CI over seeds)


## stress = baseline

| setting | QRL | PPO-small | PPO |
|---|---|---|---|
| no_comm_dt | 65.9 ± 10.0 (n=10) | 54.2 ± 3.7 (n=10) | 67.1 ± 4.8 (n=10) |
| comm_aware | 80.6 ± 4.1 (n=10) | 65.5 ± 3.5 (n=10) | 88.5 ± 2.6 (n=10) |
| comm_aware_secure | 91.6 ± 1.6 (n=10) | 88.2 ± 2.3 (n=10) | 91.5 ± 1.7 (n=10) |

## stress = low

| setting | QRL | PPO-small | PPO |
|---|---|---|---|
| no_comm_dt | 70.1 ± 9.6 (n=10) | 60.0 ± 3.7 (n=10) | 71.3 ± 2.8 (n=10) |
| comm_aware | 81.7 ± 2.6 (n=10) | 68.2 ± 2.9 (n=10) | 82.5 ± 1.2 (n=10) |
| comm_aware_secure | 90.6 ± 1.4 (n=10) | 87.5 ± 2.4 (n=10) | 90.6 ± 1.5 (n=10) |

## stress = medium

| setting | QRL | PPO-small | PPO |
|---|---|---|---|
| no_comm_dt | 67.9 ± 9.8 (n=10) | 54.1 ± 2.4 (n=10) | 58.3 ± 0.4 (n=10) |
| comm_aware | 72.2 ± 2.5 (n=10) | 55.4 ± 2.4 (n=10) | 59.1 ± 0.2 (n=10) |
| comm_aware_secure | 74.8 ± 1.2 (n=10) | 72.8 ± 1.1 (n=10) | 76.1 ± 1.2 (n=10) |

## stress = high

| setting | QRL | PPO-small | PPO |
|---|---|---|---|
| no_comm_dt | 59.7 ± 8.8 (n=10) | 43.2 ± 1.2 (n=10) | 43.3 ± 0.2 (n=10) |
| comm_aware | 62.0 ± 2.1 (n=10) | 44.1 ± 0.7 (n=10) | 44.1 ± 0.1 (n=10) |
| comm_aware_secure | 63.2 ± 1.1 (n=10) | 62.5 ± 1.1 (n=10) | 64.1 ± 1.2 (n=10) |

## stress = disaster

| setting | QRL | PPO-small | PPO |
|---|---|---|---|
| no_comm_dt | 48.8 ± 9.3 (n=10) | 25.9 ± 0.9 (n=10) | 23.2 ± 0.2 (n=10) |
| comm_aware | 48.1 ± 4.7 (n=10) | 29.6 ± 2.5 (n=10) | 26.3 ± 0.4 (n=10) |
| comm_aware_secure | 50.6 ± 1.3 (n=10) | 50.4 ± 0.9 (n=10) | 52.5 ± 1.9 (n=10) |

## packet loss sweep, setting = comm_aware_secure vs no_comm_dt

| config | 0 | 1 | 2 | 3 |
| no_comm_dt / QRL | 65.9 ± 10.0 | 67.6 ± 10.1 | 65.8 ± 9.4 | 65.7 ± 8.3 |
| no_comm_dt / PPO-small | 54.2 ± 3.7 | 57.5 ± 3.5 | 57.7 ± 3.5 | 59.7 ± 2.9 |
| no_comm_dt / PPO | 67.1 ± 4.8 | 69.2 ± 4.5 | 68.4 ± 3.9 | 68.6 ± 3.1 |
| comm_aware_secure / QRL | 91.6 ± 1.6 | 91.2 ± 1.3 | 88.9 ± 1.3 | 86.4 ± 1.1 |
| comm_aware_secure / PPO-small | 88.2 ± 2.3 | 88.2 ± 1.9 | 86.0 ± 1.9 | 83.7 ± 1.6 |
| comm_aware_secure / PPO | 91.5 ± 1.7 | 91.1 ± 1.4 | 88.9 ± 1.2 | 86.4 ± 1.1 |

## MITM attack rate sweep, setting = comm_aware_secure vs no_comm_dt

| config | 0 | 1 | 2 | 3 | 4 |
| no_comm_dt / QRL | 65.9 ± 10.0 | 71.0 ± 9.9 | 72.0 ± 10.3 | 73.6 ± 10.8 | 69.7 ± 12.4 |
| no_comm_dt / PPO-small | 54.2 ± 3.7 | 60.9 ± 4.4 | 60.7 ± 3.8 | 58.1 ± 3.1 | 45.5 ± 2.4 |
| no_comm_dt / PPO | 67.1 ± 4.8 | 71.4 ± 2.8 | 68.7 ± 1.7 | 63.7 ± 1.2 | 49.3 ± 0.6 |
| comm_aware_secure / QRL | 91.6 ± 1.6 | 90.7 ± 1.5 | 89.0 ± 1.4 | 87.4 ± 1.5 | 81.0 ± 1.8 |
| comm_aware_secure / PPO-small | 88.2 ± 2.3 | 87.5 ± 2.0 | 85.6 ± 1.9 | 84.0 ± 2.0 | 77.0 ± 2.4 |
| comm_aware_secure / PPO | 91.5 ± 1.7 | 90.7 ± 1.6 | 89.1 ± 1.5 | 87.4 ± 1.7 | 81.4 ± 1.6 |

## latency (ms) sweep, setting = comm_aware_secure vs no_comm_dt

| config | 0 | 1 | 2 | 3 | 4 |
| no_comm_dt / QRL | 65.9 ± 10.0 | 66.9 ± 8.5 | 59.6 ± 7.1 | 54.9 ± 6.1 | 51.3 ± 5.4 |
| no_comm_dt / PPO-small | 54.2 ± 3.7 | 66.2 ± 2.2 | 59.4 ± 1.9 | 54.4 ± 1.5 | 50.6 ± 1.2 |
| no_comm_dt / PPO | 67.1 ± 4.8 | 75.2 ± 1.2 | 66.7 ± 1.0 | 60.5 ± 1.0 | 55.7 ± 0.8 |
| comm_aware_secure / QRL | 91.6 ± 1.6 | 79.5 ± 0.9 | 67.7 ± 0.9 | 58.7 ± 1.1 | 52.1 ± 1.2 |
| comm_aware_secure / PPO-small | 88.2 ± 2.3 | 77.8 ± 0.9 | 66.9 ± 0.8 | 58.7 ± 0.7 | 52.5 ± 0.7 |
| comm_aware_secure / PPO | 91.5 ± 1.7 | 80.8 ± 0.9 | 69.1 ± 0.7 | 60.2 ± 1.1 | 53.5 ± 1.2 |

Actor parameter counts: {'QRL': {'encoder': 8, 'circuit': 8, 'head': 9, 'total': 25}, 'PPO-small': {'total': 31}, 'PPO': {'total': 451}}
