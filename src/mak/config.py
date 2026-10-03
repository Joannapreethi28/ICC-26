"""Paths and thresholds. SHARED CONTRACT: change only with a CONTRACT CHANGE message in document/handoffs.md."""
from pathlib import Path

ROOT = Path(__file__).resolve().parents[2]
DATA = ROOT / "data"
GOLDEN_PATH = DATA / "golden" / "records_v1.csv"
DB_PATH = DATA / "processed" / "mak.duckdb"
LEXICON_DIR = DATA / "lexicons"
I18N_DIR = DATA / "i18n"
TESTSET_DIR = ROOT / "testsets"
RESULTS_DIR = ROOT / "results"

# Gender confidence below this -> treat as neutral -> show both (fail-safe). Re-fit by Jabin in J-P3.
GENDER_THRESHOLD = 0.85
# Injection markers in a query -> show both.
INJECTION_FAILSAFE = True

# Classifier switch. False = rules only. Jabin sets LAYA_MODEL_ID and announces "flip USE_LAYA" in handoffs.
USE_LAYA = False
LAYA_MODEL_ID = ""          # Hugging Face Hub repo id of the fine-tuned model, filled in J-P4
LAYA_BASE_MODEL = "convaiinnovations/laya-multilingual"
