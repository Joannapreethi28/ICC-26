# OWNERS: who edits what (Sir Jabin's team split, 3 Oct 2026)

Edit only your own folders. Shared files change only after a CONTRACT CHANGE message in `document/handoffs.md`.

| Owner | Paths |
|---|---|
| **Jabin** (model, training, evaluation) | `src/mak/nlu/` (except `entities.py`), `training/`, `src/mak/eval/classifier_eval.py`, `src/mak/eval/arms.py`, `src/mak/eval/score.py`, `src/mak/eval/stats.py`, `data/lexicons/`, `models/` (never committed), `results/classifier/`, `results/e1/`, `results/e3/`, `results/e4/`, `results/training_log.md`, `docs/model_card.md` |
| **Joanna** (data, test sets, facts, product, deployment, docs) | `src/mak/ingest/`, `src/mak/registry/`, `src/mak/records/`, `src/mak/fetch/`, `src/mak/policy/`, `src/mak/compose/`, `src/mak/api/`, `src/mak/ui/`, `src/mak/pages/`, `src/mak/adapters/`, `src/mak/pipeline.py`, `src/mak/nlu/entities.py`, `data/` (except `data/lexicons/`), `testsets/`, `eval_data/`, `space/`, `site/`, `docs/` (except `model_card.md`), `results/reconciliation.md`, `scripts/download_data.py`, `scripts/refresh.py` |
| **Shared** (CONTRACT CHANGE message first) | `src/mak/types.py`, `src/mak/labels.py`, `src/mak/config.py`, `pyproject.toml`, `OWNERS.md` |
| **Both** (append-only, newest first) | `document/handoffs.md`, `document/gotcha.md` |
| **Sir Jabin decides** | `document/plan.md`, `document/buildplan.md`, `document/*_split.md`, `CLAUDE.md`, `AGENTS.md` |

Firewall: Jabin does not open `testsets/` or `eval_data/` until his training data is frozen (`training/DATA_FROZEN.md`). Test data is never given to the training-data generator.
