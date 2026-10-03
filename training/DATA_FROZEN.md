# DATA_FROZEN

Frozen: 2026-10-03 (J-P2). Training and calibration data are final for J-P3.

| file | rows | sha256 |
|---|---|---|
| training/data/train.jsonl | 10780 | f448d921ed408ba7d15fbb69156274c6271a9b255f990af21c9a96d2f68f4bba |
| training/data/calib.jsonl | 2981 | 8c579f17f24ebe97fa694944957c0c8ada494e9c9610c6c9267c7504b371b63a |

Regenerate with `python training/generate_data/build_dataset.py` (seed 20261003). Test sets were not read to build this data (G-011); the leakage check runs after this file exists.

