# CHANGELOG (build)

- 2026-10-03 IST: K-P1 (Joanna): golden loader and all 25 leader cross-checks; reproducible Cricsheet ingestion (8,916 matches); 18,554-person registry with conservative category derivation; cached Hindi/Tamil names and entity resolution; portable CSVs, provenance, coverage and rebuild docs. 131 tests passed. Four conflicting registry categories stay unknown; missing native labels explicitly fall back to English. Shared contracts and Jabin's files unchanged.
- 2026-10-03 IST: J-P1 (Jabin): rules baseline. Lexicons en/hi/ta (strong vs weak gender cues, stats, formats, injection), `nlu/lang.py`, `nlu/rules.py`, real `understand()` (rules only, never raises). 63 tests green.
- 2026-10-03 18:15 IST: Phase 0 contract (Jabin): repo scaffold, shared types/labels/config, stubs for understand() and resolve(), golden CSV with D2 fix, OWNERS, planning files, vetted project skills. Research history lives in icc-make-ai-know-her/CHANGELOG.md.
- 2026-10-03 IST: J-P2 (Jabin): Laya zero-shot baseline (2/10 gender, overconfident), training-data generator (schema, en/hi/ta banks incl. Hinglish/Tanglish, noise, grammar, build_dataset), paraphrases, 10,780 train / 2,981 calib rows, dataset tests, hashes frozen in training/DATA_FROZEN.md.
- 2026-10-03 IST: Verified Laya install location, model provenance and GPU by command; recorded in icc-make-ai-know-her/docs/09_laya_training_plan.md. No code change.

- 2026-10-03 J-P3: wrote training/train_laya.py (single GPU, bf16, grad checkpointing, offline). Smoke test OK: 0.56 s/update, peak 6.5 GB, est ~40 min for 3 epochs. Zero-shot (untrained) calib accuracy was 0.30-0.45 on family/format/gender/topic (MEASURED, 600 seqs). Full run launched; log: results/train_run1.log. Bug fixed: snapshot_download refuses the cache (missing README.md/.gitattributes), script reads the snapshot folder directly.

- 2026-10-03 J-P3 step 4: downloaded FacebookAI/xlm-roberta-base (safetensors only, hash MATCH, approved by Sir Jabin). Approach/method written into docs/09. Laya page confirms 'Downloads are not tracked'.

- 2026-10-03 J-P3: added training/train_encoder_baseline.py (xlm-roberta comparison arm, same data/labels/calibration) and training/generate_data/make_messy_slice.py -> training/data/messy_calib.jsonl (harsher messy-input EVALUATION slice from calib rows; never trained on; gender cues never corrupted). Not yet scored.

- 2026-10-03 J-P4 prerequisites (done early, while Laya trains): src/mak/nlu/laya_head.py (lazy offline load, two-step family->stat), understand.py merge policy v1 (rules cue = override; Laya gender accepted only if p >= GENDER_THRESHOLD else neutral/show both; injection keeps neutral; any Laya failure -> rules result + trace note), src/mak/nlu/laya_questions.json (question schemas), tests/nlu/test_laya_merge.py (6 tests with fake Laya output), training/generate_data/leakage_check.py. 105 tests pass (duckdb-dependent tests of Joanna's modules not collectable here: duckdb not installed). config.py NOT changed; USE_LAYA stays False until J-P4.

- CORRECTION 2026-10-03: laya_head.py is the Laya CANDIDATE backend only; the classifier choice (Laya vs xlm-roberta-base etc.) is NOT made. merge()/tests are model-neutral; a winner other than Laya needs only a sibling backend returning the same output.
