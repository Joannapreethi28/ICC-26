<img src="logo/logo_mcp_128.png" alt="Make AI Know Her logo" width="96" align="right">

# Make AI Know Her

**The gender-aware sports answer layer.** When a fan asks a gender-neutral cricket question ("Who has the most T20I runs?"), AI assistants tend to answer with the men's record only. Make AI Know Her detects that gender was not specified and answers with **both** the women's and men's records, each labelled, sourced and dated, in English, Hindi and Tamil. Explicit questions stay untouched; questions where gender does not matter get no intervention.

ICC Global Hackathon powered by Ignyte, 2026 (Prototype track). Status: submitted prototype (5 Oct 2026).

- **Live demo:** https://jabssyyy--make-ai-know-her-web.modal.run (permanent, free Modal hosting; sleeps when idle, so the first request takes ~20-60 s)
- **MCP server (Streamable HTTP, no auth):** https://jabssyyy--make-ai-know-her-web.modal.run/gradio_api/mcp/ . Tools: `resolve_sports_query`, `list_supported_intents`
- **Open model weights:** [GitHub Release `laya-mak-v3`](https://github.com/Joannapreethi28/ICC-26/releases/tag/laya-mak-v3) (Apache-2.0). Model card: [`docs/model_card.md`](docs/model_card.md)
- **Results:** [`results/classifier/report.md`](results/classifier/report.md), [`results/e1/tables.md`](results/e1/tables.md) (first-pass automatic labels)
- **Connect from ChatGPT:** Settings → Apps & Connectors → Developer mode → Create → paste the MCP URL, set No authentication, and use [`logo/logo_mcp_128.png`](logo/logo_mcp_128.png) as the icon.

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
pip install -e .[dev,ml]
python scripts/get_laya_weights.py   # trained Laya v3 from the GitHub Release, SHA-256 checked
pytest
python scripts/serve_demo.py          # demo + MCP on http://127.0.0.1:7862 (add --share for a temporary public link)
```

## Data and licences

Cricsheet (Open Data Commons Attribution License 1.0: data from cricsheet.org), Wikidata (CC0), Wikipedia (CC BY-SA), NQ-open (CC BY-SA 3.0), Aya dataset (Apache-2.0), IndicTrans2 (MIT), Laya (Apache-2.0). Code: Apache-2.0 (`LICENSE`).

## Local demo, REST and MCP

Validated with Python 3.14 and Gradio 6.29.1 on 4 October 2026. The current UI uses Gradio 6 APIs; the dependency now requires Gradio 6.29.1 or later within major version 6.

```bash
python -m mak.api.app
```

Open http://127.0.0.1:8000. REST: `POST /resolve`, `GET /health`, `/coverage`, `/intents`; MCP: `http://127.0.0.1:8000/gradio_api/mcp/` (Streamable HTTP). Tools: `resolve_sports_query` and `list_supported_intents`. Queries must be nonblank and at most 2,000 characters. Language: `auto`, `en`, `hi`, `ta`.

Alternatively `python -m mak.ui.demo` serves the UI and MCP on port 7860. For a different unified port: `python -m uvicorn mak.api.app:create_app --factory --host 127.0.0.1 --port 7861`.

The model is loaded lazily from `models/laya-mak-v3` or `MAK_LAYA_PATH`. `/health` distinguishes configuration from loaded weights. Missing weights mean **rules-only**, not a trained-model demonstration. The computed database is also needed for player-specific records; an unavailable record stays unanswered. The demo reports both limitations. The saved plain-model comparison is an exact-question E1 capture, labelled with model and date; it is neither live consumer AI nor a bias rate.

Public hosting: Modal free tier (`deploy/modal_app.py`, one small CPU container, sleeps after 5 idle minutes). Deploy: `python -m modal deploy deploy/modal_app.py`.

