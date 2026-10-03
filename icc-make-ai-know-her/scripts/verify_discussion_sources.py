"""
Verify the sources cited in source_docs/discussion_make_ai_know_her_master.md (Sir Jabin's research doc).
Ran on 3 Oct 2026: fetched each URL, stripped HTML, and searched for the exact numbers/phrases the doc claims.
Result: 20 of 22 verified, 2 mislabelled, 0 wrong (see docs/04_research_and_evidence.md section 3).
Run:  python verify_discussion_sources.py   (writes <name>.raw files, prints keyword context)
PDFs need: pip install pdfplumber
"""
import re, html, subprocess, json, urllib.request

URLS = {
 "google": "https://blog.google/products-and-platforms/products/search/how-were-making-it-easier-to-find-results-on-womens-sports/",
 "mandhana_icc": "https://www.icc-cricket.com/news/star-batter-mandhana-sets-historic-milestone-in-women-s-t20is",
 "icc100": "https://www.icc-cricket.com/100percentcricket",   # returned 404 for the sandbox; the page exists at /100percentcricket/what-is-100percent-cricket
 "iccgoogle": "https://www.icc-cricket.com/news/icc-google-announce-partnership-to-elevate-women-s-cricket",
 "cwc_digital": "https://www.icc-cricket.com/tournaments/womens-cricket-worldcup-2025/news/icc-women-s-cricket-world-cup-2025-sets-unprecedented-global-digital-engagement-records",
 "cwc_final": "https://www.icc-cricket.com/tournaments/womens-cricket-worldcup-2025/news/cwc25-final-draws-benchmark-viewership-figures",
 "pew": "https://www.pewresearch.org/internet/2026/06/17/how-opinions-and-use-of-ai-differ-by-age/",
 "deloitte": "https://www.deloitte.com/uk/en/about/press-room/womens-elite-sports-revenues-2026.html",
 "nielsen": "https://www.nielsen.com/insights/2026/women-sports/",
 "nielsen_fb": "https://www.nielsen.com/news-center/2025/womens-football-set-to-enter-global-top-5-sports-by-2030-with-over-800m-fans-nielsen-sports-and-pepsico-report-reveals-untapped-opportunity-for-brands/",
 "persian": "https://aclanthology.org/2025.winlp-main.3/",
 "cricsheet": "https://cricsheet.org/downloads/",
 "tigzig": "https://mcp.tigzig.com/post/cricket-womens-data-added-sep2026",
 "statsperform": "https://www.statsperform.com/womens-sports/",
 "cricketsky": "https://www.cricketsky.com/babar-azam-p874/",
 "sangri": "https://en.sangritimes.com/sports/smriti-mandhana-becomes-leading-t20i-run-scorer",
 "iccpdf1": "https://images.icc-cricket.com/image/upload/prd/hcueaghytzn8htllwelt.pdf",  # actually ICC Annual Report 2022-23 (doc labels it "strategy")
 "iccpdf2": "https://images.icc-cricket.com/image/upload/prd/bisel0ksrxtscf16t2wu.pdf",  # actually ICC Annual Report 2021-22
 "naacl": "https://aclanthology.org/2025.naacl-short.17/",
}
CHECKS = {
 "google": ["cricket captain", "India", "German", "Hindi", "women"],
 "mandhana_icc": ["4788", "4,788", "4758", "4,758", "Babar"],
 "cwc_digital": ["5.2", "279", "8.5"],
 "cwc_final": ["185", "JioHotstar", "2024"],
 "pew": ["61%", "54%", "ChatGPT", "Gemini", "Copilot", "Meta AI"],
 "deloitte": ["3 billion", "US$3"],
 "nielsen": ["46 billion", "71%"],
 "nielsen_fb": ["800"],
 "persian": ["sport", "GPT-4o", "Persian"],
 "cricsheet": ["22,983", "4,667", "611", "2,171"],
 "cricketsky": ["4596", "4,596"],
 "sangri": ["4788", "4596", "Babar", "Mandhana"],
}
REPOS = ["ankitksr/duckworth-mcp", "asaraog/mcp-cricket", "backspace-me/sportscore-mcp", "i-m-arul/cricketstudio-mcp"]
UA = "Mozilla/5.0 (Windows NT 10.0; Win64; x64) AppleWebKit/537.36 Chrome/126 Safari/537.36"

def fetch(name, url):
    req = urllib.request.Request(url, headers={"User-Agent": UA})
    try:
        data = urllib.request.urlopen(req, timeout=40).read()
    except Exception as e:
        print(name, "ERR", e); return ""
    open(name + ".raw", "wb").write(data)
    return data.decode("utf-8", "ignore")

def text(s):
    s = re.sub(r"(?is)<(script|style)[^>]*>.*?</\1>", " ", s)
    return re.sub(r"\s+", " ", html.unescape(re.sub(r"<[^>]+>", " ", s)))

if __name__ == "__main__":
    for n, u in URLS.items():
        t = text(fetch(n, u))
        print("\n=====", n, len(t))
        for k in CHECKS.get(n, []):
            hits = [m.start() for m in re.finditer(re.escape(k), t)][:1]
            print(f"  [{k}]", "FOUND ..." + t[max(0, hits[0]-120):hits[0]+160] + "..." if hits else "NOT FOUND")
    for r in REPOS:   # existence + description of the cited MCP repos
        try:
            d = json.load(urllib.request.urlopen(urllib.request.Request("https://api.github.com/repos/" + r, headers={"User-Agent": "x"}), timeout=30))
            print(r, "|", d.get("description"), "|", d.get("pushed_at"))
        except Exception as e:
            print(r, "ERR", e)
