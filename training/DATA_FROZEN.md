# DATA_FROZEN

## v2 (current): frozen 2026-10-03 (J-P3, approved by Sir Jabin: "v2 first, then test once")

Built ONLY from calibration-set findings (G-026); the frozen test sets were not opened or scored before this freeze
(only testsets/FROZEN.md counts/hashes were read). Changes vs v1: English slang/variant phrasings added to 4 career cores
(knock, team innings total, tons/100s, bowling/batting avg) in both train and calib positions; new 'abbrev' noise op
(wkts, 100s, avg, SR, econ, intl, games, top). Hindi/Tamil banks unchanged (no native-speaker review available).
Training-side v2 changes (scripts, not data): all text lowercased + whitespace-normalised for every model arm at train
and inference; Laya 2 epochs (was 3) + label smoothing 0.05 on CE only.

| file | rows | sha256 |
|---|---|---|
| training/data/train.jsonl | 10760 | 5fcb257f1bc5ddeaa2d06b0b3bc3cc4fdfead1b8b7dd7b174604d29394fc35db |
| training/data/calib.jsonl | 2982 | 1178b77fa141e9d16202c73761e38c56233bdd970ddf5f65ca67bfa9d5236605 |
| training/data/messy_calib.jsonl | 2982 | b2c41c03918014ebc8924c78a0e48036b3b8f82eb5c89e4baff0f41e992adc8e |

Regenerate: `python training/generate_data/build_dataset.py` then `python training/generate_data/make_messy_slice.py` (seeds 20261003 / 20261004).
Hashes are of UTF-8 bytes with LF line endings (same as the git blobs).
Leakage (2026-10-03): exact 0 everywhere. Near-duplicate screen (>= 0.92 character similarity, leakage_check.py) flagged 4 train rows; they were dropped automatically WITHOUT being displayed (`--drop`), train 10764 -> 10760; re-check: 0 exact, 0 near in train/calib/messy_calib. String hygiene only, not proof against semantic overlap.

## v1 (superseded, kept for history): frozen 2026-10-03 (J-P2)

| file | rows | sha256 |
|---|---|---|
| training/data/train.jsonl | 10780 | f448d921ed408ba7d15fbb69156274c6271a9b255f990af21c9a96d2f68f4bba |
| training/data/calib.jsonl | 2981 | 8c579f17f24ebe97fa694944957c0c8ada494e9c9610c6c9267c7504b371b63a |

v1 models: models/laya-mak-v1, models/xlmr-mak-v1 (calibration-set results only; never scored on test sets).