## E3 cross-sport (testsets/xsport.csv), first and only run with the selected model

### rules on xsport

- set: `C:\Users\Jabin M\OneDrive\Desktop\ICC'26\testsets\xsport.csv` (60 queries). model models/laya-mak-v3; only gender_signal/topic are meaningful here
- latency per query p50 0.1 ms, p95 0.1 ms; prediction errors 0; confident errors (conf >= 0.9) 26

| question | lang | n | accuracy | 95% CI | ECE |
|---|---|---|---|---|---|
| gender_signal | en | 59 | 0.847 | 0.735-0.918 | 0.153 |
| gender_signal | ta | 1 | 1.000 | 0.207-1.000 | 0.000 |
| topic | en | 59 | 0.729 | 0.604-0.826 | 0.271 |
| topic | ta | 1 | 0.000 | 0.000-0.793 | 1.000 |

Gates (docs/09 §6):

- gender_signal en: 0.847 (95% CI 0.735-0.918, n=59) target 0.98 -> MISSED
- gender_signal ta: 1.000 (95% CI 0.207-1.000, n=1) target 0.98 -> MET

### laya_ft on xsport

- set: `C:\Users\Jabin M\OneDrive\Desktop\ICC'26\testsets\xsport.csv` (60 queries). model models/laya-mak-v3; only gender_signal/topic are meaningful here
- latency per query p50 23.5 ms, p95 44.9 ms; prediction errors 0; confident errors (conf >= 0.9) 14

| question | lang | n | accuracy | 95% CI | ECE |
|---|---|---|---|---|---|
| gender_signal | en | 59 | 0.949 | 0.861-0.983 | 0.008 |
| gender_signal | ta | 1 | 1.000 | 0.207-1.000 | 0.043 |
| topic | en | 59 | 0.797 | 0.677-0.880 | 0.153 |
| topic | ta | 1 | 0.000 | 0.000-0.793 | 0.958 |

Gates (docs/09 §6):

- gender_signal en: 0.949 (95% CI 0.861-0.983, n=59) target 0.98 -> MISSED
- gender_signal ta: 1.000 (95% CI 0.207-1.000, n=1) target 0.98 -> MET

### shipped on xsport

- set: `C:\Users\Jabin M\OneDrive\Desktop\ICC'26\testsets\xsport.csv` (60 queries). model models/laya-mak-v3; only gender_signal/topic are meaningful here
- latency per query p50 24.0 ms, p95 45.0 ms; prediction errors 0; confident errors (conf >= 0.9) 16

| question | lang | n | accuracy | 95% CI | ECE |
|---|---|---|---|---|---|
| gender_signal | en | 59 | 0.949 | 0.861-0.983 | 0.018 |
| gender_signal | ta | 1 | 1.000 | 0.207-1.000 | 0.043 |
| topic | en | 59 | 0.797 | 0.677-0.880 | 0.203 |
| topic | ta | 1 | 0.000 | 0.000-0.793 | 1.000 |

Gates (docs/09 §6):

- gender_signal en: 0.949 (95% CI 0.861-0.983, n=59) target 0.98 -> MISSED
- gender_signal ta: 1.000 (95% CI 0.207-1.000, n=1) target 0.98 -> MET
