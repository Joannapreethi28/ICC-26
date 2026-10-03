# Make AI Know Her

**The gender-aware sports answer layer.** When a fan asks a gender-neutral cricket question ("Who has the most T20I runs?"), AI assistants tend to answer with the men's record only. Make AI Know Her detects that gender was not specified and answers with **both** the women's and men's records, each labelled, sourced and dated, in English, Hindi and Tamil. Explicit questions stay untouched; questions where gender does not matter get no intervention.

ICC Global Hackathon powered by Ignyte, 2026 (Prototype track). Status: in development (build started 3 Oct 2026).

## Repository map

| Path | What |
|---|---|
| `src/mak/` | The layer: understand (rules + fine-tuned Laya) → decide (plain-code policy) → fetch (verified facts) → answer (en/hi/ta templates) |
| `training/` | Training-data generation, Laya fine-tuning, calibration |
| `testsets/`, `eval_data/` | Held-out evaluation data and the three-arm benchmark |
| `document/` | Strategy (`plan.md`), build spec (`buildplan.md`), team tracks (`jabin_split.md`, `joanna_split.md`), `handoffs.md`, `gotcha.md` |
| `icc-make-ai-know-her/` | Research context pack: problem, evidence, decisions, verified records (`data/records_v1.csv`) |
| `CLAUDE.md` / `AGENTS.md` | Rules for coding agents |

## Quick start (development)

```bash
pip install -e .[dev]
pytest
```

## Data and licences

Cricsheet (Open Data Commons Attribution License 1.0: data from cricsheet.org), Wikidata (CC0), Wikipedia (CC BY-SA), NQ-open (CC BY-SA 3.0), Aya dataset (Apache-2.0), IndicTrans2 (MIT), Laya (Apache-2.0). Code: Apache-2.0 (`LICENSE`).
