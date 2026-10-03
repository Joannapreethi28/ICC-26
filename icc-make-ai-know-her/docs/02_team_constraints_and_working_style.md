# 02. Team, constraints and working style

## Team
- Sir Jabin (leads; B.Tech AI & Data Science, LICET Chennai), Joanna (the required woman team member), Efanio. Student category, Prototype track. Fully dedicated until the deadline.
- **Sir Jabin decides all work allocation.** Do not propose or assign roles. Note only the rule: Women-integrated teams must have strong representation of women founders or developers, and the criteria reward it; how that is organised is Sir Jabin's call.

## Hard constraints
| Constraint | Detail |
|---|---|
| **Free only** | Locked 3 Oct. No paid APIs or services at runtime. Jev (paid, no free tier) is out. |
| Dev tools | Claude Code and GPT 6 are available for building and for one-time training-data generation. Nothing at runtime may depend on them. |
| Hardware | Laptop with RTX 5060 (8 GB VRAM); about US$100 AWS credit (new account, GPU quota starts at 0, so not relied on); free Kaggle GPUs (2x T4 notebooks); free Hugging Face Spaces for hosting |
| Time | Sat 3 Oct (today) to Sun 4 Oct 8 pm = build window. Mon 5 Oct = buffer and submission only. |
| Scope | Everything in `docs/08_build_plan.md` is to be built; no cut line. |
| Languages | English, Hindi, Tamil (Tamil is required to show multilingual capability) |
| Domain | Fan engagement / visibility only. Athlete health is out. |

## Quality bar (from the team's earlier wins)
- Antimicrobial-peptide triage (Tech Sangamam 2026: 4th of 78, special award) and RWAUSD (Multipli.fi DeFi hackathon). Pattern: a common assumption that doesn't match reality, **measured on real data**, honest about negative results, ending in a decision or mechanism.
- For this project: assumption = "AI assistants will surface women's cricket when asked a normal cricket question"; reality = measured gap; mechanism = the gender-aware policy layer.

## How to work with Sir Jabin
- Brutal honesty: say plainly when something is weak, wrong or unrealistic. Never blindly agree. Own your mistakes.
- Short, clear, point-wise answers; explain new concepts like to a beginner, with examples and analogies; explain the *why*.
- Plan before build; research before locking a direction; challenge his reasoning and yours.
- Complete files ready to paste, not diffs.
- **Do not run long analyses or tool-heavy tests without asking first.** (On 2 Oct and again on 3 Oct, unrequested/long runs cost tokens and time without changing the decision; the Claude-in-Chrome audit was dropped for this reason.)
- Do not present a proxy result as a finding. Say what a number does not prove.
- Prefer visuals/diagrams where they help.
- Mark each claim: verified (source), from memory, or unverified.

## Locked decisions by Sir Jabin (summary; full log in docs/05)
1. Neutral cricket question -> show both men's and women's records, labelled.
2. "Asked back" ("men's or women's?") is its own result row, not a pass.
3. Everyday prompts ("best Indian cricketers right now?") are a side measure (is any woman named?).
4. Target markets: India, England, Australia, New Zealand.
5. Free only; trained Laya (or Qwen-class) is required, not optional; Tamil included; everything gets built.
6. Claude-in-Chrome baseline audit dropped; existing sources and findings are enough evidence.
7. Build stops Sun 4 Oct 8 pm; Monday is buffer.
8. Laya coverage v1: T20I, ODI, World Cups (extensions welcome since everything is in scope).

## Earlier rejected ideas (do not re-propose without new evidence)
From `source_docs/handoff_icc_hackathon_2_oct.md` section 4: Audience Curve; Spotlight / Hidden Match-Winner; cross-league bowling workload; Cycle-Safe; Shop-Window Fixtures; Guaranteed Audience; Replace DRS; Replace the wagon wheel; plus set aside: fan retention cliff, sponsor-logo computer vision, endorsement marketplace, moment-triggered brand activation. `source_docs/context-2-icc_AUDIENCE_CURVE_SUPERSEDED.md` is the superseded Audience Curve brief; only its event facts are still used.
