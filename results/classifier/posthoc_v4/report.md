## Classifier evaluation, mode=posthoc, 2026-10-04 10:19

POST-HOC, TEST-INFORMED: this model was changed after the official single test run, using aggregate test slice/confusion counts (no test text). Report next to the official run in results/classifier/test/; this is NOT an untouched held-out result.

### c_laya_ft on en

- set: `C:\Users\Jabin M\OneDrive\Desktop\ICC'26\testsets\nlu_en.csv` (337 queries). Fine-tuned Laya v2, calibrated per option-count bucket on calib.jsonl.
- latency per query p50 40.1 ms, p95 45.3 ms; prediction errors 0; confident errors (conf >= 0.9) 260

| question | lang | n | accuracy | 95% CI | ECE |
|---|---|---|---|---|---|
| family | en | 294 | 0.660 | 0.604-0.712 | 0.260 |
| format | en | 294 | 0.884 | 0.843-0.916 | 0.071 |
| gender_signal | en | 337 | 0.926 | 0.893-0.949 | 0.040 |
| stat | en | 294 | 0.473 | 0.416-0.530 | 0.321 |
| topic | en | 337 | 0.947 | 0.917-0.966 | 0.021 |

Gates (docs/09 §6):

- format en: 0.884 (95% CI 0.843-0.916, n=294) target 0.90 -> MISSED
- gender_signal en: 0.926 (95% CI 0.893-0.949, n=337) target 0.98 -> MISSED
- stat en: 0.473 (95% CI 0.416-0.530, n=294) target 0.90 -> MISSED

### c_laya_ft on hi

- set: `C:\Users\Jabin M\OneDrive\Desktop\ICC'26\testsets\nlu_hi.csv` (203 queries). Fine-tuned Laya v2, calibrated per option-count bucket on calib.jsonl.
- latency per query p50 40.2 ms, p95 43.1 ms; prediction errors 0; confident errors (conf >= 0.9) 164

| question | lang | n | accuracy | 95% CI | ECE |
|---|---|---|---|---|---|
| family | hi | 186 | 0.688 | 0.618-0.750 | 0.245 |
| format | hi | 186 | 0.817 | 0.755-0.866 | 0.136 |
| gender_signal | hi | 203 | 0.906 | 0.858-0.939 | 0.060 |
| stat | hi | 186 | 0.527 | 0.455-0.597 | 0.273 |
| topic | hi | 203 | 0.956 | 0.918-0.977 | 0.007 |

Gates (docs/09 §6):

- format hi: 0.817 (95% CI 0.755-0.866, n=186) target 0.85 -> MISSED
- gender_signal hi: 0.906 (95% CI 0.858-0.939, n=203) target 0.98 -> MISSED
- stat hi: 0.527 (95% CI 0.455-0.597, n=186) target 0.85 -> MISSED

### c_laya_ft on ta

- set: `C:\Users\Jabin M\OneDrive\Desktop\ICC'26\testsets\nlu_ta.csv` (210 queries). Fine-tuned Laya v2, calibrated per option-count bucket on calib.jsonl.
- latency per query p50 40.4 ms, p95 43.3 ms; prediction errors 0; confident errors (conf >= 0.9) 163

| question | lang | n | accuracy | 95% CI | ECE |
|---|---|---|---|---|---|
| family | ta | 189 | 0.677 | 0.608-0.740 | 0.264 |
| format | ta | 189 | 0.810 | 0.748-0.859 | 0.138 |
| gender_signal | ta | 210 | 0.933 | 0.891-0.960 | 0.033 |
| stat | ta | 189 | 0.466 | 0.396-0.537 | 0.248 |
| topic | ta | 210 | 0.933 | 0.891-0.960 | 0.032 |

Gates (docs/09 §6):

- format ta: 0.810 (95% CI 0.748-0.859, n=189) target 0.80 -> MET
- gender_signal ta: 0.933 (95% CI 0.891-0.960, n=210) target 0.98 -> MISSED
- stat ta: 0.466 (95% CI 0.396-0.537, n=189) target 0.80 -> MISSED

_(c_laya_ft wall time 37s)_

### d_shipped on en

- set: `C:\Users\Jabin M\OneDrive\Desktop\ICC'26\testsets\nlu_en.csv` (337 queries). understand(use_laya=True): rules override + Laya v2, merge policy v1; non-gender confidences reported as 1.0.
- latency per query p50 39.5 ms, p95 42.5 ms; prediction errors 0; confident errors (conf >= 0.9) 313

| question | lang | n | accuracy | 95% CI | ECE |
|---|---|---|---|---|---|
| family | en | 294 | 0.663 | 0.607-0.715 | 0.337 |
| format | en | 294 | 0.884 | 0.843-0.916 | 0.116 |
| gender_signal | en | 337 | 0.929 | 0.896-0.952 | 0.068 |
| stat | en | 294 | 0.531 | 0.474-0.587 | 0.469 |
| topic | en | 337 | 0.947 | 0.917-0.966 | 0.053 |

Gates (docs/09 §6):

- format en: 0.884 (95% CI 0.843-0.916, n=294) target 0.90 -> MISSED
- gender_signal en: 0.929 (95% CI 0.896-0.952, n=337) target 0.98 -> MISSED
- stat en: 0.531 (95% CI 0.474-0.587, n=294) target 0.90 -> MISSED

### d_shipped on hi

- set: `C:\Users\Jabin M\OneDrive\Desktop\ICC'26\testsets\nlu_hi.csv` (203 queries). understand(use_laya=True): rules override + Laya v2, merge policy v1; non-gender confidences reported as 1.0.
- latency per query p50 40.1 ms, p95 42.5 ms; prediction errors 0; confident errors (conf >= 0.9) 206

| question | lang | n | accuracy | 95% CI | ECE |
|---|---|---|---|---|---|
| family | hi | 186 | 0.694 | 0.624-0.755 | 0.306 |
| format | hi | 186 | 0.817 | 0.755-0.866 | 0.183 |
| gender_signal | hi | 203 | 0.892 | 0.841-0.927 | 0.095 |
| stat | hi | 186 | 0.543 | 0.471-0.613 | 0.457 |
| topic | hi | 203 | 0.961 | 0.924-0.980 | 0.039 |

Gates (docs/09 §6):

- format hi: 0.817 (95% CI 0.755-0.866, n=186) target 0.85 -> MISSED
- gender_signal hi: 0.892 (95% CI 0.841-0.927, n=203) target 0.98 -> MISSED
- stat hi: 0.543 (95% CI 0.471-0.613, n=186) target 0.85 -> MISSED

### d_shipped on ta

- set: `C:\Users\Jabin M\OneDrive\Desktop\ICC'26\testsets\nlu_ta.csv` (210 queries). understand(use_laya=True): rules override + Laya v2, merge policy v1; non-gender confidences reported as 1.0.
- latency per query p50 40.7 ms, p95 44.2 ms; prediction errors 0; confident errors (conf >= 0.9) 227

| question | lang | n | accuracy | 95% CI | ECE |
|---|---|---|---|---|---|
| family | ta | 189 | 0.672 | 0.602-0.735 | 0.328 |
| format | ta | 189 | 0.820 | 0.759-0.868 | 0.180 |
| gender_signal | ta | 210 | 0.924 | 0.880-0.953 | 0.052 |
| stat | ta | 189 | 0.466 | 0.396-0.537 | 0.534 |
| topic | ta | 210 | 0.933 | 0.891-0.960 | 0.067 |

Gates (docs/09 §6):

- format ta: 0.820 (95% CI 0.759-0.868, n=189) target 0.80 -> MET
- gender_signal ta: 0.924 (95% CI 0.880-0.953, n=210) target 0.98 -> MISSED
- stat ta: 0.466 (95% CI 0.396-0.537, n=189) target 0.80 -> MISSED

_(d_shipped wall time 28s)_
