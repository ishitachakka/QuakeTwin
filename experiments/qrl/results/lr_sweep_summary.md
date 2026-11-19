# lr sweep (comm_aware_secure, 15 segments), mean ± 95% CI over 5 seeds

Accuracy in %; health and cost are end-of-episode values at medium stress.

| lr | agent | baseline acc | medium acc | disaster acc | medium health | medium cost | train s |
|---|---|---|---|---|---|---|---|
| 0.001 | QRL | 61.8 ± 14.3 | 57.8 ± 5.4 | 43.3 ± 3.5 | 0.71 ± 0.04 | 49.68 ± 16.52 | 30 |
| 0.001 | PPO | 83.5 ± 4.1 | 71.2 ± 1.3 | 49.8 ± 0.3 | 0.79 ± 0.01 | 39.41 ± 0.88 | 8 |
| 0.005 | QRL | 92.6 ± 3.2 | 74.4 ± 2.0 | 50.4 ± 2.3 | 0.81 ± 0.01 | 41.77 ± 3.79 | 29 |
| 0.005 | PPO | 92.4 ± 2.8 | 76.8 ± 1.9 | 53.6 ± 2.5 | 0.82 ± 0.01 | 43.35 ± 2.42 | 9 |
| 0.01 | QRL | 91.6 ± 2.4 | 76.2 ± 1.5 | 51.5 ± 2.9 | 0.82 ± 0.01 | 42.68 ± 2.33 | 29 |
| 0.01 | PPO | 92.8 ± 2.2 | 77.1 ± 2.2 | 53.8 ± 2.3 | 0.82 ± 0.01 | 44.84 ± 7.21 | 10 |