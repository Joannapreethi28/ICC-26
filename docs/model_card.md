# Model card: Laya v3 for Make AI Know Her

**What it does:** reads a sports question (English, Hindi, Tamil, including romanised and messy text) and picks categories: gender signal (women / men / both named / none), topic, record family, statistic and format. **It never writes a fact or a number**; every number comes from the verified database with a source and an as-of date. The "show both" policy is plain code, not the model.

| | |
|---|---|
| Base model | `convaiinnovations/laya-multilingual` (mmBERT-base backbone + typed-decision head, 322M params, Apache-2.0) |
| Fine-tuning | Laya recipe (soft cross-entropy + proper-scoring policy reward), 2 epochs, label smoothing 0.05, lowercased input, single RTX 5060 8 GB, ~35 min |
| Training data | ~10.8k synthetic questions (training data v3, `training/DATA_FROZEN.md`), template + paraphrase, ~40% noise (typos, casing, SMS, abbreviations, voice-style) |
| Calibration | temperature per option-count bucket on a template-disjoint calibration set; gender accepted only if p >= 0.85, else neutral (show both) |
| Weights | GitHub Release `laya-mak-v3` (`python scripts/get_laya_weights.py`, SHA-256 verified) |
| Size / cost | ~640 MB fp16; runs on CPU; free, offline, no API |

## Results (from `results/classifier/report.md`)
- **Official held-out run** used the earlier v2 models; it was also the selection run (disclosed).
- **v3 numbers are post-hoc and test-informed** (changed using aggregate test counts, no test text read).
- Shipped system (Laya v3 + rules), gender accuracy: en 0.917, hi 0.887, ta 0.929 (post-hoc). End-to-end decision accuracy (E4): en 0.748, hi 0.675, ta 0.762 vs rules-only 0.632 / 0.498 / 0.481.
- Cross-sport (E3, untouched): gender en 0.949 vs rules 0.847 (n=59).
- **Gate G4 (gender >= 98% per language) is not met** on real queries.

## Limits
- Hindi and Tamil training data and most test rows are synthetic or machine-translated; no native-speaker validation.
- No real voice transcripts; voice robustness only on a synthetic dev slice.
- Stat accuracy on real queries is ~0.55; outside the 25 supported record types the system says unsupported (or gives guidance only) rather than guessing.
- Records change (e.g. Mandhana passed Bates on 20 Sep 2026); answers always carry `as_of` and must be re-verified.
- Prompt-injection text never changes the policy (fail-safe: show both).
