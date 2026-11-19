# Hybrid QKD + ML-KEM with authentication cost (R1 comment 4.3): accuracy %, mean ± 95% CI over seeds

Each key refresh (every 50 messages) holds up the hop for key exchange + authentication time at the given link rate; a refresh that outlasts one step keeps delaying delivery until it finishes.

Caveat: at 20 kbps the refresh rarely finishes before the next one is due (ML-DSA every refresh especially), so the backlog does not drain within an episode and the hop stays effectively always-busy -- treat the 20 kbps column as 'severely degraded', not a precise point on a curve. At disaster stress, the packet-loss/attack-rate floor already dominates over refresh-induced lag, so the 1000/100/20 kbps columns can come out nearly identical there; this is expected, not a bug, and is a weaker test of the link-rate effect than the baseline/medium rows.

| mode | agent | stress | 1000 kbps | 100 kbps | 20 kbps |
|---|---|---|---|---|---|
| hybrid_mldsa_first_round | QRL | baseline | 90.3 ± 0.2 | 89.6 ± 0.2 | 68.6 ± 0.7 |
| hybrid_mldsa_first_round | QRL | medium | 76.5 ± 1.4 | 76.5 ± 1.4 | 63.2 ± 1.3 |
| hybrid_mldsa_first_round | QRL | disaster | 52.0 ± 8.0 | 52.0 ± 8.0 | 52.0 ± 8.0 |
| hybrid_mldsa_first_round | PPO | baseline | 89.9 ± 0.9 | 89.3 ± 1.0 | 68.3 ± 0.7 |
| hybrid_mldsa_first_round | PPO | medium | 77.9 ± 0.9 | 77.9 ± 0.9 | 65.3 ± 0.7 |
| hybrid_mldsa_first_round | PPO | disaster | 60.6 ± 2.7 | 60.6 ± 2.7 | 60.6 ± 2.7 |
| pqc_only_mldsa_every_refresh | QRL | baseline | 90.7 ± 1.6 | 87.8 ± 0.7 | 68.6 ± 0.3 |
| pqc_only_mldsa_every_refresh | QRL | medium | 75.9 ± 2.1 | 75.3 ± 1.9 | 63.4 ± 1.2 |
| pqc_only_mldsa_every_refresh | QRL | disaster | 53.8 ± 5.6 | 53.7 ± 5.7 | 53.7 ± 5.7 |
| pqc_only_mldsa_every_refresh | PPO | baseline | 89.6 ± 0.7 | 87.4 ± 0.8 | 68.2 ± 0.4 |
| pqc_only_mldsa_every_refresh | PPO | medium | 78.7 ± 0.6 | 77.7 ± 0.6 | 66.5 ± 0.9 |
| pqc_only_mldsa_every_refresh | PPO | disaster | 65.7 ± 2.1 | 65.7 ± 2.1 | 65.7 ± 2.1 |