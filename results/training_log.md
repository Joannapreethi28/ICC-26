
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
