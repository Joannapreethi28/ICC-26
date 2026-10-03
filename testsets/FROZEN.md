# K-P2 test sets FROZEN — v1, 3 October 2026

Joanna/Astra: one reviewer, same-agent semantic self-review. No independent agreement
or human/native-speaker validation is claimed. No project evaluation outputs inspected.

Training firewall: Jabin may read these inputs only after publishing `training/DATA_FROZEN.md`.

| File | Rows | SHA-256 (UTF-8, LF) |
|---|---:|---|
| `testsets/nlu_en.csv` | 337 | `18e1a05b5a23feae870d024e02d86dc76663d9aa0d1808c9b772a53bd4da2c4a` |
| `testsets/nlu_hi.csv` | 203 | `4555f1ba80beead6a2e464917fd8957b9d895285a478f48e6e7abd93d59df240` |
| `testsets/nlu_ta.csv` | 210 | `ea8d7dd8fc61dbe5d5f8ff55cbe373c15f5b8574cca28b528186d38c6cf86168` |
| `testsets/xsport.csv` | 60 | `8a151f3cb0a5ca6f2471d7089656a6f64b5d2aa69f75469ecbe6e31a8b0cb220` |
| `eval_data/benchmark_v1.csv` | 188 | `3487b18ea3358bde1f8ee314fa3c638531589a3697093b7481cca93e34c6a076` |
| `eval_data/provenance_v1.jsonl` | 998 | `7d3e857e9f56ef9a4a3cbb5fa6916b726ebaaefd2997c5dabb7719464a6fa82a` |

## Measured counts

### testsets/nlu_en.csv

- lang: en=337
- source: heldout_gen=50, nq_open=287
- slice: control_insensitive=43, explicit=12, grammatical_gender=2, injection=12, mixed_gender=7, plain=27, surname=5, typo=17, unsupported=212

### testsets/nlu_hi.csv

- lang: hi=203
- source: aya=8, heldout_gen=45, indictrans2=150
- slice: control_insensitive=16, explicit=6, grammatical_gender=5, injection=12, mixed_gender=8, plain=20, romanised=6, surname=6, typo=1, unsupported=123

### testsets/nlu_ta.csv

- lang: ta=210
- source: aya=21, heldout_gen=47, indictrans2=142
- slice: control_insensitive=20, explicit=6, grammatical_gender=5, injection=12, mixed_gender=8, plain=18, romanised=6, surname=6, typo=1, unsupported=128

### testsets/xsport.csv

- lang: en=59, ta=1
- source: aya=1, nq_open=59
- slice: explicit=23, plain=37

### eval_data/benchmark_v1.csv

- language: en=120, hi=34, ta=34
- source: heldout_gen=120, indictrans2=68


Counts by language/source/slice and every evidence hash are in
`eval_data/release_manifest.json`. Read `eval_data/DATA_CARD.md` for exclusions,
licences, source biases and the small native-language subsets.

Verify with `python eval_data/tools/build_release.py --check`.
The preregistration hash is in the manifest; no results or accuracy are claimed.
