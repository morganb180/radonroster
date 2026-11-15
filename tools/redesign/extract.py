"""Collect everything the new templates need into tools/redesign/data.json.

Sources, all already in this repo:
  api/firms.json, api/county/*.json, api/city/*.json   -> firms, listings per place
  pa/radon-levels-by-county/index.html                  -> county radon stats
  pa/firms/<slug>/index.html                            -> address, people, Google reviews
  pa/county|city/<slug>/index.html                      -> FAQ (JSON-LD), neighbours, city stats
Run from the repo root: python3 tools/redesign/extract.py
"""
import glob, html, json, os, re

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
P = lambda *a: os.path.join(ROOT, *a)


def read(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


def text(x):
    return html.unescape(re.sub(r"<[^>]+>", "", x)).strip()


def num(x):
    return float(x.replace(",", "").replace("%", "")) if x else None


def ldjson(page, typ):
    for m in re.finditer(r'<script type="application/ld\+json">(.*?)</script>', page, re.S):
        try:
            d = json.loads(m.group(1))
        except Exception:
            continue
        if d.get("@type") == typ:
            return d
    return None


# ---------- firms ----------
firms = {}
for f in json.load(open(P("api", "firms.json")))["firms"]:
    slug = f["firm_url"].rstrip("/").split("/")[-1]
    rec = {
        "id": f["id"], "slug": slug, "raw_name": f["name"], "city": f["city"],
        "state": f.get("state", "PA"),
        "county": (f.get("county") or {}).get("name", ""), "county_slug": (f.get("county") or {}).get("slug", ""),
        "services": f["services"], "ids": [c["text"] for c in f["credentials"]],
        "rating": (f.get("google_rating") or {}).get("rating"),
        "reviews": (f.get("google_rating") or {}).get("count") or 0,
        "rating_as_of": (f.get("google_rating") or {}).get("as_of"),
        "source": f["source"]["urls"], "retrieved": f["source"]["retrieved"],
        "listed_on": [], "address": "", "people": [], "quotes": [], "maps": "",
    }
    fp = P("pa", "firms", slug, "index.html")
    if os.path.exists(fp):
        s = read(fp)
        m = re.search(r"<h4>Address</h4>(.*?)</li>", s, re.S)
        rec["address"] = text(m.group(1)) if m else ""
        sec = s[s.find("Certified individuals"):]
        sec = sec[: sec.find("</ul>")]
        rec["people"] = [[text(a), text(b)] for a, b in re.findall(r"<li>(.*?)<span class=\"muted\">\((.*?)\)</span>", sec)]
        for q, who, ago in re.findall(r'<blockquote class="grev"><p>(.*?)</p><footer>.*?<a [^>]*>(.*?)</a> · (.*?)</footer>', s, re.S):
            rec["quotes"].append({"text": text(q), "who": text(who), "ago": text(ago)})
        m = re.search(r'href="(https://maps\.google\.com/\?cid=[^"]+)"', s)
        rec["maps"] = html.unescape(m.group(1)) if m else ""
        lo = s[s.find("<h2>Listed on</h2>"):]
        lo = lo[: lo.find("</section>")]
        rec["listed_on"] = [[html.unescape(h), text(t)] for h, t in re.findall(r'<a href="([^"]+)">(.*?)</a>', lo)]
    firms[f["id"]] = rec

# ---------- counties ----------
counties = {}
s = read(P("pa", "radon-levels-by-county", "index.html"))
for r in re.findall(r"<tr[^>]*>(.*?)</tr>", s, re.S):
    cells = [text(c) for c in re.findall(r"<t[dh][^>]*>(.*?)</t[dh]>", r, re.S)]
    if len(cells) < 7 or not cells[0].isdigit():
        continue
    rank, name, tests, median, pb, pf, nf = cells[:7]
    slug = re.sub(r"[^a-z]+", "-", name.lower()).strip("-")
    counties[slug] = {"slug": slug, "name": name, "rank": int(rank), "tests": int(num(tests) or 0),
                      "median": num(median), "pct": num(pb), "pct_first": num(pf), "firm_count": int(num(nf) or 0)}

for p in sorted(glob.glob(P("api", "county", "*.json"))):
    d = json.load(open(p))
    c = counties.setdefault(d["slug"], {"slug": d["slug"], "name": d["slug"].title()})
    c["firms"] = [f["id"] for f in d["firms"]]
    c["local_count"] = d.get("local_count")
    page = read(P("pa", "county", d["slug"], "index.html"))
    faq = ldjson(page, "FAQPage")
    c["faq"] = [[q["name"], q["acceptedAnswer"]["text"]] for q in (faq or {}).get("mainEntity", [])]
    i = page.find('<h2 id="which-counties-border')
    nb = page[i: page.find("</p>", i)] if i > 0 else ""
    c["neighbors"] = [x for x in dict.fromkeys(re.findall(r"href='/pa/county/([a-z-]+)/'", nb)) if x != d["slug"]]
    j = page.rfind("cities-have-radon-roster-pages")
    c["cities"] = list(dict.fromkeys(re.findall(r"href='/pa/city/([a-z0-9-]+)/'", page[j: j + 3000]))) if j > 0 else []

# ---------- cities ----------
cities = {}
for p in sorted(glob.glob(P("api", "city", "*.json"))):
    d = json.load(open(p))
    page = read(P("pa", "city", d["slug"], "index.html"))
    main = text(re.search(r"<main.*?</main>", page, re.S).group(0))
    name = re.sub(r"^Radon testing & mitigation in ", "", d["name"]).replace(", PA", "")
    m = re.search(r"([\d.]+)% of ([\d,]+) basement radon tests", main)
    med = re.search(r"median was\s*([\d.]+) pCi/L", main)
    cm = re.search(r"sits in ([A-Za-z ]+?) County", main)
    faq = ldjson(page, "FAQPage")
    guide = re.search(r"href='(/pa/city/[a-z0-9-]+/radon-guide/)'", page)
    cities[d["slug"]] = {
        "slug": d["slug"], "name": name, "pct": num(m.group(1)) if m else None, "tests": int(num(m.group(2))) if m else None,
        "median": num(med.group(1)) if med else None, "county": cm.group(1) if cm else "",
        "county_slug": re.sub(r"[^a-z]+", "-", (cm.group(1) if cm else "").lower()).strip("-"),
        "firms": [f["id"] for f in d["firms"]], "local_count": d.get("local_count"),
        "faq": [[q["name"], q["acceptedAnswer"]["text"]] for q in (faq or {}).get("mainEntity", [])],
        "guide": guide.group(1) if guide else "",
    }

# Display names already cleaned by the generator ("Barrick, Darrell" -> "Darrell Barrick").
q = read(P("quotes", "index.html"))
m = re.search(r"window\.RR_FIRMS=(\{.*?\});", q, re.S)
clean = json.loads(m.group(1)) if m else {}
SUFFIX = {"jr": "Jr.", "jr.": "Jr.", "sr": "Sr.", "sr.": "Sr.", "ii": "II", "iii": "III", "iv": "IV"}
BIZ = re.compile(r"\b(inc|llc|co|corp|company|services?|inspections?|radon|home|homes|consultants?|technical|labs?|laboratories|environmental|mechanical|group|solutions|associates|testing|systems|\.com)\b", re.I)


def display(n):
    n = n.strip()
    if "," in n and not BIZ.search(n):  # "Casciato, Jr., Daniel" -> "Daniel Casciato Jr."
        parts = [x.strip() for x in n.split(",") if x.strip()]
        last, rest, suf = parts[0], [], []
        for x in parts[1:]:
            (suf if x.lower() in SUFFIX else rest).append(SUFFIX.get(x.lower(), x))
        n = " ".join(rest + [last] + suf)
    n = re.sub(r",?\s+(LLC\.?|L\.L\.C\.|Inc\.?|Incorporated|Corp\.?|Co\.)$", "", n, flags=re.I)
    n = re.sub(r"\.Com\b", ".com", n)
    n = re.sub(r"\b(Usa|Llc|Pa|Nj|Ny)\b", lambda m: m.group(1).upper(), n)
    n = re.sub(r"\b([B-DF-HJ-NP-TV-Z][b-df-hj-np-tv-z]{1,3})\b", lambda m: m.group(1) if m.group(1) in ("St", "Mr", "Dr", "Jr", "Sr", "Mc", "Ms", "Mt", "Rn") else m.group(1).upper(), n)  # vowel-less initialisms: Jk, Bpg
    n = re.sub(r"(?<=\w )(Of|And|The|In)(?= )", lambda m: m.group(1).lower(), n)
    return n


names = [f["raw_name"] for f in firms.values()]
for fid, f in firms.items():
    base = clean.get(fid) or f["raw_name"]
    if len(f["raw_name"]) in (20, 21):  # DEP truncates names; borrow the full one if another listing has it
        longer = [x for x in names if x != f["raw_name"] and x.startswith(f["raw_name"].rstrip())]
        if len(longer) == 1:
            base = longer[0]
    f["name"] = display(base)
    f["legal_name"] = f["raw_name"]

out = {"firms": firms, "counties": counties, "cities": cities}
json.dump(out, open(P("tools", "redesign", "data.json"), "w"), indent=0)
print(f"firms {len(firms)} · counties {len(counties)} · cities {len(cities)}")
print("firms with address", sum(1 for f in firms.values() if f["address"]), "· with quotes", sum(1 for f in firms.values() if f["quotes"]))
print("counties with stats", sum(1 for c in counties.values() if c.get("pct") is not None), "· with neighbours", sum(1 for c in counties.values() if c.get("neighbors")))
print("cities with pct", sum(1 for c in cities.values() if c["pct"] is not None), "· guide", sum(1 for c in cities.values() if c["guide"]))
