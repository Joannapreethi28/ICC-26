"""Build a harsher messy-input slice from calib.jsonl (EVALUATION ONLY, never used for training). OWNER: Jabin.

Takes each calibration row, keeps its gold labels, and applies 2-4 heavy corruptions to the query text:
heavy typos, run-together words, dropped non-cue words, ALL CAPS / no caps, "??!!" spam, trailing emoji,
no punctuation. Gender-cue words are never corrupted or merged (that would be label noise, not realism).
Hindi/Tamil script: only whole-text operations (case n/a), punctuation spam, emoji, filler; no word surgery.

  python training/generate_data/make_messy_slice.py   ->  training/data/messy_calib.jsonl
"""
import json
import pathlib
import random
import re
import sys

ROOT = pathlib.Path(__file__).resolve().parents[2]
sys.path[:0] = [str(pathlib.Path(__file__).parent)]
from noise import _PROTECT, _typo_word  # noqa: E402

SEED = 20261004
EMOJI = ["🏏", "🙏", "😅", "??", "!!", "🤔", "🔥"]
CUE_EXTRA = {"women", "woman", "womens", "women's", "men", "mens", "men's", "male", "female", "ladies", "girls", "boys"}


def is_cue(tok: str) -> bool:
    core = re.sub(r"[^\w']", "", tok.lower())
    return core in _PROTECT or core in CUE_EXTRA


def heavy_typos(text, rng):
    out = []
    for t in text.split(" "):
        core = t.strip("?,.!:;()\"")
        if len(core) >= 4 and core.isascii() and core.isalpha() and not is_cue(core) and rng.random() < 0.6:
            t = t.replace(core, _typo_word(core, rng) if len(core) >= 5 else core[:-1] + core[-1] * 2, 1)
        out.append(t)
    return " ".join(out)


def run_together(text, rng):
    toks = text.split(" ")
    for _ in range(rng.choice((1, 2))):
        i = rng.randrange(0, max(1, len(toks) - 1))
        if i + 1 < len(toks) and toks[i].isascii() and toks[i + 1].isascii() and not is_cue(toks[i]) and not is_cue(toks[i + 1]):
            toks[i:i + 2] = [toks[i] + toks[i + 1]]
    return " ".join(toks)


def drop_word(text, rng):
    toks = text.split(" ")
    cand = [i for i, t in enumerate(toks) if len(t) <= 4 and t.isascii() and not is_cue(t) and not re.search(r"\d|t20|odi|wc", t.lower())]
    if cand and len(toks) > 4:
        toks.pop(rng.choice(cand))
    return " ".join(toks)


def case_mess(text, rng):
    return rng.choice((text.upper(), text.lower(), "".join(c.upper() if rng.random() < 0.4 else c.lower() for c in text)))


def punct_spam(text, rng):
    return text.rstrip("?।. !") + rng.choice(("???", "?!", "!!", "..", " ??", "?!?!", ""))


def emoji(text, rng):
    return text + " " + rng.choice(EMOJI)


LATIN_OPS = [heavy_typos, run_together, drop_word, case_mess, punct_spam, emoji]
SCRIPT_OPS = [punct_spam, emoji]


def corrupt(text, lang, romanised, rng):
    ops = LATIN_OPS if (lang == "en" or romanised) else SCRIPT_OPS
    applied = rng.sample(ops, k=min(len(ops), rng.choice((2, 3, 4))))
    for op in applied:
        text = op(text, rng)
    return re.sub(r"\s+", " ", text).strip()


def main():
    rng = random.Random(SEED)
    src = ROOT / "training" / "data" / "calib.jsonl"
    out = ROOT / "training" / "data" / "messy_calib.jsonl"
    n = changed = 0
    with src.open(encoding="utf-8") as f, out.open("w", encoding="utf-8") as g:
        for line in f:
            row = json.loads(line)
            lang = row["meta"]["lang"]
            romanised = lang != "en" and row["state"].isascii()
            new = corrupt(row["state"], lang, romanised, rng)
            n += 1
            changed += new != row["state"]
            row["state"] = new
            row["meta"] = {**row["meta"], "slice": "messy_hard"}
            g.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(f"wrote {out} ({n} rows, {changed} changed)")
    import banks_en, banks_hi, banks_ta  # v3: voice-style dev slice (synthetic speech-to-text style; EVALUATION ONLY)
    from noise import voice
    banks = {b.BANK["variant"]: b.BANK for m in (banks_en, banks_hi, banks_ta) for b in [m]}
    for m in (banks_en, banks_hi, banks_ta):
        for extra in m.__dict__.values():
            if isinstance(extra, dict) and "variant" in extra and "script" in extra:
                banks[extra["variant"]] = extra
    vout = ROOT / "training" / "data" / "voice_calib.jsonl"
    with src.open(encoding="utf-8") as f, vout.open("w", encoding="utf-8", newline="\n") as g:
        for line in f:
            row = json.loads(line)
            bank = banks.get(row["meta"]["variant"], banks["en"])
            row["state"] = voice(row["state"], bank, rng)
            row["meta"] = {**row["meta"], "slice": "voice_style"}
            g.write(json.dumps(row, ensure_ascii=False) + "\n")
    print(f"wrote {vout}")
    for lang in ("en", "hi", "ta"):
        with out.open(encoding="utf-8") as f:
            ex = [json.loads(x)["state"] for x in f if f'"lang": "{lang}"' in x][:4]
        print(lang, ex)


if __name__ == "__main__":
    main()
