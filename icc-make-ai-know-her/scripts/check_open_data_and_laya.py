"""
Facts checked before designing the solution (3 Oct 2026):
 1. Hugging Face model cards for laya and laya-multilingual: licence, size, languages, fine-tuning notebook, warnings.
 2. Cricsheet register page: licence wording, ID columns (key_cricinfo, key_opta, key_pulse...), people.csv / names.csv.
 3. Wikidata: property P2697 (Cricinfo player ID), P21 (sex or gender), Hindi/Tamil labels (Smriti Mandhana = Q16224802).
Results are summarised in docs/09_laya_training_plan.md and docs/10_data_and_records.md.
"""
import json, re, html, urllib.request, urllib.parse

UA = {"User-Agent": "ICC-hackathon-research/0.1"}
def get(u, t=40):
    return urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=t).read().decode("utf-8", "ignore")

for m in ["convaiinnovations/laya-multilingual", "convaiinnovations/laya"]:
    d = json.loads(get(f"https://huggingface.co/api/models/{m}"))
    print("==", m, "| licence:", d.get("cardData", {}).get("license"), "| pipeline:", d.get("pipeline_tag"), "| modified:", d.get("lastModified"))
    r = get(f"https://huggingface.co/{m}/raw/main/README.md")
    for k in ["Fine-tun", "Near chance", "choice` questions under", "pip install", "Tamil", "Hindi", "head_max_len", "Router"]:
        mm = re.search(k, r, re.I)
        if mm: print(f"  [{k}] ...{r[max(0, mm.start()-120):mm.start()+220].replace(chr(10), ' ')}...")

for u in ["https://cricsheet.org/register/"]:
    s = re.sub(r"\s+", " ", re.sub("<[^>]+>", " ", html.unescape(get(u))))
    for k in ["Open Data Commons", "key_cricinfo", "key_opta", "key_pulse", "people.csv", "names.csv"]:
        mm = re.search(k, s)
        if mm: print(f"[{k}] ...{s[max(0, mm.start()-140):mm.start()+200]}...")

for q in ["ESPNcricinfo player ID"]:
    d = json.loads(get("https://www.wikidata.org/w/api.php?" + urllib.parse.urlencode(
        {"action": "wbsearchentities", "search": q, "type": "property", "language": "en", "format": "json"})))
    print(q, "->", [(x["id"], x.get("label")) for x in d.get("search", [])][:3])
d = json.loads(get("https://www.wikidata.org/w/api.php?" + urllib.parse.urlencode(
    {"action": "wbsearchentities", "search": "Smriti Mandhana", "language": "en", "format": "json"})))
qid = d["search"][0]["id"]
e = json.loads(get(f"https://www.wikidata.org/wiki/Special:EntityData/{qid}.json"))["entities"][qid]
print(qid, "labels hi/ta:", e["labels"].get("hi", {}).get("value"), "/", e["labels"].get("ta", {}).get("value"))
print(" P21:", [c["mainsnak"]["datavalue"]["value"]["id"] for c in e["claims"].get("P21", [])],
      " P2697:", [c["mainsnak"]["datavalue"]["value"] for c in e["claims"].get("P2697", [])])
