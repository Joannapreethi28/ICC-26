### shipped on xsport, POST-HOC re-run 5 Oct (current code incl. other-sport keep rule)

- set: `C:\Users\Jabin M\OneDrive\Desktop\ICC'26\testsets\xsport.csv` (60 queries). model models/laya-mak-v3; not the official E3 run
- latency per query p50 24.8 ms, p95 53.1 ms; prediction errors 0; confident errors (conf >= 0.9) 8

| question | lang | n | accuracy | 95% CI | ECE |
|---|---|---|---|---|---|
| gender_signal | en | 59 | 0.949 | 0.861-0.983 | 0.018 |
| gender_signal | ta | 1 | 1.000 | 0.207-1.000 | 0.043 |
| topic | en | 59 | 0.932 | 0.838-0.973 | 0.068 |
| topic | ta | 1 | 0.000 | 0.000-0.793 | 1.000 |

Gates (docs/09 §6):

- gender_signal en: 0.949 (95% CI 0.861-0.983, n=59) target 0.98 -> MISSED
- gender_signal ta: 1.000 (95% CI 0.207-1.000, n=1) target 0.98 -> MET
