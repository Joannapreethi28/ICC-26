## Classifier evaluation, mode=dev, 2026-10-04 09:27

DEVELOPMENT numbers on template-labelled calibration data. NOT test results; do not quote as accuracy.

### c_laya_ft on calib

- set: `C:\Users\Jabin M\OneDrive\Desktop\ICC'26\training\data\calib.jsonl` (600 queries). Fine-tuned Laya v2, calibrated per option-count bucket on calib.jsonl.
- latency per query p50 40.0 ms, p95 43.3 ms; prediction errors 0; confident errors (conf >= 0.9) 124

| question | lang | n | accuracy | 95% CI | ECE |
|---|---|---|---|---|---|
| family | en | 483 | 0.878 | 0.846-0.904 | 0.038 |
| format | en | 483 | 1.000 | 0.992-1.000 | 0.070 |
| gender_signal | en | 600 | 0.997 | 0.988-0.999 | 0.043 |
| stat | en | 483 | 0.743 | 0.703-0.780 | 0.071 |
| topic | en | 600 | 0.948 | 0.928-0.963 | 0.009 |

Gates (docs/09 §6):

- format en: 1.000 (95% CI 0.992-1.000, n=483) target 0.90 -> MET
- gender_signal en: 0.997 (95% CI 0.988-0.999, n=600) target 0.98 -> MET
- stat en: 0.743 (95% CI 0.703-0.780, n=483) target 0.90 -> MISSED

### c_laya_ft on messy

- set: `C:\Users\Jabin M\OneDrive\Desktop\ICC'26\training\data\messy_calib.jsonl` (600 queries). Fine-tuned Laya v2, calibrated per option-count bucket on calib.jsonl.
- latency per query p50 39.7 ms, p95 42.9 ms; prediction errors 0; confident errors (conf >= 0.9) 245

| question | lang | n | accuracy | 95% CI | ECE |
|---|---|---|---|---|---|
| family | en | 483 | 0.795 | 0.757-0.829 | 0.120 |
| format | en | 483 | 0.969 | 0.949-0.981 | 0.040 |
| gender_signal | en | 600 | 0.978 | 0.963-0.987 | 0.027 |
| stat | en | 483 | 0.658 | 0.615-0.699 | 0.145 |
| topic | en | 600 | 0.917 | 0.892-0.936 | 0.040 |

Gates (docs/09 §6):

- format en: 0.969 (95% CI 0.949-0.981, n=483) target 0.90 -> MET
- gender_signal en: 0.978 (95% CI 0.963-0.987, n=600) target 0.98 -> MISSED
- stat en: 0.658 (95% CI 0.615-0.699, n=483) target 0.90 -> MISSED

### c_laya_ft on voice

- set: `C:\Users\Jabin M\OneDrive\Desktop\ICC'26\training\data\voice_calib.jsonl` (600 queries). Fine-tuned Laya v2, calibrated per option-count bucket on calib.jsonl.
- latency per query p50 40.2 ms, p95 43.6 ms; prediction errors 0; confident errors (conf >= 0.9) 161

| question | lang | n | accuracy | 95% CI | ECE |
|---|---|---|---|---|---|
| family | en | 483 | 0.855 | 0.821-0.884 | 0.058 |
| format | en | 483 | 0.998 | 0.988-1.000 | 0.068 |
| gender_signal | en | 600 | 0.975 | 0.959-0.985 | 0.020 |
| stat | en | 483 | 0.714 | 0.672-0.753 | 0.088 |
| topic | en | 600 | 0.943 | 0.922-0.959 | 0.013 |

Gates (docs/09 §6):

- format en: 0.998 (95% CI 0.988-1.000, n=483) target 0.90 -> MET
- gender_signal en: 0.975 (95% CI 0.959-0.985, n=600) target 0.98 -> MISSED
- stat en: 0.714 (95% CI 0.672-0.753, n=483) target 0.90 -> MISSED

_(c_laya_ft wall time 76s)_

### d2_shipped_laya_first on calib

- set: `C:\Users\Jabin M\OneDrive\Desktop\ICC'26\training\data\calib.jsonl` (600 queries). Same as d but merge policy v2 (confident Laya beats rules on topic/family/stat; gender rules unchanged).
- latency per query p50 40.6 ms, p95 43.7 ms; prediction errors 0; confident errors (conf >= 0.9) 203

| question | lang | n | accuracy | 95% CI | ECE |
|---|---|---|---|---|---|
| family | en | 483 | 0.874 | 0.841-0.900 | 0.126 |
| format | en | 483 | 0.979 | 0.962-0.989 | 0.021 |
| gender_signal | en | 600 | 0.927 | 0.903-0.945 | 0.051 |
| stat | en | 483 | 0.834 | 0.799-0.865 | 0.166 |
| topic | en | 600 | 0.948 | 0.928-0.963 | 0.052 |

Gates (docs/09 §6):

- format en: 0.979 (95% CI 0.962-0.989, n=483) target 0.90 -> MET
- gender_signal en: 0.927 (95% CI 0.903-0.945, n=600) target 0.98 -> MISSED
- stat en: 0.834 (95% CI 0.799-0.865, n=483) target 0.90 -> MISSED

### d2_shipped_laya_first on messy

- set: `C:\Users\Jabin M\OneDrive\Desktop\ICC'26\training\data\messy_calib.jsonl` (600 queries). Same as d but merge policy v2 (confident Laya beats rules on topic/family/stat; gender rules unchanged).
- latency per query p50 40.8 ms, p95 43.7 ms; prediction errors 0; confident errors (conf >= 0.9) 357

| question | lang | n | accuracy | 95% CI | ECE |
|---|---|---|---|---|---|
| family | en | 483 | 0.793 | 0.755-0.827 | 0.207 |
| format | en | 483 | 0.915 | 0.887-0.937 | 0.085 |
| gender_signal | en | 600 | 0.932 | 0.909-0.949 | 0.052 |
| stat | en | 483 | 0.702 | 0.660-0.741 | 0.298 |
| topic | en | 600 | 0.917 | 0.892-0.936 | 0.083 |

Gates (docs/09 §6):

- format en: 0.915 (95% CI 0.887-0.937, n=483) target 0.90 -> MET
- gender_signal en: 0.932 (95% CI 0.909-0.949, n=600) target 0.98 -> MISSED
- stat en: 0.702 (95% CI 0.660-0.741, n=483) target 0.90 -> MISSED

### d2_shipped_laya_first on voice

- set: `C:\Users\Jabin M\OneDrive\Desktop\ICC'26\training\data\voice_calib.jsonl` (600 queries). Same as d but merge policy v2 (confident Laya beats rules on topic/family/stat; gender rules unchanged).
- latency per query p50 40.8 ms, p95 44.0 ms; prediction errors 0; confident errors (conf >= 0.9) 220

| question | lang | n | accuracy | 95% CI | ECE |
|---|---|---|---|---|---|
| family | en | 483 | 0.855 | 0.821-0.884 | 0.145 |
| format | en | 483 | 0.994 | 0.982-0.998 | 0.006 |
| gender_signal | en | 600 | 0.928 | 0.905-0.946 | 0.049 |
| stat | en | 483 | 0.807 | 0.770-0.840 | 0.193 |
| topic | en | 600 | 0.943 | 0.922-0.959 | 0.057 |

Gates (docs/09 §6):

- format en: 0.994 (95% CI 0.982-0.998, n=483) target 0.90 -> MET
- gender_signal en: 0.928 (95% CI 0.905-0.946, n=600) target 0.98 -> MISSED
- stat en: 0.807 (95% CI 0.770-0.840, n=483) target 0.90 -> MISSED

_(d2_shipped_laya_first wall time 66s)_
