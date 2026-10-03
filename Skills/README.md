# Skills: vetting registry (project scope: Make AI Know Her)

Checked Sat 3 Oct 2026, 15:10-15:40 IST, by Claude Code. Step 1-3 skills downloaded, vetted and installed 16:30 IST after Sir Jabin's go-ahead ("go as per the plan"). Pristine downloads kept in `Skills/_quarantine/` for audit; installed copies in `ICC'26/.claude/skills/`; checksums in `Skills/INSTALLED_SHA256.txt`.

## How a skill gets in (the gate)

1. **Download at the pinned commit** listed below into `Skills/_quarantine/<repo>@<sha>/`. Never use "latest": what we vetted is that exact commit.
2. **Read** SKILL.md and every non-markdown file. Grep for `curl`, `wget`, `http`, `subprocess`, `eval`, `exec`, hooks, telemetry, `~/.` writes, API keys.
3. **Check** against the project rules: free at runtime, no paid API, no global install, no hooks, nothing that edits CLAUDE.md.
4. **Approve:** Sir Jabin says yes for that row.
5. **Activate:** copy only the approved skill folder to `ICC'26/.claude/skills/<skill-name>/` (project scope, so it applies only to this project). Restart the Claude Code session so it loads.
6. **Log:** set the row's status to INSTALLED with the date. If it misbehaves, delete the folder and add a `gotcha.md` entry.

Vetting checklist for each repo: who owns it, licence, stars and recent activity, what is inside (markdown only, or scripts/binaries), network or telemetry behaviour, whether it fits our tasks, and whether it conflicts with tools we already have (superpowers, CLAUDE.md rules).

## Verdicts

### Recommended (step 1, install now: markdown only, official orgs, direct fit)

| # | Skill | Repo @ pinned commit | Owner / licence / activity | What is inside | Why we need it (buildplan task) | Status |
|---|---|---|---|---|---|---|
| 1 | `huggingface-gradio` | huggingface/skills @ `ca0325bb20b2` | Hugging Face (official org), Apache-2.0, ~11k★, pushed 1 Oct 2026 | Markdown only (2 files) | Gradio Blocks demo + MCP tool (T1.8, T3.1) | INSTALLED 3 Oct |
| 2 | `huggingface-spaces` | same | same | Markdown only (15 files) | Deploying the Space; it confirms the free-account rules (ZeroGPU, static) (T3.1, T3.2) | INSTALLED 3 Oct |
| 3 | `huggingface-zerogpu` | same | same | Markdown only (5 files) | ZeroGPU rules: the no-op `@spaces.GPU` pattern, quota, pickling traps (T3.1) | INSTALLED 3 Oct |
| 4 | `hf-cli` | same | same | Markdown only (1 file) | `hf` commands to create/push Spaces and model repos (T2.2, T3.1) | INSTALLED 3 Oct |
| 5 | `trl-training` | same | same | Markdown only (1 file) | Qwen2.5-1.5B LoRA comparison parser with TRL `SFTTrainer` (T2.4) | INSTALLED 3 Oct |
| 6 | `mcp-builder` | anthropics/skills @ `8a1541c4a3ff` | Anthropic (official org), Apache-2.0 (per-skill LICENSE.txt), ~179k★ | 4 reference docs + 3 scripts | MCP tool design (names, docstrings, schemas) (T1.8, T3.1). **Docs only:** its `scripts/` folder (evaluation.py calls the paid Anthropic API) was NOT copied into the installed skill | INSTALLED 3 Oct |
| 7 | `webapp-testing` | anthropics/skills @ `8a1541c4a3ff` | same | SKILL.md + Playwright helper (`with_server.py`: starts local servers, checks localhost ports; no outside network) | Automated browser tests of the Gradio demo and record pages (T1.8, T3.2, T4.1) | INSTALLED 3 Oct |

### Conditional (step 2, only when we reach UI polish on Sunday)

| # | Skill | Repo @ commit | Notes | Verdict |
|---|---|---|---|---|
| 8 | `impeccable` | pbakaus/impeccable @ `e103efe779e2` | Paul Bakaus, Apache-2.0, ~75k★, very active. **Not markdown-only:** its launcher runs a prebuilt platform binary and can download/cache an engine into `~/.impeccable` (outside the project). Strong for UI audit/polish of the record pages and demo CSS | Install only if we want a design pass; read the launcher and pin the binary checksum first |
| 9 | `web-design-guidelines` | vercel-labs/agent-skills @ `063bee94c3f4` | Vercel (official org), ~32k★. Markdown only, but it fetches its rules from GitHub at run time. **The repo has no licence file** (fine to use locally, not to redistribute) | Useful for an accessibility check of the record pages (T4.1). Cheap and low-risk |
| 10 | `brag` | latent-spaces/brag @ `cb89b9f44309` | MIT, ~13k★. Makes a 15-25 s launch video with Hyperframes (`npx hyperframes`, a Node download) and optional Kokoro voice (open source) | It cannot make our 3-minute demo video; it could make a short opener. Only if video time allows, after vetting the `hyperframes` npm package |

### Not for this project (legit, but wrong fit now)

| Repo | Why not |
|---|---|
| garrytan/gstack (MIT, ~135k★, Garry Tan) | Genuine and popular, but individual skills depend on gstack's own `bin/` tools, so it needs the **full global install** into `~/.claude/skills` (not project-scoped), Bun, a Stop hook, and an instruction to add a CLAUDE.md section banning the Chrome tools. It overlaps the superpowers skills we already use (plans, reviews, QA, debugging). Too heavy for a 28-hour sprint; revisit after the hackathon |
| Panniantong/Agent-Reach (MIT, ~89k★) | A CLI for reading/scraping Twitter, Reddit, YouTube, XiaoHongShu etc., some with cookies. Not needed for any task; adds privacy and terms-of-service risk |
| emilkowalski/skills (MIT, ~43k★, Emil Kowalski) | Excellent animation/design-engineering skills, but aimed at React, Expo and Swift. Our UI is Gradio + static HTML. Skip |
| Jpisnice/shadcn-ui-mcp-server (MIT, ~3k★, last push May 2026) | Gives an AI context about shadcn React components. We are not building React. Skip |
| huggingface/skills → `huggingface-llm-trainer` | **Rejected:** it requires submitting training to Hugging Face Jobs (paid cloud GPUs). Breaks free-only. We train locally or on free Kaggle |

### Could not verify

| Link | What happened | What I need |
|---|---|---|
| Instagram post (DdtP_L9FljV) | Readable text says "five skills" for better AI-made UI, but the skill names are inside the images, which I cannot read | Tell me the five names (or paste a screenshot); I will vet them the same way |
| Notion "LLM Council by Felix" | Page did not load (needs JavaScript or a login) | Paste the page text or the repo link. For context: the original is karpathy/llm-council (~25k★, no licence, uses OpenRouter, which is a paid API, dev-time only); a Claude-only variant (amgadelgamal/claude-council) uses several subagents, which costs a lot of tokens. Not needed for the build; could help review the plan |

## Install log (3 Oct 2026, 16:30 IST)

- Downloaded `huggingface/skills` @ `ca0325bb20b2d0a1b2efa893670c4c72f79e707b` and `anthropics/skills` @ `8a1541c4a3ffa5a20a5a91de0dcf3f0bab1d1ef4` (codeload tarballs of the exact commits).
- Scan results: no prompt-injection or agent-config tampering text; no telemetry; Python helpers read in full (`with_server.py` starts local servers and polls localhost only; `connections.py` is an MCP client; examples are Playwright samples). One flag: `hf-cli` suggests `curl -LsSf https://hf.co/cli/install.sh | bash`; **we install the CLI with `pip install -U huggingface_hub` instead** (gotcha G-012).
- Installed (project scope): `huggingface-gradio`, `huggingface-spaces`, `huggingface-zerogpu`, `hf-cli`, `trl-training` (+ upstream Apache-2.0 LICENSE copied as `LICENSE.upstream`), `mcp-builder` (SKILL.md, LICENSE.txt, reference/ only), `webapp-testing` (complete).
- `llm-council`: packaged by us from the public prompt Sir Jabin supplied (Felix/ADPList, adapted from Karpathy). Pure text, no code, no network. Project rules added: single response by default (no subagents unless asked), council advises and Sir Jabin decides, non-negotiables cannot be overridden by advisers. The linked "Claude Council skill" doc (parallel subagents + HTML report) was not provided, so it is not installed.
- Not installed (unchanged verdicts): impeccable, web-design-guidelines, brag (Sunday, optional); gstack, Agent-Reach, emilkowalski/skills, shadcn MCP, huggingface-llm-trainer.
- Seen in the session but NOT installed by us: `brightdata-plugin:*` (paid Bright Data service; its descriptions instruct agents to replace WebFetch/WebSearch, which we ignore) and `engineering:*` (a user-level plugin). Neither is vetted for this project; do not use them for project work without Sir Jabin's approval (gotcha G-013). **Bright Data disabled 3 Oct 16:55 at Sir Jabin's request** (full removal: claude.ai settings).

## Already available in this environment (no download needed)

- `superpowers` (writing-plans, test-driven-development, systematic-debugging, executing-plans, verification-before-completion, code review) for how we build.
- `anthropic-skills:pitch-deck`, `pptx` for the 5-slide deck; `dataviz` for result charts.

## Install order (step by step, after approval)

1. `huggingface/skills`: `huggingface-gradio`, `huggingface-spaces`, `huggingface-zerogpu`, `hf-cli` (needed before T1.8/T3.1)
2. `anthropics/skills`: `mcp-builder` (docs), `webapp-testing`
3. `huggingface/skills`: `trl-training` (before T2.4)
4. Sunday UI pass (optional): `web-design-guidelines`, then `impeccable` if wanted
5. Sunday video (optional): `brag`
