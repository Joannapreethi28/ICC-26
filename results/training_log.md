
## Laya fine-tune run, 2026-10-03 20:43

- base: convaiinnovations/laya-multilingual (local cache, offline); data: training/data/train.jsonl (47804 sequences), calibration: calib.jsonl (13184 sequences); see training/DATA_FROZEN.md for hashes
- epochs 3, micro-batch 8 x accum 4 (effective 32), LR encoder 2.5e-05 / head 0.0001, AdamW wd 0.01, cosine to 1e-6, grad clip 1.0, bf16, max_len 512, head_max_len 256, reward group 4, sigma 0.4->0.1, seed 20261003
- wall time 3334s on NVIDIA GeForce RTX 5060 Laptop GPU, peak GPU 6.51 GB
- zero-shot accuracy per question on first 600 calib sequences (MEASURED): family=0.30, format=0.45, gender_signal=0.41, stat_career_record=0.49, stat_firsts_history=0.43, stat_player_stat=0.94, stat_role_or_ranking=1.00, stat_team_record=1.00, stat_world_cup_record=0.47, topic=0.44
- fitted temperatures (clamped 0.5-5.0): {"choice:3-5": 3.914, "choice:6-10": 4.141, "choice:11+": 4.987, "choice:2": 3.202}

Calibration-set results (MEASURED on template-disjoint calibration data, NOT the frozen test sets; this is not the headline accuracy):

| lang | question | n | accuracy | ECE before | ECE after |
|---|---|---|---|---|---|
| en | family | 808 | 0.896 | 0.104 | 0.050 |
| en | format | 808 | 1.000 | 0.000 | 0.043 |
| en | gender_signal | 997 | 0.998 | 0.002 | 0.017 |
| en | stat_career_record | 297 | 0.687 | 0.314 | 0.161 |
| en | stat_firsts_history | 57 | 0.947 | 0.053 | 0.038 |
| en | stat_player_stat | 95 | 1.000 | 0.000 | 0.002 |
| en | stat_role_or_ranking | 61 | 1.000 | 0.000 | 0.002 |
| en | stat_team_record | 79 | 0.987 | 0.013 | 0.032 |
| en | stat_world_cup_record | 129 | 1.000 | 0.000 | 0.040 |
| en | topic | 997 | 0.966 | 0.034 | 0.016 |
| hi | family | 834 | 0.926 | 0.074 | 0.022 |
| hi | format | 834 | 0.993 | 0.007 | 0.036 |
| hi | gender_signal | 992 | 0.998 | 0.002 | 0.017 |
| hi | stat_career_record | 315 | 0.921 | 0.078 | 0.083 |
| hi | stat_firsts_history | 60 | 1.000 | 0.000 | 0.013 |
| hi | stat_player_stat | 103 | 0.990 | 0.010 | 0.008 |
| hi | stat_role_or_ranking | 60 | 1.000 | 0.000 | 0.002 |
| hi | stat_team_record | 96 | 0.844 | 0.153 | 0.133 |
| hi | stat_world_cup_record | 128 | 0.945 | 0.055 | 0.013 |
| hi | topic | 992 | 0.988 | 0.012 | 0.011 |
| ta | family | 844 | 0.857 | 0.141 | 0.082 |
| ta | format | 844 | 0.995 | 0.005 | 0.038 |
| ta | gender_signal | 992 | 0.987 | 0.013 | 0.007 |
| ta | stat_career_record | 324 | 0.867 | 0.124 | 0.078 |
| ta | stat_firsts_history | 67 | 0.716 | 0.281 | 0.266 |
| ta | stat_player_stat | 106 | 1.000 | 0.000 | 0.002 |
| ta | stat_role_or_ranking | 51 | 1.000 | 0.000 | 0.002 |
| ta | stat_team_record | 92 | 0.924 | 0.052 | 0.018 |
| ta | stat_world_cup_record | 130 | 0.962 | 0.038 | 0.003 |
| ta | topic | 992 | 0.962 | 0.038 | 0.020 |

Overall accuracy per language (all questions, calibration set): en=0.950, hi=0.971, ta=0.944

## xlmr-mak-v1 (FacebookAI/xlm-roberta-base) run, 2026-10-03 20:48

- epochs 3, batch 16x2, LR enc 3e-05 head 0.001, max_len 128, seed 20261003, wall 247s
- temperatures per question: {"gender_signal": 1.178, "topic": 1.696, "family": 1.857, "format": 0.9, "stat_career_record": 2.016, "stat_role_or_ranking": 0.5, "stat_player_stat": 0.995, "stat_world_cup_record": 1.977, "stat_firsts_history": 1.338, "stat_team_record": 2.014}

Calibration-set results (MEASURED, template-disjoint calib data; NOT headline test accuracy):

| lang | question | n | accuracy | ECE before | ECE after |
|---|---|---|---|---|---|
| en | gender_signal | 997 | 0.996 | 0.004 | 0.007 |
| en | topic | 997 | 0.945 | 0.036 | 0.022 |
| en | family | 808 | 0.863 | 0.059 | 0.048 |
| en | format | 808 | 0.981 | 0.006 | 0.006 |
| en | stat_career_record | 297 | 0.562 | 0.223 | 0.120 |
| en | stat_role_or_ranking | 61 | 1.000 | 0.002 | 0.000 |
| en | stat_player_stat | 95 | 1.000 | 0.000 | 0.000 |
| en | stat_world_cup_record | 129 | 1.000 | 0.008 | 0.083 |
| en | stat_firsts_history | 57 | 0.947 | 0.043 | 0.053 |
| en | stat_team_record | 79 | 1.000 | 0.010 | 0.083 |
| hi | gender_signal | 992 | 0.988 | 0.011 | 0.009 |
| hi | topic | 992 | 0.935 | 0.043 | 0.020 |
| hi | family | 834 | 0.910 | 0.052 | 0.040 |
| hi | format | 834 | 0.998 | 0.007 | 0.005 |
| hi | stat_career_record | 315 | 0.863 | 0.071 | 0.120 |
| hi | stat_role_or_ranking | 60 | 1.000 | 0.000 | 0.000 |
| hi | stat_player_stat | 103 | 1.000 | 0.000 | 0.000 |
| hi | stat_world_cup_record | 128 | 0.875 | 0.130 | 0.084 |
| hi | stat_firsts_history | 60 | 0.833 | 0.088 | 0.083 |
| hi | stat_team_record | 96 | 0.823 | 0.127 | 0.128 |
| ta | gender_signal | 992 | 0.988 | 0.009 | 0.008 |
| ta | topic | 992 | 0.955 | 0.033 | 0.017 |
| ta | family | 844 | 0.845 | 0.096 | 0.044 |
| ta | format | 844 | 0.994 | 0.002 | 0.002 |
| ta | stat_career_record | 324 | 0.827 | 0.120 | 0.060 |
| ta | stat_role_or_ranking | 51 | 1.000 | 0.003 | 0.001 |
| ta | stat_player_stat | 106 | 1.000 | 0.000 | 0.000 |
| ta | stat_world_cup_record | 130 | 0.823 | 0.136 | 0.076 |
| ta | stat_firsts_history | 67 | 0.851 | 0.096 | 0.069 |
| ta | stat_team_record | 92 | 0.750 | 0.172 | 0.121 |

Overall accuracy per language (calibration set): en=0.927, hi=0.946, ta=0.931

## Laya fine-tune run, 2026-10-03 22:05

- base: convaiinnovations/laya-multilingual (local cache, offline); data: training/data/train.jsonl (48067 sequences), calibration: calib.jsonl (13236 sequences); see training/DATA_FROZEN.md for hashes
- epochs 2, micro-batch 8 x accum 4 (effective 32), LR encoder 2.5e-05 / head 0.0001, AdamW wd 0.01, cosine to 1e-6, grad clip 1.0, bf16, max_len 512, head_max_len 256, reward group 4, sigma 0.4->0.1, seed 20261003, label smoothing 0.05 (CE only), text lowercased (normalise_for_model), out laya-mak-v2
- wall time 2121s on NVIDIA GeForce RTX 5060 Laptop GPU, peak GPU 6.51 GB
- zero-shot accuracy per question on first 600 calib sequences (MEASURED): family=0.29, format=0.36, gender_signal=0.40, stat_career_record=0.61, stat_firsts_history=1.00, stat_player_stat=0.76, stat_role_or_ranking=1.00, stat_team_record=0.83, stat_world_cup_record=0.40, topic=0.41
- fitted temperatures (clamped 0.5-5.0): {"choice:3-5": 3.817, "choice:6-10": 3.771, "choice:11+": 3.938, "choice:2": 4.114}

Calibration-set results (MEASURED on template-disjoint calibration data, NOT the frozen test sets; this is not the headline accuracy):

| lang | question | n | accuracy | ECE before | ECE after |
|---|---|---|---|---|---|
| en | family | 820 | 0.898 | 0.098 | 0.048 |
| en | format | 820 | 0.999 | 0.001 | 0.041 |
| en | gender_signal | 997 | 0.999 | 0.001 | 0.025 |
| en | stat_career_record | 309 | 0.945 | 0.055 | 0.022 |
| en | stat_firsts_history | 65 | 0.677 | 0.343 | 0.324 |
| en | stat_player_stat | 104 | 1.000 | 0.000 | 0.014 |
| en | stat_role_or_ranking | 47 | 1.000 | 0.000 | 0.014 |
| en | stat_team_record | 72 | 1.000 | 0.000 | 0.032 |
| en | stat_world_cup_record | 134 | 1.000 | 0.000 | 0.040 |
| en | topic | 997 | 0.945 | 0.053 | 0.026 |
| hi | family | 847 | 0.903 | 0.088 | 0.041 |
| hi | format | 847 | 0.999 | 0.001 | 0.041 |
| hi | gender_signal | 992 | 0.988 | 0.011 | 0.018 |
| hi | stat_career_record | 337 | 0.929 | 0.069 | 0.016 |
| hi | stat_firsts_history | 63 | 1.000 | 0.000 | 0.019 |
| hi | stat_player_stat | 100 | 0.990 | 0.010 | 0.004 |
| hi | stat_role_or_ranking | 68 | 1.000 | 0.000 | 0.014 |
| hi | stat_team_record | 82 | 1.000 | 0.000 | 0.032 |
| hi | stat_world_cup_record | 125 | 1.000 | 0.028 | 0.066 |
| hi | topic | 992 | 0.986 | 0.010 | 0.022 |
| ta | family | 838 | 0.875 | 0.116 | 0.065 |
| ta | format | 838 | 0.995 | 0.005 | 0.038 |
| ta | gender_signal | 993 | 0.969 | 0.031 | 0.005 |
| ta | stat_career_record | 316 | 0.851 | 0.133 | 0.054 |
| ta | stat_firsts_history | 63 | 0.905 | 0.091 | 0.050 |
| ta | stat_player_stat | 114 | 0.947 | 0.054 | 0.047 |
| ta | stat_role_or_ranking | 54 | 1.000 | 0.011 | 0.030 |
| ta | stat_team_record | 92 | 0.815 | 0.180 | 0.152 |
| ta | stat_world_cup_record | 117 | 0.974 | 0.026 | 0.015 |
| ta | topic | 993 | 0.966 | 0.036 | 0.010 |

Overall accuracy per language (all questions, calibration set): en=0.959, hi=0.970, ta=0.943

## xlmr-mak-v2 (FacebookAI/xlm-roberta-base) run, 2026-10-03 22:09

- epochs 3, batch 16x2, LR enc 3e-05 head 0.001, max_len 128, seed 20261003, wall 228s
- temperatures per question: {"gender_signal": 0.964, "topic": 1.727, "family": 1.576, "format": 0.795, "stat_career_record": 1.481, "stat_role_or_ranking": 0.5, "stat_team_record": 0.834, "stat_world_cup_record": 1.581, "stat_player_stat": 0.5, "stat_firsts_history": 2.64}

Calibration-set results (MEASURED, template-disjoint calib data; NOT headline test accuracy):

| lang | question | n | accuracy | ECE before | ECE after |
|---|---|---|---|---|---|
| en | gender_signal | 997 | 1.000 | 0.003 | 0.002 |
| en | topic | 997 | 0.969 | 0.020 | 0.015 |
| en | family | 820 | 0.917 | 0.020 | 0.044 |
| en | format | 820 | 0.999 | 0.006 | 0.003 |
| en | stat_career_record | 309 | 0.819 | 0.095 | 0.075 |
| en | stat_role_or_ranking | 47 | 1.000 | 0.001 | 0.000 |
| en | stat_team_record | 72 | 1.000 | 0.008 | 0.005 |
| en | stat_world_cup_record | 134 | 1.000 | 0.004 | 0.032 |
| en | stat_player_stat | 104 | 1.000 | 0.000 | 0.000 |
| en | stat_firsts_history | 65 | 0.615 | 0.335 | 0.269 |
| hi | gender_signal | 992 | 0.997 | 0.004 | 0.004 |
| hi | topic | 992 | 0.958 | 0.024 | 0.013 |
| hi | family | 847 | 0.911 | 0.065 | 0.045 |
| hi | format | 847 | 0.999 | 0.002 | 0.001 |
| hi | stat_career_record | 337 | 0.878 | 0.056 | 0.051 |
| hi | stat_role_or_ranking | 68 | 1.000 | 0.000 | 0.000 |
| hi | stat_team_record | 82 | 0.939 | 0.041 | 0.056 |
| hi | stat_world_cup_record | 125 | 0.824 | 0.115 | 0.080 |
| hi | stat_player_stat | 100 | 1.000 | 0.000 | 0.000 |
| hi | stat_firsts_history | 63 | 0.730 | 0.217 | 0.201 |
| ta | gender_signal | 993 | 0.991 | 0.005 | 0.005 |
| ta | topic | 993 | 0.922 | 0.057 | 0.027 |
| ta | family | 838 | 0.872 | 0.061 | 0.036 |
| ta | format | 838 | 0.999 | 0.001 | 0.001 |
| ta | stat_career_record | 316 | 0.870 | 0.062 | 0.040 |
| ta | stat_role_or_ranking | 54 | 1.000 | 0.001 | 0.000 |
| ta | stat_team_record | 92 | 0.978 | 0.040 | 0.022 |
| ta | stat_world_cup_record | 117 | 0.906 | 0.067 | 0.082 |
| ta | stat_player_stat | 114 | 1.000 | 0.000 | 0.000 |
| ta | stat_firsts_history | 63 | 0.841 | 0.127 | 0.127 |

Overall accuracy per language (calibration set): en=0.959, hi=0.954, ta=0.942

## Qwen LoRA parser run, 2026-10-03 22:56

- base Qwen/Qwen2.5-1.5B-Instruct@989aa7980e4c, LoRA r=16 alpha=32 dropout 0.05 on all attention+MLP projections, epochs 1.0, batch 8x4, LR 2e-4 cosine, bf16, completion-only loss, seed 20261003; 10760 train rows; wall 2764s, peak GPU 4.74 GB, final train loss 0.013475590924092805
