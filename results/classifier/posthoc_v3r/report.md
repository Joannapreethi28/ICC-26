## Classifier evaluation, mode=posthoc, 2026-10-04 09:44

POST-HOC, TEST-INFORMED: this model was changed after the official single test run, using aggregate test slice/confusion counts (no test text). Report next to the official run in results/classifier/test/; this is NOT an untouched held-out result.

### a_rules on en

- set: `C:\Users\Jabin M\OneDrive\Desktop\ICC'26\testsets\nlu_en.csv` (337 queries). Rules are deterministic: confidence 1.0, so ECE is not meaningful for this arm.
- latency per query p50 0.1 ms, p95 0.2 ms; prediction errors 0; confident errors (conf >= 0.9) 453

| question | lang | n | accuracy | 95% CI | ECE |
|---|---|---|---|---|---|
| family | en | 294 | 0.565 | 0.507-0.620 | 0.435 |
| format | en | 294 | 0.643 | 0.587-0.695 | 0.357 |
| gender_signal | en | 337 | 0.941 | 0.910-0.961 | 0.059 |
| stat | en | 294 | 0.500 | 0.443-0.557 | 0.500 |
| topic | en | 337 | 0.843 | 0.800-0.878 | 0.157 |

Gates (docs/09 §6):

- format en: 0.643 (95% CI 0.587-0.695, n=294) target 0.90 -> MISSED
- gender_signal en: 0.941 (95% CI 0.910-0.961, n=337) target 0.98 -> MISSED
- stat en: 0.500 (95% CI 0.443-0.557, n=294) target 0.90 -> MISSED

### a_rules on hi

- set: `C:\Users\Jabin M\OneDrive\Desktop\ICC'26\testsets\nlu_hi.csv` (203 queries). Rules are deterministic: confidence 1.0, so ECE is not meaningful for this arm.
- latency per query p50 0.2 ms, p95 0.5 ms; prediction errors 0; confident errors (conf >= 0.9) 337

| question | lang | n | accuracy | 95% CI | ECE |
|---|---|---|---|---|---|
| family | hi | 186 | 0.478 | 0.408-0.550 | 0.522 |
| format | hi | 186 | 0.613 | 0.541-0.680 | 0.387 |
| gender_signal | hi | 203 | 0.877 | 0.825-0.915 | 0.123 |
| stat | hi | 186 | 0.446 | 0.377-0.518 | 0.554 |
| topic | hi | 203 | 0.803 | 0.743-0.852 | 0.197 |

Gates (docs/09 §6):

- format hi: 0.613 (95% CI 0.541-0.680, n=186) target 0.85 -> MISSED
- gender_signal hi: 0.877 (95% CI 0.825-0.915, n=203) target 0.98 -> MISSED
- stat hi: 0.446 (95% CI 0.377-0.518, n=186) target 0.85 -> MISSED

### a_rules on ta

- set: `C:\Users\Jabin M\OneDrive\Desktop\ICC'26\testsets\nlu_ta.csv` (210 queries). Rules are deterministic: confidence 1.0, so ECE is not meaningful for this arm.
- latency per query p50 0.2 ms, p95 0.6 ms; prediction errors 0; confident errors (conf >= 0.9) 379

| question | lang | n | accuracy | 95% CI | ECE |
|---|---|---|---|---|---|
| family | ta | 189 | 0.429 | 0.360-0.500 | 0.571 |
| format | ta | 189 | 0.577 | 0.505-0.645 | 0.423 |
| gender_signal | ta | 210 | 0.910 | 0.863-0.941 | 0.090 |
| stat | ta | 189 | 0.365 | 0.300-0.436 | 0.635 |
| topic | ta | 210 | 0.752 | 0.690-0.806 | 0.248 |

Gates (docs/09 §6):

- format ta: 0.577 (95% CI 0.505-0.645, n=189) target 0.80 -> MISSED
- gender_signal ta: 0.910 (95% CI 0.863-0.941, n=210) target 0.98 -> MISSED
- stat ta: 0.365 (95% CI 0.300-0.436, n=189) target 0.80 -> MISSED

_(a_rules wall time 0s)_

### d_shipped on en

- set: `C:\Users\Jabin M\OneDrive\Desktop\ICC'26\testsets\nlu_en.csv` (337 queries). understand(use_laya=True): rules override + Laya v2, merge policy v1; non-gender confidences reported as 1.0.
- latency per query p50 40.3 ms, p95 46.2 ms; prediction errors 0; confident errors (conf >= 0.9) 304

| question | lang | n | accuracy | 95% CI | ECE |
|---|---|---|---|---|---|
| family | en | 294 | 0.701 | 0.646-0.750 | 0.299 |
| format | en | 294 | 0.884 | 0.843-0.916 | 0.116 |
| gender_signal | en | 337 | 0.917 | 0.883-0.942 | 0.072 |
| stat | en | 294 | 0.561 | 0.504-0.617 | 0.439 |
| topic | en | 337 | 0.926 | 0.893-0.949 | 0.074 |

Gates (docs/09 §6):

- format en: 0.884 (95% CI 0.843-0.916, n=294) target 0.90 -> MISSED
- gender_signal en: 0.917 (95% CI 0.883-0.942, n=337) target 0.98 -> MISSED
- stat en: 0.561 (95% CI 0.504-0.617, n=294) target 0.90 -> MISSED

### d_shipped on hi

- set: `C:\Users\Jabin M\OneDrive\Desktop\ICC'26\testsets\nlu_hi.csv` (203 queries). understand(use_laya=True): rules override + Laya v2, merge policy v1; non-gender confidences reported as 1.0.
- latency per query p50 40.9 ms, p95 43.8 ms; prediction errors 0; confident errors (conf >= 0.9) 196

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
- latency per query p50 41.3 ms, p95 44.4 ms; prediction errors 0; confident errors (conf >= 0.9) 196

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

_(d_shipped wall time 38s)_
