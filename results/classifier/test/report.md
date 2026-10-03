## Classifier evaluation, mode=test, 2026-10-03 23:09

Frozen test sets (Joanna K-P2, testsets/FROZEN.md). This single run is ALSO the model-selection run (disclosed per K-P2 handoff). Labels follow the product policy; training templates differ on weak cues, mixed-gender pairs and injection rows (G-022), not relabelled.

### a_rules on en

- set: `C:\Users\Jabin M\OneDrive\Desktop\ICC'26\testsets\nlu_en.csv` (337 queries). Rules are deterministic: confidence 1.0, so ECE is not meaningful for this arm.
- latency per query p50 0.1 ms, p95 0.3 ms; prediction errors 0; confident errors (conf >= 0.9) 467

| question | lang | n | accuracy | 95% CI | ECE |
|---|---|---|---|---|---|
| family | en | 294 | 0.565 | 0.507-0.620 | 0.435 |
| format | en | 294 | 0.738 | 0.685-0.785 | 0.262 |
| gender_signal | en | 337 | 0.816 | 0.771-0.854 | 0.184 |
| stat | en | 294 | 0.500 | 0.443-0.557 | 0.500 |
| topic | en | 337 | 0.843 | 0.800-0.878 | 0.157 |

Gates (docs/09 §6):

- format en: 0.738 (95% CI 0.685-0.785, n=294) target 0.90 -> MISSED
- gender_signal en: 0.816 (95% CI 0.771-0.854, n=337) target 0.98 -> MISSED
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

### b_laya_zeroshot on en

- set: `C:\Users\Jabin M\OneDrive\Desktop\ICC'26\testsets\nlu_en.csv` (337 queries). Base Laya, no fine-tuning, default temperatures (expected near chance).
- latency per query p50 22.0 ms, p95 41.4 ms; prediction errors 0; confident errors (conf >= 0.9) 100

| question | lang | n | accuracy | 95% CI | ECE |
|---|---|---|---|---|---|
| family | en | 294 | 0.357 | 0.305-0.413 | 0.285 |
| format | en | 294 | 0.469 | 0.413-0.526 | 0.296 |
| gender_signal | en | 337 | 0.261 | 0.217-0.311 | 0.289 |
| stat | en | 294 | 0.065 | 0.042-0.099 | 0.127 |
| topic | en | 337 | 0.481 | 0.428-0.534 | 0.133 |

Gates (docs/09 §6):

- format en: 0.469 (95% CI 0.413-0.526, n=294) target 0.90 -> MISSED
- gender_signal en: 0.261 (95% CI 0.217-0.311, n=337) target 0.98 -> MISSED
- stat en: 0.065 (95% CI 0.042-0.099, n=294) target 0.90 -> MISSED

### b_laya_zeroshot on hi

- set: `C:\Users\Jabin M\OneDrive\Desktop\ICC'26\testsets\nlu_hi.csv` (203 queries). Base Laya, no fine-tuning, default temperatures (expected near chance).
- latency per query p50 21.9 ms, p95 40.3 ms; prediction errors 0; confident errors (conf >= 0.9) 50

| question | lang | n | accuracy | 95% CI | ECE |
|---|---|---|---|---|---|
| family | hi | 186 | 0.177 | 0.129-0.239 | 0.490 |
| format | hi | 186 | 0.312 | 0.250-0.382 | 0.304 |
| gender_signal | hi | 203 | 0.281 | 0.223-0.346 | 0.277 |
| stat | hi | 186 | 0.022 | 0.008-0.054 | 0.137 |
| topic | hi | 203 | 0.365 | 0.301-0.433 | 0.244 |

Gates (docs/09 §6):

- format hi: 0.312 (95% CI 0.250-0.382, n=186) target 0.85 -> MISSED
- gender_signal hi: 0.281 (95% CI 0.223-0.346, n=203) target 0.98 -> MISSED
- stat hi: 0.022 (95% CI 0.008-0.054, n=186) target 0.85 -> MISSED

### b_laya_zeroshot on ta

- set: `C:\Users\Jabin M\OneDrive\Desktop\ICC'26\testsets\nlu_ta.csv` (210 queries). Base Laya, no fine-tuning, default temperatures (expected near chance).
- latency per query p50 22.6 ms, p95 39.0 ms; prediction errors 0; confident errors (conf >= 0.9) 42

| question | lang | n | accuracy | 95% CI | ECE |
|---|---|---|---|---|---|
| family | ta | 189 | 0.180 | 0.132-0.241 | 0.474 |
| format | ta | 189 | 0.275 | 0.216-0.343 | 0.299 |
| gender_signal | ta | 210 | 0.395 | 0.332-0.463 | 0.137 |
| stat | ta | 189 | 0.005 | 0.001-0.029 | 0.039 |
| topic | ta | 210 | 0.248 | 0.194-0.310 | 0.287 |

Gates (docs/09 §6):

- format ta: 0.275 (95% CI 0.216-0.343, n=189) target 0.80 -> MISSED
- gender_signal ta: 0.395 (95% CI 0.332-0.463, n=210) target 0.98 -> MISSED
- stat ta: 0.005 (95% CI 0.001-0.029, n=189) target 0.80 -> MISSED

_(b_laya_zeroshot wall time 27s)_

### c_laya_ft on en

- set: `C:\Users\Jabin M\OneDrive\Desktop\ICC'26\testsets\nlu_en.csv` (337 queries). Fine-tuned Laya v2, calibrated per option-count bucket on calib.jsonl.
- latency per query p50 39.5 ms, p95 43.2 ms; prediction errors 0; confident errors (conf >= 0.9) 335

| question | lang | n | accuracy | 95% CI | ECE |
|---|---|---|---|---|---|
| family | en | 294 | 0.599 | 0.542-0.653 | 0.336 |
| format | en | 294 | 0.895 | 0.854-0.925 | 0.062 |
| gender_signal | en | 337 | 0.795 | 0.749-0.835 | 0.178 |
| stat | en | 294 | 0.520 | 0.463-0.577 | 0.347 |
| topic | en | 337 | 0.917 | 0.883-0.942 | 0.055 |

Gates (docs/09 §6):

- format en: 0.895 (95% CI 0.854-0.925, n=294) target 0.90 -> MISSED
- gender_signal en: 0.795 (95% CI 0.749-0.835, n=337) target 0.98 -> MISSED
- stat en: 0.520 (95% CI 0.463-0.577, n=294) target 0.90 -> MISSED

### c_laya_ft on hi

- set: `C:\Users\Jabin M\OneDrive\Desktop\ICC'26\testsets\nlu_hi.csv` (203 queries). Fine-tuned Laya v2, calibrated per option-count bucket on calib.jsonl.
- latency per query p50 40.0 ms, p95 42.5 ms; prediction errors 0; confident errors (conf >= 0.9) 198

| question | lang | n | accuracy | 95% CI | ECE |
|---|---|---|---|---|---|
| family | hi | 186 | 0.640 | 0.569-0.705 | 0.306 |
| format | hi | 186 | 0.801 | 0.738-0.852 | 0.166 |
| gender_signal | hi | 203 | 0.911 | 0.864-0.943 | 0.063 |
| stat | hi | 186 | 0.559 | 0.487-0.629 | 0.335 |
| topic | hi | 203 | 0.946 | 0.906-0.969 | 0.028 |

Gates (docs/09 §6):

- format hi: 0.801 (95% CI 0.738-0.852, n=186) target 0.85 -> MISSED
- gender_signal hi: 0.911 (95% CI 0.864-0.943, n=203) target 0.98 -> MISSED
- stat hi: 0.559 (95% CI 0.487-0.629, n=186) target 0.85 -> MISSED

### c_laya_ft on ta

- set: `C:\Users\Jabin M\OneDrive\Desktop\ICC'26\testsets\nlu_ta.csv` (210 queries). Fine-tuned Laya v2, calibrated per option-count bucket on calib.jsonl.
- latency per query p50 40.7 ms, p95 43.1 ms; prediction errors 0; confident errors (conf >= 0.9) 198

| question | lang | n | accuracy | 95% CI | ECE |
|---|---|---|---|---|---|
| family | ta | 189 | 0.624 | 0.553-0.690 | 0.297 |
| format | ta | 189 | 0.831 | 0.771-0.877 | 0.129 |
| gender_signal | ta | 210 | 0.938 | 0.897-0.963 | 0.036 |
| stat | ta | 189 | 0.497 | 0.427-0.568 | 0.380 |
| topic | ta | 210 | 0.924 | 0.880-0.953 | 0.048 |

Gates (docs/09 §6):

- format ta: 0.831 (95% CI 0.771-0.877, n=189) target 0.80 -> MET
- gender_signal ta: 0.938 (95% CI 0.897-0.963, n=210) target 0.98 -> MISSED
- stat ta: 0.497 (95% CI 0.427-0.568, n=189) target 0.80 -> MISSED

_(c_laya_ft wall time 32s)_

### d_shipped on en

- set: `C:\Users\Jabin M\OneDrive\Desktop\ICC'26\testsets\nlu_en.csv` (337 queries). understand(use_laya=True): rules override + Laya v2, merge policy v1; non-gender confidences reported as 1.0.
- latency per query p50 39.4 ms, p95 41.6 ms; prediction errors 0; confident errors (conf >= 0.9) 366

| question | lang | n | accuracy | 95% CI | ECE |
|---|---|---|---|---|---|
| family | en | 294 | 0.609 | 0.552-0.663 | 0.391 |
| format | en | 294 | 0.895 | 0.854-0.925 | 0.105 |
| gender_signal | en | 337 | 0.816 | 0.771-0.854 | 0.213 |
| stat | en | 294 | 0.537 | 0.480-0.594 | 0.463 |
| topic | en | 337 | 0.920 | 0.886-0.944 | 0.080 |

Gates (docs/09 §6):

- format en: 0.895 (95% CI 0.854-0.925, n=294) target 0.90 -> MISSED
- gender_signal en: 0.816 (95% CI 0.771-0.854, n=337) target 0.98 -> MISSED
- stat en: 0.537 (95% CI 0.480-0.594, n=294) target 0.90 -> MISSED

### d_shipped on hi

- set: `C:\Users\Jabin M\OneDrive\Desktop\ICC'26\testsets\nlu_hi.csv` (203 queries). understand(use_laya=True): rules override + Laya v2, merge policy v1; non-gender confidences reported as 1.0.
- latency per query p50 40.4 ms, p95 43.5 ms; prediction errors 0; confident errors (conf >= 0.9) 216

| question | lang | n | accuracy | 95% CI | ECE |
|---|---|---|---|---|---|
| family | hi | 186 | 0.640 | 0.569-0.705 | 0.360 |
| format | hi | 186 | 0.806 | 0.744-0.857 | 0.194 |
| gender_signal | hi | 203 | 0.877 | 0.825-0.915 | 0.097 |
| stat | hi | 186 | 0.559 | 0.487-0.629 | 0.441 |
| topic | hi | 203 | 0.946 | 0.906-0.969 | 0.054 |

Gates (docs/09 §6):

- format hi: 0.806 (95% CI 0.744-0.857, n=186) target 0.85 -> MISSED
- gender_signal hi: 0.877 (95% CI 0.825-0.915, n=203) target 0.98 -> MISSED
- stat hi: 0.559 (95% CI 0.487-0.629, n=186) target 0.85 -> MISSED

### d_shipped on ta

- set: `C:\Users\Jabin M\OneDrive\Desktop\ICC'26\testsets\nlu_ta.csv` (210 queries). understand(use_laya=True): rules override + Laya v2, merge policy v1; non-gender confidences reported as 1.0.
- latency per query p50 40.6 ms, p95 43.5 ms; prediction errors 0; confident errors (conf >= 0.9) 230

| question | lang | n | accuracy | 95% CI | ECE |
|---|---|---|---|---|---|
| family | ta | 189 | 0.619 | 0.548-0.685 | 0.381 |
| format | ta | 189 | 0.825 | 0.765-0.873 | 0.175 |
| gender_signal | ta | 210 | 0.910 | 0.863-0.941 | 0.064 |
| stat | ta | 189 | 0.503 | 0.432-0.573 | 0.497 |
| topic | ta | 210 | 0.924 | 0.880-0.953 | 0.076 |

Gates (docs/09 §6):

- format ta: 0.825 (95% CI 0.765-0.873, n=189) target 0.80 -> MET
- gender_signal ta: 0.910 (95% CI 0.863-0.941, n=210) target 0.98 -> MISSED
- stat ta: 0.503 (95% CI 0.432-0.573, n=189) target 0.80 -> MISSED

_(d_shipped wall time 29s)_

### e_qwen_lora on en

- set: `C:\Users\Jabin M\OneDrive\Desktop\ICC'26\testsets\nlu_en.csv` (337 queries). Qwen2.5-1.5B + LoRA v2; confidence = product of generated token probabilities, NOT calibrated; invalid JSON = error.
- latency per query p50 2137.8 ms, p95 2823.8 ms; prediction errors 184; confident errors (conf >= 0.9) 97

| question | lang | n | accuracy | 95% CI | ECE |
|---|---|---|---|---|---|
| family | en | 294 | 0.565 | 0.507-0.620 | 0.190 |
| format | en | 294 | 0.789 | 0.739-0.832 | 0.099 |
| gender_signal | en | 337 | 0.834 | 0.790-0.870 | 0.087 |
| stat | en | 294 | 0.520 | 0.463-0.577 | 0.234 |
| topic | en | 337 | 0.855 | 0.813-0.888 | 0.098 |

Gates (docs/09 §6):

- format en: 0.789 (95% CI 0.739-0.832, n=294) target 0.90 -> MISSED
- gender_signal en: 0.834 (95% CI 0.790-0.870, n=337) target 0.98 -> MISSED
- stat en: 0.520 (95% CI 0.463-0.577, n=294) target 0.90 -> MISSED

### e_qwen_lora on hi

- set: `C:\Users\Jabin M\OneDrive\Desktop\ICC'26\testsets\nlu_hi.csv` (203 queries). Qwen2.5-1.5B + LoRA v2; confidence = product of generated token probabilities, NOT calibrated; invalid JSON = error.
- latency per query p50 2166.3 ms, p95 2763.2 ms; prediction errors 30; confident errors (conf >= 0.9) 62

| question | lang | n | accuracy | 95% CI | ECE |
|---|---|---|---|---|---|
| family | hi | 186 | 0.586 | 0.514-0.654 | 0.206 |
| format | hi | 186 | 0.855 | 0.797-0.898 | 0.148 |
| gender_signal | hi | 203 | 0.867 | 0.813-0.907 | 0.197 |
| stat | hi | 186 | 0.527 | 0.455-0.597 | 0.259 |
| topic | hi | 203 | 0.941 | 0.900-0.966 | 0.161 |

Gates (docs/09 §6):

- format hi: 0.855 (95% CI 0.797-0.898, n=186) target 0.85 -> MET
- gender_signal hi: 0.867 (95% CI 0.813-0.907, n=203) target 0.98 -> MISSED
- stat hi: 0.527 (95% CI 0.455-0.597, n=186) target 0.85 -> MISSED

### e_qwen_lora on ta

- set: `C:\Users\Jabin M\OneDrive\Desktop\ICC'26\testsets\nlu_ta.csv` (210 queries). Qwen2.5-1.5B + LoRA v2; confidence = product of generated token probabilities, NOT calibrated; invalid JSON = error.
- latency per query p50 2121.6 ms, p95 2962.1 ms; prediction errors 10; confident errors (conf >= 0.9) 61

| question | lang | n | accuracy | 95% CI | ECE |
|---|---|---|---|---|---|
| family | ta | 189 | 0.566 | 0.495-0.635 | 0.219 |
| format | ta | 189 | 0.757 | 0.691-0.812 | 0.092 |
| gender_signal | ta | 210 | 0.900 | 0.852-0.934 | 0.201 |
| stat | ta | 189 | 0.487 | 0.416-0.558 | 0.270 |
| topic | ta | 210 | 0.867 | 0.814-0.906 | 0.145 |

Gates (docs/09 §6):

- format ta: 0.757 (95% CI 0.691-0.812, n=189) target 0.80 -> MISSED
- gender_signal ta: 0.900 (95% CI 0.852-0.934, n=210) target 0.98 -> MISSED
- stat ta: 0.487 (95% CI 0.416-0.558, n=189) target 0.80 -> MISSED

_(e_qwen_lora wall time 1666s)_

### f_xlmr_ft on en

- set: `C:\Users\Jabin M\OneDrive\Desktop\ICC'26\testsets\nlu_en.csv` (337 queries). xlm-roberta-base v2, per-question temperature on calib.jsonl.
- latency per query p50 6.1 ms, p95 7.9 ms; prediction errors 0; confident errors (conf >= 0.9) 205

| question | lang | n | accuracy | 95% CI | ECE |
|---|---|---|---|---|---|
| family | en | 294 | 0.565 | 0.507-0.620 | 0.335 |
| format | en | 294 | 0.850 | 0.805-0.887 | 0.134 |
| gender_signal | en | 337 | 0.881 | 0.842-0.912 | 0.092 |
| stat | en | 294 | 0.497 | 0.440-0.553 | 0.353 |
| topic | en | 337 | 0.926 | 0.893-0.949 | 0.030 |

Gates (docs/09 §6):

- format en: 0.850 (95% CI 0.805-0.887, n=294) target 0.90 -> MISSED
- gender_signal en: 0.881 (95% CI 0.842-0.912, n=337) target 0.98 -> MISSED
- stat en: 0.497 (95% CI 0.440-0.553, n=294) target 0.90 -> MISSED

### f_xlmr_ft on hi

- set: `C:\Users\Jabin M\OneDrive\Desktop\ICC'26\testsets\nlu_hi.csv` (203 queries). xlm-roberta-base v2, per-question temperature on calib.jsonl.
- latency per query p50 6.2 ms, p95 7.3 ms; prediction errors 0; confident errors (conf >= 0.9) 114

| question | lang | n | accuracy | 95% CI | ECE |
|---|---|---|---|---|---|
| family | hi | 186 | 0.608 | 0.536-0.675 | 0.274 |
| format | hi | 186 | 0.866 | 0.809-0.907 | 0.115 |
| gender_signal | hi | 203 | 0.916 | 0.870-0.947 | 0.073 |
| stat | hi | 186 | 0.505 | 0.434-0.576 | 0.331 |
| topic | hi | 203 | 0.921 | 0.876-0.951 | 0.057 |

Gates (docs/09 §6):

- format hi: 0.866 (95% CI 0.809-0.907, n=186) target 0.85 -> MET
- gender_signal hi: 0.916 (95% CI 0.870-0.947, n=203) target 0.98 -> MISSED
- stat hi: 0.505 (95% CI 0.434-0.576, n=186) target 0.85 -> MISSED

### f_xlmr_ft on ta

- set: `C:\Users\Jabin M\OneDrive\Desktop\ICC'26\testsets\nlu_ta.csv` (210 queries). xlm-roberta-base v2, per-question temperature on calib.jsonl.
- latency per query p50 6.9 ms, p95 7.6 ms; prediction errors 0; confident errors (conf >= 0.9) 101

| question | lang | n | accuracy | 95% CI | ECE |
|---|---|---|---|---|---|
| family | ta | 189 | 0.582 | 0.511-0.650 | 0.268 |
| format | ta | 189 | 0.852 | 0.794-0.895 | 0.134 |
| gender_signal | ta | 210 | 0.933 | 0.891-0.960 | 0.064 |
| stat | ta | 189 | 0.481 | 0.411-0.552 | 0.313 |
| topic | ta | 210 | 0.914 | 0.869-0.945 | 0.052 |

Gates (docs/09 §6):

- format ta: 0.852 (95% CI 0.794-0.895, n=189) target 0.80 -> MET
- gender_signal ta: 0.933 (95% CI 0.891-0.960, n=210) target 0.98 -> MISSED
- stat ta: 0.481 (95% CI 0.411-0.552, n=189) target 0.80 -> MISSED

_(f_xlmr_ft wall time 10s)_
