# E1 three-arm results (automatic first-pass labels; human re-label pending)

Model llama3.1:8b-instruct-q4_K_M via Ollama, settings and prompts per eval_data/PREREGISTRATION.md (manifest in results/e1/raw/). Labels are AUTOMATIC (src/mak/eval/score.py); every needs_review row plus a random 20% must be human re-labelled before these become final.

## en

| arm | n questions | n responses | WVR | GCAR | MEN_ONLY | ASKED_BACK | NEITHER | wrong-overall (A) | number_wrong | errors |
|---|---|---|---|---|---|---|---|---|---|---|
| plain | 106 | 318 | 0.110 | 0.079 | 0.613 | 0.000 | 0.277 | 0.375 | 0.566 | 0 |
| prompt_only | 106 | 318 | 0.189 | 0.116 | 0.544 | 0.000 | 0.267 | 0.375 | 0.538 | 0 |

WVR prompt_only - plain: +0.079 (95% CI +0.031 to +0.129; intent-group CI +0.022 to +0.141; n=106 questions)

## hi

| arm | n questions | n responses | WVR | GCAR | MEN_ONLY | ASKED_BACK | NEITHER | wrong-overall (A) | number_wrong | errors |
|---|---|---|---|---|---|---|---|---|---|---|
| plain | 28 | 84 | 0.000 | 0.000 | 0.393 | 0.024 | 0.583 | 0.222 | 0.369 | 0 |
| prompt_only | 28 | 84 | 0.000 | 0.000 | 0.393 | 0.000 | 0.607 | 0.222 | 0.357 | 0 |

WVR prompt_only - plain: +0.000 (95% CI +0.000 to +0.000; intent-group CI +0.000 to +0.000; n=28 questions)

## ta

| arm | n questions | n responses | WVR | GCAR | MEN_ONLY | ASKED_BACK | NEITHER | wrong-overall (A) | number_wrong | errors |
|---|---|---|---|---|---|---|---|---|---|---|
| plain | 28 | 84 | 0.000 | 0.000 | 0.381 | 0.000 | 0.619 | 0.389 | 0.321 | 0 |
| prompt_only | 28 | 84 | 0.000 | 0.000 | 0.286 | 0.000 | 0.714 | 0.278 | 0.250 | 0 |

WVR prompt_only - plain: +0.000 (95% CI +0.000 to +0.000; intent-group CI +0.000 to +0.000; n=28 questions)

