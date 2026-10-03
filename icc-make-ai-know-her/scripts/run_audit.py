"""
Default-Man Audit runner.
Asks every question in question_bank.csv to each configured AI model, saves raw answers,
auto-scores them with marker matching, and writes a summary. Auto-scores MUST be human-checked
(column human_label in scored_*.csv) before any number goes on a slide.

Usage:
  python run_audit.py --mock                      # dry run, no API calls
  python run_audit.py --providers gemini,groq     # real run (keys in env vars, see PROVIDERS)
Design choices (and why):
  * No system prompt, default temperature -> closest to what a casual user gets from the raw model.
  * One sample per question by default (--samples 3 recommended for the final run: answers vary).
  * API models have no web search, so this measures the model's built-in default. Consumer apps
    (ChatGPT, Gemini app, Google AI Overviews, Perplexity) add search: test those with consumer_app_log.csv.
"""
import csv, json, os, sys, time, argparse, re, urllib.request, datetime, collections

# OpenAI-compatible endpoints. Model names change often: check each provider's model list before running.
PROVIDERS = {
  "gemini":     dict(base="https://generativelanguage.googleapis.com/v1beta/openai", key="GEMINI_API_KEY",  models=["gemini-2.5-flash"]),
  "groq":       dict(base="https://api.groq.com/openai/v1",                         key="GROQ_API_KEY",    models=["llama-3.3-70b-versatile"]),
  "github":     dict(base="https://models.github.ai/inference",                     key="GITHUB_TOKEN",    models=["openai/gpt-4o-mini","openai/gpt-4o"]),
  "pollinations":dict(base="https://gen.pollinations.ai/v1",                        key="POLLINATIONS_KEY",models=["openai/gpt-4o-mini","google/gemini-2.5-flash-lite","meta/llama-4-scout","perplexity/sonar"]),
  "openrouter": dict(base="https://openrouter.ai/api/v1",                           key="OPENROUTER_API_KEY", models=[]),
}

WOMEN_LIST = """mandhana harmanpreet jemimah deepti shafali richa ghosh renuka radha yadav vastrakar mithali jhulan
perry healy lanning mooney gardner sutherland schutt bates devine amelia kerr sciver ecclestone heather knight wyatt
athapaththu chamari dottin hayley matthews stafanie taylor shabnim kapp wolvaardt nida dar bismah fatima sana nigar
belinda clark heyhoe charlotte edwards bakewell edulji rangaswamy anjum chopra rohmalia lucia taylor
women's woman women wpl female girls' मंधाना हरमनप्रीत दीप्ति महिला मिताली झूलन மந்தனா ஹர்மன்பிரீத் தீப்தி மகளிர் பெண்கள் வீராங்கனை மிதாலி""".split()
# multiword names are matched by their distinctive token above (e.g. 'harmanpreet'); generic tokens like 'women' count as visibility.

def norm(t): return (t or "").lower()

def score(row, answer):
    a = norm(answer)
    wm = [m for m in row["women_markers"].split("|") if m]
    if wm == ["<WOMEN_LIST>"]:
        wm = WOMEN_LIST
    mm = [m for m in row["men_markers"].split("|") if m]
    has_w = any(m.lower() in a for m in wm)
    has_m = any(m.lower() in a for m in mm)
    cat = row["category"]; rule = row["scoring_rule"][:2]
    if not a.strip(): return "NO_ANSWER"
    if rule.startswith("D"): return "VISIBLE" if has_w else "INVISIBLE"
    if cat == "C": return "KNOWS" if has_w else "DOES_NOT_KNOW"
    if rule.startswith("A"):
        if has_w: return "CORRECT"
        return "WRONG_MEN_ONLY" if has_m else "OTHER"
    if rule.startswith("B"):
        if has_w and has_m: return "BOTH"
        if has_w: return "WOMEN_ONLY"
        return "MEN_ONLY" if has_m else "OTHER"
    return "OTHER"

def ask(base, key, model, q, timeout=120):
    body = json.dumps({"model": model, "messages": [{"role": "user", "content": q}]}).encode()
    req = urllib.request.Request(base.rstrip("/") + "/chat/completions", data=body,
        headers={"Content-Type": "application/json", "Authorization": f"Bearer {key}"})
    for attempt in range(4):
        try:
            d = json.load(urllib.request.urlopen(req, timeout=timeout))
            return d["choices"][0]["message"]["content"]
        except Exception as e:
            err = str(e); time.sleep(2 ** attempt * 3)
    return f"__ERROR__ {err}"

MOCK = {  # canned answers to test the pipeline only
  "A": "The most is held by Babar Azam of Pakistan.", "B": "Sachin Tendulkar holds it.",
  "C": "In women's cricket it is Smriti Mandhana.", "D": "Virat Kohli, Rohit Sharma and Jasprit Bumrah.",
  "E": "बाबर आज़म"}

def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--providers", default="")
    ap.add_argument("--samples", type=int, default=1)
    ap.add_argument("--mock", action="store_true")
    ap.add_argument("--only", default="", help="comma list of ids, e.g. A01,A02")
    args = ap.parse_args()
    bank = list(csv.DictReader(open("question_bank.csv", encoding="utf-8")))
    if args.only: bank = [r for r in bank if r["id"] in args.only.split(",")]
    targets = [("mock", None, "mock-model")] if args.mock else []
    for p in filter(None, args.providers.split(",")):
        cfg = PROVIDERS[p]; key = os.environ.get(cfg["key"])
        if not key: sys.exit(f"Missing env var {cfg['key']} for provider {p}")
        targets += [(p, cfg, m) for m in cfg["models"]]
    stamp = datetime.datetime.now().strftime("%Y%m%d_%H%M")
    raw = open(f"responses_{stamp}.jsonl", "w", encoding="utf-8")
    scored = []
    for prov, cfg, model in targets:
        for r in bank:
            for s in range(args.samples):
                ans = MOCK[r["category"]] if prov == "mock" else ask(cfg["base"], os.environ[cfg["key"]], model, r["question"])
                lab = score(r, ans)
                rec = dict(timestamp=datetime.datetime.now().isoformat(timespec="seconds"), provider=prov, model=model,
                           id=r["id"], category=r["category"], language=r["language"], sample=s, question=r["question"],
                           answer=ans, auto_label=lab, human_label="", note="")
                raw.write(json.dumps(rec, ensure_ascii=False) + "\n"); scored.append(rec)
                if prov != "mock": time.sleep(1.5)
            print(f"{prov}/{model} {r['id']} -> {lab}", flush=True)
    raw.close()
    with open(f"scored_{stamp}.csv", "w", newline="", encoding="utf-8") as f:
        w = csv.DictWriter(f, fieldnames=list(scored[0].keys())); w.writeheader(); w.writerows(scored)
    # summary (auto labels; replace with human labels before quoting)
    out = [f"# Default-Man Audit summary ({stamp}) - AUTO labels, not yet human-checked\n"]
    by = collections.defaultdict(list)
    for x in scored: by[(x["provider"], x["model"])].append(x)
    def rate(xs, cat, labs, lang="en"):
        sel = [x for x in xs if x["category"] == cat and x["language"] == lang]
        return (sum(x["auto_label"] in labs for x in sel), len(sel))
    for (p, m), xs in by.items():
        a = rate(xs, "A", ["WRONG_MEN_ONLY"]); b = rate(xs, "B", ["MEN_ONLY"])
        c = rate(xs, "C", ["KNOWS"]); d = rate(xs, "D", ["VISIBLE"])
        e = (sum(x["auto_label"] in ("WRONG_MEN_ONLY", "INVISIBLE") for x in xs if x["category"] == "E"),
             sum(1 for x in xs if x["category"] == "E"))
        pct = lambda t: f"{t[0]}/{t[1]} ({100*t[0]/max(t[1],1):.0f}%)"
        out.append(f"## {p} / {m}\n- A wrong answer (named a man where a woman holds it): {pct(a)}\n"
                   f"- B men-only answer to a neutral question: {pct(b)}\n- C knows the women's answer when asked directly: {pct(c)}\n"
                   f"- D women visible in everyday prompts: {pct(d)}\n- E Hindi/Tamil fails (men-only or invisible): {pct(e)}\n")
    open(f"summary_{stamp}.md", "w", encoding="utf-8").write("\n".join(out))
    print("\n".join(out))

if __name__ == "__main__":
    main()
