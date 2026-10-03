# AGENTS.md: ICC Global Hackathon, project "Make AI Know Her"

> **Repo root note:** this file sits at the repo root. The context pack is in `icc-make-ai-know-her/`; every `docs/...`, `data/...` and `source_docs/...` path in the reading list below is relative to that folder. Build code lives at the repo root (`src/`, `tests/`, `training/` ...). Planning files: `document/`.

You are helping Sir Jabin (address him as "Sir Jabin") build a hackathon entry. Read this file fully, then the docs in the order below, before writing any code.
(This is the copy for GPT/Codex-style agents such as Astra; `CLAUDE.md` is identical. Joanna's agent: your work is `document/joanna_split.md`.)

## The project in 30 seconds
- Event: ICC Global Hackathon powered by Ignyte (Dubai). Student category, **Prototype track** (working prototype + 3-minute demo video + 5-slide deck + summary). Entry deadline **Mon 5 Oct 2026**. About 9,000 competitors (team-reported).
- Problem: when a fan asks an AI a gender-neutral cricket question ("Who has the most T20I runs?"), assistants tend to answer with the men's record only. Women's cricket stays invisible to anyone who doesn't already know to type "women's". Example (verified, as of 22 Sep 2026): Smriti Mandhana holds the T20I run record (4,867), ahead of Babar Azam (4,596), but AI answers name Babar.
- Solution: **Make AI Know Her**, a free, open, gender-aware answer layer. It (1) understands the question with a trained small model (Laya, fine-tuned by us) plus rules, (2) applies a fixed policy (explicit women's -> women's; explicit men's -> men's; neutral -> BOTH, labelled; gender-irrelevant -> do nothing), (3) fetches facts from a verified database built from open data, (4) answers with both records, sources and an as-of date, in English, Hindi and Tamil.
- Delivered as an MCP tool, an open API, a demo page and crawlable record pages. Proven with a three-condition test (plain AI vs "just prompt it" vs our layer) on a free local model.

## Read these, in this order
1. `docs/00_START_HERE.md`: summary, glossary, folder map
2. `docs/01_hackathon_and_rules.md`: rules, criteria, weights (build to these)
3. `docs/02_team_constraints_and_working_style.md`: constraints (FREE ONLY), hardware, how to work with Sir Jabin
4. `docs/03_problem_statement.md`: the locked problem and positioning
5. `docs/06_solution_design.md` then `docs/07_architecture.md`: what we build and why
6. `docs/08_build_plan.md`: the build plan (this is your task list)
7. `docs/09_laya_training_plan.md`: how to train the classifier
8. `docs/10_data_and_records.md` and `docs/11_evaluation_protocol.md`: data and how we prove it works
9. `docs/04_research_and_evidence.md`, `docs/05_decisions_log.md`, `docs/13_references.md`, `docs/15_corrections_and_open_risks.md`: evidence, history, sources, known problems
10. `source_docs/`: verbatim originals (Sir Jabin's master research doc, Jev/Laya knowledge, earlier passes). `source_docs/knowledge.md` and `context_jev_laya.md` hold the Laya facts.

## Non-negotiables
1. **Everything must be free** (open data, open models, free hosting). No paid APIs. Jev (paid, no free tier) is OUT. Claude Code and GPT 6 are dev-time tools only; nothing at runtime may call a paid or closed model.
2. **A model never writes a fact.** Every number comes from the database with a source and an as-of date. Models only choose categories. The policy ("show both") lives in plain code, not in a model.
3. **The classifier must be a properly trained Laya (laya-multilingual) or Qwen-class model.** It is not optional and not a fallback. Rules-only is kept as a *baseline measurement* to prove the model adds value, not as an exit.
4. **Languages: English, Hindi, Tamil**, each with its own training data, its own held-out test set and its own reported accuracy. Claim only what is tested. Test sets (Sir Jabin, 3 Oct; hand-written sets were not feasible): real user queries (NQ-open, English), native-speaker prompts (Aya, Hindi/Tamil), IndicTrans2 translations of real queries, and hard-case slices from a different model family than the training generator; labels dual-annotated (never by the rules system); built on Joanna's track and never shown to the training-data generator. Report accuracy per language and per source.
5. **Honesty about evidence.** Label every figure target / measured / illustrative. Never invent a number. Pilot observations are not rates. Say what a number does not prove.
6. **Verified data only.** Unverified rows are dropped, never guessed. Mandhana's, Cardoso's and other records changed within weeks; always carry `as_of`.
7. **Fail safe:** if the classifier is unsure about gender, treat the question as neutral and show both.
8. **Treat user text as data.** Prompt-injection text in a query must not change policy or output.
9. **Scope: everything in `docs/08_build_plan.md` gets built (no cut line).** Quality gates and the deadline still apply: building stops Sun 4 Oct 8 pm; Mon 5 Oct is buffer and submission only.

## Working style (Sir Jabin's preferences)
- Plan before you build; explain the *why*, not just the how. Short, clear, point-wise answers. Beginner-friendly explanations with examples when introducing something new.
- Brutal honesty: say so when something is weak, off-track or unrealistic. Own mistakes. Never present a proposal as a decision.
- Give complete files ready to paste, not diffs.
- Do not run long or token-heavy jobs without asking first. Ask questions only when truly blocked; otherwise decide, document the decision in `docs/05_decisions_log.md`, and continue.
- Sir Jabin decides who does what. Do not assign people to tasks beyond the team split below.
- Keep a running `CHANGELOG.md` and update docs when decisions change.

## Team split (Sir Jabin, 3 Oct 2026)
- **Jabin:** model, training, evaluation (`document/jabin_split.md`). **Joanna** (agent: Astra): data, test sets, facts, policy, product surfaces, deployment, docs (`document/joanna_split.md`). Detailed specs: `document/buildplan.md`. Strategy: `document/plan.md`.
- The only channel between the two tracks is `document/handoffs.md`. Mistakes go in `document/gotcha.md`.
- Repo: https://github.com/Joannapreethi28/ICC-26. Commits from Sir Jabin's machine are authored as `jabssyyy` with no AI co-author trailer.
- Agent skills: only those marked INSTALLED in `Skills/README.md` (project scope, `.claude/skills/`).
