# 14. Scripts index (every script run for this problem statement)

All live in `scripts/`. The first four were **re-created from the exact commands run on 3 Oct 2026** (the original runs were inline); they were syntax-checked (`py_compile`) but not re-run end to end when packed, and the sources they hit change over time, so results may differ from the dated numbers in the docs. `build_bank.py` and `run_audit.py` are the original files.

| Script | Purpose | Output / where results are recorded | Status |
|---|---|---|---|
| `wikipedia_source_audit.py` | Pageviews and lead-text audit of unqualified vs women's Wikipedia pages; marker counts in the records-page wikitext | `data/wiki_audit.json`; docs/04 section 6 | Recreated |
| `wikipedia_records_extract.py` | Fetch 8 Wikipedia pages (records lists, World Cup pages), print last-edit dates, extract record tables and infobox records | The numbers in `data/records_v1.csv`; docs/10 | Recreated |
| `verify_discussion_sources.py` | Fetch all sources cited in the master doc and search for the claimed figures; check the cited GitHub repos exist | docs/04 section 10 | Recreated |
| `check_open_data_and_laya.py` | Laya model cards (licence, size, languages, warnings), Cricsheet register licence/ID columns, Wikidata P2697/P21 and hi/ta labels | docs/09, docs/10 | Recreated |
| `probe_free_llm_endpoints.sh` | Tested keyless LLM endpoints for a baseline audit; all unusable | docs/05 item 2 | Recreated (outcome: none usable) |
| `build_bank.py` | Builds the 100-question draft benchmark (`data/question_bank.csv`) | A 17, B 25, C 18, D 28, E 12 | Original; **partly stale** (A03 truth, B numbers, scoring rule predates "show both", no G set) |
| `run_audit.py` | Runner that asks each question to API models, auto-scores with marker matching, writes a summary | Mock-tested only; never run on real models | Original; uses the pre-"show both" scoring and OpenAI-compatible endpoints that need keys (Gemini, Groq, GitHub Models); rebuild under docs/11 |

Not scripts, but part of the record:
- `data/records_v1.csv` was written by an inline Python script (one `add(...)` per row). Its provenance is in the CSV columns.
- Web searches (news/ICC pages) were used to corroborate dynamic records (listed in docs/13).
- `prompts_archive/` holds the Claude-in-Chrome audit prompts and context blocks (plan dropped).
