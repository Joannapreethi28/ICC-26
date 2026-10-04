# E1 three-arm results (automatic first-pass labels; human re-label pending)

Model llama3.1:8b-instruct-q4_K_M via Ollama, settings and prompts per eval_data/PREREGISTRATION.md (manifest in results/e1/raw/). Labels are AUTOMATIC (src/mak/eval/score.py); every needs_review row plus a random 20% must be human re-labelled before these become final.

## en

| arm | n questions | n responses | WVR | GCAR | MEN_ONLY | ASKED_BACK | NEITHER | wrong-overall (A) | number_wrong | errors |
|---|---|---|---|---|---|---|---|---|---|---|
| plain | 106 | 318 | 0.110 | 0.079 | 0.613 | 0.000 | 0.277 | 0.375 | 0.566 | 0 |
| prompt_only | 106 | 318 | 0.189 | 0.116 | 0.544 | 0.000 | 0.267 | 0.375 | 0.538 | 0 |
| layer | 106 | 318 | 0.528 | 0.459 | 0.308 | 0.000 | 0.164 | 0.125 | 0.173 | 0 |
| layer_text | 106 | 106 | 0.708 | 0.708 | 0.009 | 0.000 | 0.283 | 0.021 | 0.104 | 0 |

WVR prompt_only - plain: +0.079 (95% CI +0.031 to +0.129; intent-group CI +0.022 to +0.141; n=106 questions)
WVR layer - plain: +0.418 (95% CI +0.324 to +0.516; intent-group CI +0.287 to +0.547; n=106 questions)
WVR layer - prompt_only: +0.340 (95% CI +0.236 to +0.440; intent-group CI +0.194 to +0.478; n=106 questions)

## hi

| arm | n questions | n responses | WVR | GCAR | MEN_ONLY | ASKED_BACK | NEITHER | wrong-overall (A) | number_wrong | errors |
|---|---|---|---|---|---|---|---|---|---|---|
| plain | 28 | 84 | 0.000 | 0.000 | 0.393 | 0.024 | 0.583 | 0.222 | 0.369 | 0 |
| prompt_only | 28 | 84 | 0.000 | 0.000 | 0.393 | 0.000 | 0.607 | 0.222 | 0.357 | 0 |
| layer | 28 | 84 | 0.643 | 0.238 | 0.167 | 0.000 | 0.190 | 0.000 | 0.048 | 0 |
| layer_text | 28 | 28 | 0.893 | 0.893 | 0.000 | 0.000 | 0.107 | 0.000 | 0.071 | 0 |

WVR prompt_only - plain: +0.000 (95% CI +0.000 to +0.000; intent-group CI +0.000 to +0.000; n=28 questions)
WVR layer - plain: +0.643 (95% CI +0.476 to +0.798; intent-group CI +0.448 to +0.833; n=28 questions)
WVR layer - prompt_only: +0.643 (95% CI +0.476 to +0.798; intent-group CI +0.448 to +0.833; n=28 questions)

## ta

| arm | n questions | n responses | WVR | GCAR | MEN_ONLY | ASKED_BACK | NEITHER | wrong-overall (A) | number_wrong | errors |
|---|---|---|---|---|---|---|---|---|---|---|
| plain | 28 | 84 | 0.000 | 0.000 | 0.381 | 0.000 | 0.619 | 0.389 | 0.321 | 0 |
| prompt_only | 28 | 84 | 0.000 | 0.000 | 0.286 | 0.000 | 0.714 | 0.278 | 0.250 | 0 |
| layer | 28 | 84 | 0.429 | 0.107 | 0.155 | 0.000 | 0.417 | 0.028 | 0.202 | 0 |
| layer_text | 28 | 28 | 0.750 | 0.714 | 0.000 | 0.000 | 0.250 | 0.000 | 0.179 | 0 |

WVR prompt_only - plain: +0.000 (95% CI +0.000 to +0.000; intent-group CI +0.000 to +0.000; n=28 questions)
WVR layer - plain: +0.429 (95% CI +0.262 to +0.607; intent-group CI +0.250 to +0.628; n=28 questions)
WVR layer - prompt_only: +0.429 (95% CI +0.262 to +0.607; intent-group CI +0.250 to +0.628; n=28 questions)

