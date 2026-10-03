"""
Pull the records tables used to build data/records_v1.csv.
Ran on 3 Oct 2026. Fetches 8 Wikipedia pages (HTML via the parse API), saves them next to this script,
prints each page's last-edit timestamp, and prints the top rows of the key tables.

Pages: men's/women's T20I records, men's/women's ODI records, Cricket World Cup, Women's Cricket World Cup,
       Men's T20 World Cup, Women's T20 World Cup.
Why Wikipedia as primary: it is the only free source that lists men's AND women's records in one structured form.
Why it is NOT enough alone: dynamic rows must be cross-checked (see docs/10_data_and_records.md, verification V1/V2).
Needs: pip install beautifulsoup4
"""
import json, re, urllib.request, urllib.parse
from bs4 import BeautifulSoup

UA = {"User-Agent": "ICC-hackathon-research/0.1 (student project)"}
PAGES = {
    "m_t20i": "List of Twenty20 International records",
    "w_t20i": "List of women's Twenty20 International records",
    "m_odi": "List of One Day International cricket records",
    "w_odi": "List of women's One Day International cricket records",
    "m_wc": "Cricket World Cup",
    "w_wc": "Women's Cricket World Cup",
    "m_t20wc": "ICC Men's T20 World Cup",
    "w_t20wc": "Women's T20 World Cup",
}

def get(u):
    return urllib.request.urlopen(urllib.request.Request(u, headers=UA), timeout=60).read().decode("utf-8", "ignore")

def fetch_all():
    for k, t in PAGES.items():
        u = "https://en.wikipedia.org/w/api.php?" + urllib.parse.urlencode(
            {"action": "parse", "page": t, "prop": "text|revid", "format": "json", "redirects": 1})
        d = json.loads(get(u))["parse"]
        open(k + ".html", "w", encoding="utf-8").write(d["text"]["*"])
        print(k, d["title"], "rev", d["revid"], len(d["text"]["*"]))

def last_edits():
    for t in PAGES.values():
        u = "https://en.wikipedia.org/w/api.php?" + urllib.parse.urlencode(
            {"action": "query", "titles": t, "prop": "revisions", "rvprop": "timestamp|ids", "format": "json", "redirects": 1})
        p = list(json.loads(get(u))["query"]["pages"].values())[0]
        print(p["title"], "| last edit", p["revisions"][0]["timestamp"])

def soup(k):
    return BeautifulSoup(open(k + ".html", encoding="utf-8").read(), "html.parser")

def table_after_heading(s, pattern):
    for h in s.find_all(["h2", "h3", "h4"]):
        t = h.get_text(" ", strip=True)
        if re.search(pattern, t, re.I):
            node = h.parent if h.parent and "mw-heading" in " ".join(h.parent.get("class", [])) else h
            return t, node.find_next("table")
    return None, None

def top_rows(tb, n=3):
    return [" | ".join(re.sub(r"\s+", " ", c.get_text(" ", strip=True)) for c in tr.find_all(["th", "td"]))[:210]
            for tr in tb.find_all("tr")[: n + 1]]

SPEC = {
    "m_t20i": [r"^Highest innings totals$", r"^Most career runs$", r"^Highest individual score$", r"^Most wickets$", r"^Best bowling figures$", r"^Most matches$"],
    "w_t20i": [r"^Highest.*total", r"^Most career runs$", r"^Highest individual score$", r"^Most wickets in career$", r"^Best figures in a match$", r"^Most matches played$"],
    "m_odi": [r"^Highest.*totals?$", r"^Most career runs$|^Most runs$", r"^Highest individual score$", r"^Most wickets$", r"^Best innings figures$", r"^Most matches", r"^Most (career )?centuries"],
    "w_odi": [r"Highest.*total", r"^Most career runs$|^Most runs", r"^Highest scores$", r"^Most wickets in career$", r"Best bowling", r"^Most matches", r"^Most (career )?centuries"],
}

def infobox(k):
    ib = soup(k).find("table", class_=re.compile("infobox"))
    if not ib:
        return
    for tr in ib.find_all("tr"):
        th, td = tr.find("th"), tr.find("td")
        if th and td and re.search(r"(?i)first|latest|most|successful|current|champion|winner", th.get_text(" ", strip=True)):
            print(f"  {th.get_text(' ', strip=True)}: {re.sub(chr(10), ' ', td.get_text(' ', strip=True))[:200]}")

if __name__ == "__main__":
    fetch_all(); last_edits()
    for k, pats in SPEC.items():
        s = soup(k); print("\n=====", k)
        for p in pats:
            t, tb = table_after_heading(s, p)
            print("--", p, "->", t)
            if tb is not None:
                for r in top_rows(tb): print("   ", r)
    for k in ["m_wc", "w_wc", "m_t20wc", "w_t20wc"]:
        print("\n=====", k); infobox(k)
