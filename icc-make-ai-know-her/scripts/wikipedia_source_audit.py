"""
Wikipedia source audit: does the web-source layer default to men's cricket?
Ran on 3 Oct 2026. Output saved as ../data/wiki_audit.json.

Part 1: for each (unqualified page, women's page) pair, pull the lead sentences and 12 months
        of English-Wikipedia pageviews (Sep 2025 - Aug 2026) via the Wikimedia REST API.
Part 2: pull the wikitext of the two T20I / ODI records pages and count markers
        (does the unqualified page mention women's records at all?).
Network: needs en.wikipedia.org and wikimedia.org (both reachable from the sandbox on 3 Oct 2026).
Findings (also in docs/04_research_and_evidence.md):
  List of Twenty20 International records            324,077 views/yr   men only, caption names Babar Azam / Rashid Khan
  List of women's Twenty20 International records     28,307 views/yr   (11.4x fewer)
  List of One Day International cricket records     314,930            hatnote: "about men's ODI records"
  List of women's One Day International records     150,969            (2.1x fewer)
  Cricket World Cup 2,252,198  vs  Women's Cricket World Cup 2,858,656  (counter-evidence: events do draw interest)
"""
import json, re, urllib.request, urllib.parse

UA = {"User-Agent": "ICC-hackathon-research/0.1 (student project)"}

def get(url):
    return json.load(urllib.request.urlopen(urllib.request.Request(url, headers=UA), timeout=30))

PAIRS = [
    ("List of Twenty20 International records", "List of Women's Twenty20 International records"),
    ("List of One Day International cricket records", "List of Women's One Day International records"),
    ("Cricket World Cup", "Women's Cricket World Cup"),
    ("T20 World Cup", "Women's T20 World Cup"),
    ("Twenty20 International", "Women's Twenty20 International"),
    ("One Day International", "Women's One Day International"),
]

def info(title):
    q = get("https://en.wikipedia.org/w/api.php?" + urllib.parse.urlencode({
        "action": "query", "titles": title, "redirects": 1, "prop": "extracts",
        "exintro": 1, "explaintext": 1, "exsentences": 2, "format": "json"}))
    page = list(q["query"]["pages"].values())[0]
    resolved = page.get("title")
    try:
        pv = get("https://wikimedia.org/api/rest_v1/metrics/pageviews/per-article/en.wikipedia/all-access/user/"
                 + urllib.parse.quote(resolved.replace(" ", "_"), safe="") + "/monthly/20250901/20260831")
        views = sum(i["views"] for i in pv["items"])
    except Exception:
        views = None
    return resolved, q["query"].get("redirects"), views, (page.get("extract") or "")[:220].replace("\n", " ")

def wikitext(title):
    u = "https://en.wikipedia.org/w/api.php?" + urllib.parse.urlencode(
        {"action": "parse", "page": title, "prop": "wikitext", "format": "json", "redirects": 1})
    return get(u)["parse"]["wikitext"]["*"]

if __name__ == "__main__":
    rows = []
    for men, women in PAIRS:
        a, b = info(men), info(women)
        rows.append((men, a, women, b))
        print(f"\nUNQUALIFIED: {men} -> {a[0]} views12m={a[2]}\n  lead: {a[3]}")
        print(f"WOMEN:       {women} -> {b[0]} views12m={b[2]}\n  lead: {b[3]}")
    json.dump(rows, open("wiki_audit.json", "w"), indent=1, default=str)

    for t in ["List of Twenty20 International records", "List of One Day International cricket records"]:
        s = wikitext(t)
        print("\n==", t, len(s))
        print(" first 400 chars:", re.sub(r"\s+", " ", s[:400]))
        for k in ["women", "Women", "Mandhana", "Bates", "427", "Argentina", "Rohmalia", "Babar", "Zimbabwe", "344", "Syazrul"]:
            print(f"  {k}: {len(re.findall(k, s))}", end=";")
        print()
