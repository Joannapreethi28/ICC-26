## Classifier evaluation, mode=posthoc, 2026-10-04 09:40

POST-HOC, TEST-INFORMED: this model was changed after the official single test run, using aggregate test slice/confusion counts (no test text). Report next to the official run in results/classifier/test/; this is NOT an untouched held-out result.

### c_laya_ft on en

- set: `C:\Users\Jabin M\OneDrive\Desktop\ICC'26\testsets\nlu_en.csv` (337 queries). Fine-tuned Laya v2, calibrated per option-count bucket on calib.jsonl.
- latency per query p50 40.4 ms, p95 47.2 ms; prediction errors 0; confident errors (conf >= 0.9) 262

| question | lang | n | accuracy | 95% CI | ECE |
|---|---|---|---|---|---|
| family | en | 294 | 0.677 | 0.621-0.728 | 0.214 |
| format | en | 294 | 0.891 | 0.850-0.922 | 0.086 |
| gender_signal | en | 337 | 0.914 | 0.879-0.939 | 0.043 |
| stat | en | 294 | 0.497 | 0.440-0.553 | 0.319 |
| topic | en | 337 | 0.920 | 0.886-0.944 | 0.033 |

Gates (docs/09 §6):

- format en: 0.891 (95% CI 0.850-0.922, n=294) target 0.90 -> MISSED
- gender_signal en: 0.914 (95% CI 0.879-0.939, n=337) target 0.98 -> MISSED
- stat en: 0.497 (95% CI 0.440-0.553, n=294) target 0.90 -> MISSED

### c_laya_ft on hi

- set: `C:\Users\Jabin M\OneDrive\Desktop\ICC'26\testsets\nlu_hi.csv` (203 queries). Fine-tuned Laya v2, calibrated per option-count bucket on calib.jsonl.
- latency per query p50 40.5 ms, p95 43.8 ms; prediction errors 0; confident errors (conf >= 0.9) 165

| question | lang | n | accuracy | 95% CI | ECE |
|---|---|---|---|---|---|
| family | hi | 186 | 0.704 | 0.635-0.765 | 0.191 |
| format | hi | 186 | 0.860 | 0.803-0.903 | 0.090 |
| gender_signal | hi | 203 | 0.897 | 0.847-0.931 | 0.060 |
| stat | hi | 186 | 0.527 | 0.455-0.597 | 0.321 |
| topic | hi | 203 | 0.946 | 0.906-0.969 | 0.011 |

Gates (docs/09 §6):

- format hi: 0.860 (95% CI 0.803-0.903, n=186) target 0.85 -> MET
- gender_signal hi: 0.897 (95% CI 0.847-0.931, n=203) target 0.98 -> MISSED
- stat hi: 0.527 (95% CI 0.455-0.597, n=186) target 0.85 -> MISSED

### c_laya_ft on ta

- set: `C:\Users\Jabin M\OneDrive\Desktop\ICC'26\testsets\nlu_ta.csv` (210 queries). Fine-tuned Laya v2, calibrated per option-count bucket on calib.jsonl.
- latency per query p50 40.2 ms, p95 43.7 ms; prediction errors 0; confident errors (conf >= 0.9) 154

| question | lang | n | accuracy | 95% CI | ECE |
|---|---|---|---|---|---|
| family | ta | 189 | 0.704 | 0.635-0.764 | 0.194 |
| format | ta | 189 | 0.868 | 0.812-0.909 | 0.094 |
| gender_signal | ta | 210 | 0.919 | 0.874-0.949 | 0.034 |
| stat | ta | 189 | 0.529 | 0.458-0.599 | 0.265 |
| topic | ta | 210 | 0.919 | 0.874-0.949 | 0.038 |

Gates (docs/09 §6):

- format ta: 0.868 (95% CI 0.812-0.909, n=189) target 0.80 -> MET
- gender_signal ta: 0.919 (95% CI 0.874-0.949, n=210) target 0.98 -> MISSED
- stat ta: 0.529 (95% CI 0.458-0.599, n=189) target 0.80 -> MISSED

_(c_laya_ft wall time 39s)_

### d_shipped on en

- set: `C:\Users\Jabin M\OneDrive\Desktop\ICC'26\testsets\nlu_en.csv` (337 queries). understand(use_laya=True): rules override + Laya v2, merge policy v1; non-gender confidences reported as 1.0.
- latency per query p50 39.1 ms, p95 42.2 ms; prediction errors 0; confident errors (conf >= 0.9) 342

| question | lang | n | accuracy | 95% CI | ECE |
|---|---|---|---|---|---|
| family | en | 294 | 0.701 | 0.646-0.750 | 0.299 |
| format | en | 294 | 0.888 | 0.847-0.919 | 0.112 |
| gender_signal | en | 337 | 0.801 | 0.755-0.840 | 0.193 |
| stat | en | 294 | 0.561 | 0.504-0.617 | 0.439 |
| topic | en | 337 | 0.926 | 0.893-0.949 | 0.074 |

Gates (docs/09 §6):

- format en: 0.888 (95% CI 0.847-0.919, n=294) target 0.90 -> MISSED
- gender_signal en: 0.801 (95% CI 0.755-0.840, n=337) target 0.98 -> MISSED
- stat en: 0.561 (95% CI 0.504-0.617, n=294) target 0.90 -> MISSED

### d_shipped on hi

- set: `C:\Users\Jabin M\OneDrive\Desktop\ICC'26\testsets\nlu_hi.csv` (203 queries). understand(use_laya=True): rules override + Laya v2, merge policy v1; non-gender confidences reported as 1.0.
- latency per query p50 40.1 ms, p95 42.8 ms; prediction errors 0; confident errors (conf >= 0.9) 196

| question | lang | n | accuracy | 95% CI | ECE |
|---|---|---|---|---|---|
| family | hi | 186 | 0.715 | 0.646-0.775 | 0.285 |
| format | hi | 186 | 0.855 | 0.797-0.898 | 0.145 |
| gender_signal | hi | 203 | 0.887 | 0.836-0.923 | 0.092 |
| stat | hi | 186 | 0.559 | 0.487-0.629 | 0.441 |
| topic | hi | 203 | 0.946 | 0.906-0.969 | 0.054 |

Gates (docs/09 §6):

- format hi: 0.855 (95% CI 0.797-0.898, n=186) target 0.85 -> MET
- gender_signal hi: 0.887 (95% CI 0.836-0.923, n=203) target 0.98 -> MISSED
- stat hi: 0.559 (95% CI 0.487-0.629, n=186) target 0.85 -> MISSED

### d_shipped on ta

- set: `C:\Users\Jabin M\OneDrive\Desktop\ICC'26\testsets\nlu_ta.csv` (210 queries). understand(use_laya=True): rules override + Laya v2, merge policy v1; non-gender confidences reported as 1.0.
- latency per query p50 40.7 ms, p95 44.1 ms; prediction errors 0; confident errors (conf >= 0.9) 196

| question | lang | n | accuracy | 95% CI | ECE |
|---|---|---|---|---|---|
| family | ta | 189 | 0.714 | 0.646-0.774 | 0.286 |
| format | ta | 189 | 0.868 | 0.812-0.909 | 0.132 |
| gender_signal | ta | 210 | 0.929 | 0.886-0.956 | 0.040 |
| stat | ta | 189 | 0.550 | 0.479-0.619 | 0.450 |
| topic | ta | 210 | 0.919 | 0.874-0.949 | 0.081 |

Gates (docs/09 §6):

- format ta: 0.868 (95% CI 0.812-0.909, n=189) target 0.80 -> MET
- gender_signal ta: 0.929 (95% CI 0.886-0.956, n=210) target 0.98 -> MISSED
- stat ta: 0.550 (95% CI 0.479-0.619, n=189) target 0.80 -> MISSED

_(d_shipped wall time 28s)_
