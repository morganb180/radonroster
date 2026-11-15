"""Pull the hiring/how-to copy that the redesign dropped from county and city pages into copy.json.

Reads the pre-redesign pages straight from git (default ref 17ee1d1, main before PR #4), so it can run any time.
Keeps the editorial copy (quick answer, hiring steps, borders, guides, "what to check", cost, data notes) and drops what
the new layout already shows (firm lists, quote form, stat panel, FAQ, filters). Output is committed; build.py reads it.
Needs bs4 + lxml (only this script)."""
import json, os, re, subprocess, sys
from bs4 import BeautifulSoup

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
REF = sys.argv[1] if len(sys.argv) > 1 else "17ee1d1"
D = json.load(open(os.path.join(ROOT, "tools", "redesign", "data.json")))
ORDER_OLD = re.compile(r"ordered by (?:town, then name|location and name)", re.I)


def old(path):
    return subprocess.run(["git", "-C", ROOT, "show", f"{REF}:{path}"], capture_output=True, text=True, check=True).stdout


def clean(html, kind):
    s = BeautifulSoup(html, "lxml")
    m = s.find("main")
    for sel in ["nav.crumbs", "h1", "nav.toc", "nav.tabs", "section.sec", "div.firms", "div.qinline", "form",
                "details.faq", "div.cmp", "div.kpis", "script", "svg"]:
        for t in m.select(sel):
            t.decompose()
    # FAQ headings (the FAQ itself is rendered by build.py from data.json)
    for h in m.find_all("h2"):
        if re.search(r"frequently asked questions", h.get_text(), re.I):
            h.decompose()
    # The stat panel's heading ("X radon test data") and its bar caption: build.py renders its own stat card.
    for h in m.find_all(["h2", "p"]):
        if re.search(r"radon test data$|Share of basement tests ≥", h.get_text().strip()):
            h.decompose()
    # "Below are the firms ... then ..." describes the old list order; the new list is sorted by rating.
    for p in m.find_all("p"):
        if p.get_text().strip().startswith("Below are the PA DEP-certified firms"):
            p.decompose()
    # Firm-count headings lose their lists, so step them down to h3 (ids kept for old deep links).
    for h in m.find_all("h2"):
        if re.search(r"\(\d+(?: firms?)?\)\s*$", h.get_text()):
            h.name = "h3"
    out = []
    for t in m.find_all(["h2", "h3", "p", "ul", "ol", "div"], recursive=True):
        pass
    body = "".join(str(c) for c in m.contents)
    # unwrap old layout containers; keep content
    b = BeautifulSoup(body, "lxml").body
    for d in b.find_all(["div", "aside"]):
        cls = " ".join(d.get("class", []))
        if "answer" in cls or "hotline" in cls:
            continue
        d.unwrap()
    html = "".join(str(c) for c in b.contents)
    html = re.sub(r"<p[^>]*>\s*</p>", "", html)
    html = re.sub(r"\s+\n|\n\s+", "\n", html).strip()
    html = ORDER_OLD.sub("sorted by Google rating", html)
    return html


def main():
    out = {"ref": REF, "county": {}, "city": {}}
    for slug in D["counties"]:
        p = f"pa/county/{slug}/index.html"
        try:
            out["county"][slug] = clean(old(p), "county")
        except subprocess.CalledProcessError:
            pass
    for slug in D["cities"]:
        p = f"pa/city/{slug}/index.html"
        try:
            out["city"][slug] = clean(old(p), "city")
        except subprocess.CalledProcessError:
            pass
    json.dump(out, open(os.path.join(ROOT, "tools", "redesign", "copy.json"), "w"), ensure_ascii=False, indent=0)
    print(f"copy.json: {len(out['county'])} counties, {len(out['city'])} cities from {REF}")


if __name__ == "__main__":
    main()
