"""Radon Roster v2 templates. Rewrites the directory pages in place from tools/redesign/data.json.

  python3 tools/redesign/extract.py   # once, before the first build (reads the current pages)
  python3 tools/redesign/build.py     # home, quotes, 67 counties, 40 cities, 413 firms, + new shell on every other page

Each page keeps its own <head> (title, description, canonical, OG, JSON-LD) so URLs and SEO stay put;
only the stylesheet and scripts are swapped and the <body> is re-rendered.
"""
import glob, hashlib, html, json, os, re

ROOT = os.path.abspath(os.path.join(os.path.dirname(__file__), "..", ".."))
P = lambda *a: os.path.join(ROOT, *a)
D = json.load(open(P("tools", "redesign", "data.json")))
FIRMS, COUNTIES, CITIES = D["firms"], D["counties"], D["cities"]

DEFAULT_SORT = "rating"   # "rating" (Google rating, weighted by review count) or "town" (the old location-and-name order)
LIST_DATE = "Oct 1, 2026"  # date on the PA DEP lists
RATING_DATE = "Oct 18, 2026"
HOTLINE = "800-237-2366"
DEP_DIR = "https://www.pa.gov/agencies/dep/programs-and-services/radiation-protection/radon-division/radon-services-directory"
FUNNEL = "/quotes/"


def e(x):
    return html.escape(str(x if x is not None else ""), quote=True)


def read(p):
    with open(p, encoding="utf-8") as f:
        return f.read()


def write(p, s):
    with open(p, "w", encoding="utf-8") as f:
        f.write(s)


# ---------------------------------------------------------------- icons
def ic(name, size=20):
    paths = {
        "check": '<path d="M5 12.5l4.2 4.2L19 7" />',
        "shield": '<path d="M12 3l7 3v5.5c0 4.3-2.9 8.1-7 9.5-4.1-1.4-7-5.2-7-9.5V6z"/><path d="M8.8 12l2.2 2.2 4.3-4.4"/>',
        "test": '<rect x="6" y="3" width="12" height="18" rx="3"/><path d="M9 7h6M9 17h6"/><circle cx="12" cy="12" r="2.2"/>',
        "fix": '<path d="M4 20V10l8-6 8 6v10"/><path d="M15 20V8.5"/><path d="M15 6V3h2v4.2"/><path d="M9 20v-5h3"/>',
        "kit": '<path d="M3 8l9-5 9 5v8l-9 5-9-5z"/><path d="M3 8l9 5 9-5M12 13v8"/>',
        "result": '<path d="M4 18a8 8 0 1116 0"/><path d="M12 18l4-6"/><circle cx="12" cy="18" r="1.4"/>',
        "unsure": '<circle cx="12" cy="12" r="9"/><path d="M9.6 9.3a2.5 2.5 0 114 2c-.9.6-1.6 1.1-1.6 2.2"/><circle cx="12" cy="17" r=".6"/>',
        "search": '<circle cx="11" cy="11" r="6.5"/><path d="M16 16l4.5 4.5"/>',
        "nopay": '<circle cx="12" cy="12" r="9"/><path d="M5.6 5.6l12.8 12.8"/><path d="M14.5 9.2c-.5-.8-1.4-1.2-2.5-1.2-1.6 0-2.6.8-2.6 2 0 2.6 5.3 1.4 5.3 4 0 1.2-1.1 2-2.7 2-1.2 0-2.2-.5-2.7-1.4M12 6.5V8m0 8v1.5"/>',
        "free": '<path d="M4 12h16M12 4v16" transform="rotate(45 12 12)"/><rect x="3" y="3" width="18" height="18" rx="5"/>',
        "pin": '<path d="M12 21s7-6.2 7-11.5A7 7 0 005 9.5C5 14.8 12 21 12 21z"/><circle cx="12" cy="9.5" r="2.5"/>',
        "ext": '<path d="M14 5h5v5M19 5l-8 8M18 14v5H5V6h5"/>',
        "arrow": '<path d="M5 12h14M13 6l6 6-6 6"/>',
        "user": '<circle cx="12" cy="8" r="4"/><path d="M4 21c1.5-4 4.5-6 8-6s6.5 2 8 6"/>',
        "chat": '<path d="M4 5h16v11H9l-5 4z"/>',
        "clock": '<circle cx="12" cy="12" r="9"/><path d="M12 7v5l3 2"/>',
    }
    return (f'<svg width="{size}" height="{size}" viewBox="0 0 24 24" fill="none" stroke="currentColor" '
            f'stroke-width="1.7" stroke-linecap="round" stroke-linejoin="round" aria-hidden="true">{paths[name]}</svg>')


STAR = '<svg viewBox="0 0 24 24" aria-hidden="true"><path fill="currentColor" d="M12 2.5l2.9 6.1 6.6.8-4.9 4.6 1.3 6.6L12 17.3l-5.9 3.3 1.3-6.6L2.5 9.4l6.6-.8z"/></svg>'


def rating(f, long=False):
    if not f.get("rating"):
        return '<span class="rating"><span class="n">No reviews yet</span></span>'
    n = f["reviews"]
    lab = f"{n:,} review{'s' if n != 1 else ''}" if long else f"({n:,})"
    return (f'<span class="rating" aria-label="Rated {f["rating"]} out of 5 from {n:,} Google reviews">{STAR}'
            f'{f["rating"]:.1f} <span class="n">{lab}</span></span>')


def initials(name):
    w = [x for x in re.split(r"[\s\-]+", re.sub(r"[^A-Za-z0-9 \-]", "", name)) if x and x.lower() not in ("a", "the", "of", "and")]
    return ((w[0][0] + (w[1][0] if len(w) > 1 else "")) if w else "?").upper()


def tone(name):
    return "c" + str(int(hashlib.md5(name.encode()).hexdigest(), 16) % 6)


def score(f):
    r, n = f.get("rating"), f.get("reviews") or 0
    return (r * n + 4.3 * 5) / (n + 5) if r else 0


SVC = {"mitigation": ("Mitigation", "fix"), "testing": ("Testing", ""), "lab": ("Lab kits", "")}


def tags(f):
    return "".join(f'<span class="tag {SVC[s][1]}">{SVC[s][0]}</span>' for s in ("mitigation", "testing", "lab") if s in f["services"])


def svc_code(f):
    return "".join({"mitigation": "m", "testing": "t", "lab": "l"}[s] for s in f["services"])


def top_rated(f):
    return (f.get("rating") or 0) >= 4.5 and (f.get("reviews") or 0) >= 20


def radon_quote(f):
    """A review snippet only when it is about radon work; general home-inspection reviews don't help here."""
    for q in f.get("quotes", []):
        if re.search(r"radon|mitigat", q["text"], re.I):
            t = q["text"]
            t = t if len(t) <= 130 else t[:128].rsplit(" ", 1)[0] + "…"
            return t, q["who"].split()[0]
    return None


def person_initials(n):
    return initials(person_name(n))


AGO = re.compile(r"(a|an|\d+) (minute|hour|day|week|month|year)s? ago")
AGO_DAYS = {"minute": 0, "hour": 0, "day": 1, "week": 7, "month": 30, "year": 365}


def latest_review(f):
    """Newest of the Google reviews we hold, as (days, text). None when there are none."""
    best = None
    for q in f.get("quotes", []):
        m = AGO.search(q.get("ago", ""))
        if not m:
            continue
        n = 1 if m.group(1) in ("a", "an") else int(m.group(1))
        days = n * AGO_DAYS[m.group(2)]
        if best is None or days < best[0]:
            best = (days, q["ago"])
    return best


def kind(f):
    """What sort of business this is, from its name only. Blank when the name doesn't say."""
    n = f.get("legal_name") or f["name"]
    if re.search(r"radon|mitigat", n, re.I):
        return "Radon company"
    if re.search(r"inspect", n, re.I):
        return "Home inspection company"
    return ""


def what_they_do(f):
    sv = set(f["services"])
    if {"mitigation", "testing"} <= sv:
        return "fix", "Tests, installs and retests"
    if "mitigation" in sv:
        return "fix", "Installs radon systems"
    if "lab" in sv:
        return "kit", "Certified radon lab"
    return "test", "Testing only, no system to sell you"


def firm_card(f, here_county=None, vertical=False):
    loc = f["city"] + (f", {f['state']}" if f.get("state") and f["state"] != "PA" else "")
    if f.get("county") and f["county_slug"] != here_county:
        nb = COUNTIES.get(here_county or "", {}).get("neighbors", [])
        loc += f" · {f['county']} County" + (" (next door)" if f["county_slug"] in nb else "")
    k = kind(f)
    if k:
        loc = f"{k} · {loc}"
    first_id = (f["ids"][0].split("#")[-1]) if f["ids"] else ""
    tr = top_rated(f)
    if f.get("rating"):
        pct = f["rating"] / 5 * 100
        score_html = (f'<div class="score{" hi" if tr else ""}"><b class="num">{f["rating"]:.1f}</b>'
                      f'<span class="st" style="--p:{pct:.0f}%" aria-hidden="true">★★★★★</span>'
                      f'<small class="num">{f["reviews"]:,} review{"s" if f["reviews"] != 1 else ""}</small></div>')
    else:
        score_html = '<div class="score none"><small>No reviews yet</small></div>'
    q = radon_quote(f)
    quote_html = f'<blockquote>“{e(q[0])}”<cite>{e(q[1])}, on Google</cite></blockquote>' if q else ""
    ppl = f.get("people") or []
    faces = "".join(f'<i class="{tone(n)}">{e(person_initials(n))}</i>' for n, _ in ppl[:3])
    if len(ppl) > 3:
        faces += f"<em>+{len(ppl) - 3}</em>"
    icn, does = what_they_do(f)
    facts = [f'<li>{ic(icn, 16)}{does}</li>']
    if ppl:
        n = len(ppl)
        facts.append(f'<li>{ic("user", 16)}{"Solo certified tech" if n == 1 else f"{n} certified techs"}</li>')
    lr = latest_review(f)
    if lr:
        facts.append(f'<li>{ic("clock", 16)}Latest review {e(lr[1])}</li>')
    return (
        f'<article class="pcard{" v" if vertical else ""}{" tr" if tr else ""}" data-svc="{svc_code(f)}" data-score="{score(f):.4f}" '
        f'data-r="{f.get("rating") or 0}" data-n="{f.get("reviews") or 0}" data-top="{1 if tr else 0}" data-name="{e(f["name"].lower())}" data-town="{e(f["city"].lower())}">'
        + ('<span class="flagtr">Top rated</span>' if tr else "") +
        f'<div class="top">{score_html}<div class="who"><h3><a href="/pa/firms/{f["slug"]}/" data-fid="{f["id"]}" data-ct="card">{e(f["name"])}</a></h3>'
        f'<p class="loc">{e(loc)}</p></div></div>'
        f'<ul class="facts">{"".join(facts)}</ul>'
        f'{quote_html}'
        f'<div class="foot"><span class="faces">{faces}</span><span class="mono dep">DEP #{e(first_id)}</span></div></article>'
    )


def dedupe(ids):
    """One card per business: DEP lists sometimes carry the same firm two or three times."""
    seen, out = {}, []
    for i in ids:
        f = FIRMS.get(i)
        if not f:
            continue
        k = (re.sub(r"[^a-z0-9]", "", f["name"].lower()), f["city"].lower())
        if k in seen:
            continue
        seen[k] = i
        out.append(f)
    return out


def sort_firms(fs):
    if DEFAULT_SORT == "rating":
        return sorted(fs, key=lambda f: (-score(f), f["name"].lower()))
    return sorted(fs, key=lambda f: (f["city"].lower(), f["name"].lower()))


def lvl(pct):
    return "lvl-" + str(0 if pct < 30 else 1 if pct < 40 else 2 if pct < 50 else 3 if pct < 60 else 4)


EL = '<span class="el{cls}" aria-hidden="true"><i>86</i><b>Rn</b><s>Radon</s></span>'
MAP = json.load(open(P("tools", "redesign", "pa_map.json")))
RAMP = {"b0": "#f6e3c6", "b1": "#ebbd8c", "b2": "#d68c56", "b3": "#b35a2b", "b4": "#7a2c0c"}


def pa_map(cls, on=None, near=(), label="Pennsylvania counties shaded by share of high radon tests"):
    out = []
    for k, (b, d) in MAP.items():
        c = ' class="on"' if k == on else (' class="nb"' if k in near else "")
        out.append('<path d="' + d + '" fill="' + RAMP[b] + '"' + c + "/>")
    paths = "".join(out)
    return f'<svg class="{cls}" viewBox="0 0 800 462" role="img" aria-label="{e(label)}">{paths}</svg>'


# ---------------------------------------------------------------- shell
NAV = [("/pa/counties/", "Find a pro"), ("/pa/radon-levels-by-county/", "Radon levels"), ("/guides/", "Guides"), ("/radon-mitigation-cost/", "Costs")]


def header(active=""):
    nav = "".join(f'<a href="{u}"{" aria-current=page" if u == active else ""}>{t}</a>' for u, t in NAV)
    return f'''<a class="skip" href="#main">Skip to content</a>
<header class="hdr"><div class="wrap">
<a class="logo" href="/" aria-label="Radon Roster home">{EL.format(cls="")}Radon Roster</a>
<nav class="nav" aria-label="Main">{nav}</nav>
<a class="hlink" href="/for-contractors/">For radon pros</a>
<details class="menu"><summary aria-label="Menu"><i></i><b>Rn</b></summary><nav aria-label="Menu">
<a href="/quotes/"><strong>Get free quotes</strong></a><hr>{"".join(f'<a href="{u}">{t}</a>' for u, t in NAV)}
<a href="/what-is-radon/">What is radon?</a><hr><a href="/for-contractors/">For radon pros</a><a href="/claim-listing/">Claim your listing</a><a href="/about/">About</a></nav></details>
</div></header>'''


NETWORK = [("https://leadpaintroster.com/", "Lead Paint Roster"), ("https://moldroster.com/", "Mold Roster"), ("https://mnhomesalepros.com/", "MN Home Sale Pros"),
           ("https://njhomesalechecklist.com/", "NJ Home Sale Checklist"), ("https://title5roster.com/", "Title 5 Roster"), ("https://eastbaysewerinspection.com/", "East Bay Sewer Inspection")]


def footer():
    li = lambda u, t: '<li><a href="' + u + '">' + t + "</a></li>"
    col = lambda h, links: f'<div><h4>{h}</h4><ul>{"".join(li(u, t) for u, t in links)}</ul></div>'
    return f'''<footer class="ftr"><div class="wrap">
<p class="brand">{EL.format(cls="")}Radon Roster</p>
<div class="fcols">
{col("Find a pro", [("/pa/counties/", "All 67 counties"), ("/pa/cities/", "Cities"), ("/quotes/", "Get free quotes"), ("/pa/radon-map/", "Radon map"), ("/pa/radon-levels-by-county/", "Radon levels by county")])}
{col("Learn", [("/what-is-radon/", "What is radon?"), ("/testing-vs-mitigation/", "Testing vs. mitigation"), ("/radon-mitigation-cost/", "Mitigation cost"), ("/free-radon-test-kit-pennsylvania/", "Free test kits"), ("/pa/real-estate-radon-disclosure/", "Selling a home"), ("/guides/", "All guides")])}
{col("Radon Roster", [("/about/", "About"), ("/how-we-verify/", "How we verify pros"), ("/how-we-make-money/", "How we make money"), ("/about-our-data/", "Our data"), ("/privacy/", "Privacy"), ("/contact/", "Contact")])}
{col("For radon pros", [("/claim-listing/", "Claim or fix your listing"), ("/for-contractors/", "Advertising"), ("https://www.youtube.com/@radonroster", "YouTube")])}
</div>
<div class="fnote">
<p>Every listing comes from Pennsylvania DEP certification lists dated {LIST_DATE}. Radon Roster isn't part of PA DEP, and a listing isn't an endorsement. Pros can't pay to rank higher; any paid spot would be marked “Ad.”</p>
<p>Check any pro with the <a href="{DEP_DIR}">PA DEP Radon Services Directory</a> or the PA Radon Hotline, {HOTLINE}. General information, not medical or legal advice.</p>
<p>© 2026 Radon Roster · <a href="/sitemap.xml">Sitemap</a> · <a href="/llms.txt">llms.txt</a></p>
</div>
<div class="fnet"><span>More directories:</span>{"".join(f'<a href="{u}">{t}</a>' for u, t in NETWORK)}</div>
</div></footer>'''


OLD_CSS = re.compile(r'<link rel="stylesheet" href="/(?:theme|style)\.css">|<link rel="stylesheet" href="/assets/(?:trust|quote-boost)\.css">'
                     r'|<link rel="preload" href="/fonts/[^"]+"[^>]*>|<style>@font-face.*?</style>'
                     r'|<script src="/assets/(?:trust|quote-boost|quote-flow)\.js"[^>]*></script>')


def head(path):
    s = read(path)
    if 'href="/assets/rr.css"' in s:  # already rebuilt: keep the head we wrote
        return s[: s.find("<body")]
    h = s[: s.find("</head>")]
    h = OLD_CSS.sub("", h)
    h = h.replace('<meta name="theme-color" content="#f5f6f8">', '<meta name="theme-color" content="#ffffff">')
    h += ('<link rel="preload" href="/fonts/public-sans-var-latin.woff2" as="font" type="font/woff2" crossorigin>'
          '<link rel="stylesheet" href="/assets/rr.css"><script src="/assets/rr.js" defer></script></head>')
    return h


def page(path, body, active="", mbar=""):
    out = head(path) + ('<body class="has-mbar">' if mbar else "<body>") + header(active) + body + footer() + mbar + "</body></html>"
    write(path, out)


def mobile_bar(title, sub, href, label="Get quotes", loc="sticky_bar"):
    return (f'<div class="mbar" aria-label="Get quotes"><div class="t"><b>{e(title)}</b>{e(sub)}</div>'
            f'<a class="btn qbtn" data-ga-loc="{loc}" href="{href}">{e(label)}</a></div>')


def ask_card(title, text, href, button="Get free quotes", loc="side_card"):
    return f'''<aside class="ask"><h2>{e(title)}</h2><p>{text}</p>
<a class="btn block lg qbtn" data-ga-loc="{loc}" href="{href}">{e(button)}</a>
<p class="fine">Free · No obligation · About 1 minute</p>
<ul><li>{ic("shield", 16)}Only PA DEP-certified pros</li><li>{ic("user", 16)}You'll see who gets it</li><li>{ic("nopay", 16)}Pros can't pay to be picked</li></ul></aside>'''


def faq(items):
    return '<div class="qa">' + "".join(
        f'<details><summary>{e(q)}</summary><div class="a"><p>{a}</p></div></details>' for q, a in items) + "</div>"


# ---------------------------------------------------------------- home content (SEO / AEO)
DEP26 = "https://www.pa.gov/agencies/dep/newsroom/2026-01-12-dep-encourages-pennsylvanians-to-test-their-homes-for-radon-during-radon-action-month"
SHORT_ANSWERS = [
    ("How much does radon mitigation cost in Pennsylvania?",
     "Most radon mitigation systems in Pennsylvania cost $800 to $1,200, according to PA DEP. Nationally, HomeAdvisor's 2026 guide puts the average at $1,028. The price depends on your foundation, how many suction points the house needs and where the pipe runs, so get written quotes from two DEP-certified mitigators.",
     ("PA DEP, 2026", DEP26), ("Radon mitigation cost guide", "/radon-mitigation-cost/")),
    ("How much does a radon test cost?",
     "A do-it-yourself test kit costs about $20 to $30, according to PA DEP. A professional test costs about $150 to $800 nationally (HomeAdvisor, 2026). If you've never tested your Pennsylvania home, you may qualify for a free kit from the American Lung Association and PA DEP while supplies last.",
     ("PA DEP", "https://www.pa.gov/agencies/dep/programs-and-services/radiation-protection/radon-division/radon-in-the-home"), ("Free PA test kits", "/free-radon-test-kit-pennsylvania/")),
    ("Do radon testers and mitigators need to be certified in Pennsylvania?",
     "Yes. Pennsylvania requires anyone who tests for radon, installs mitigation systems or analyzes radon samples for the public to be certified by PA DEP and to show a current DEP photo ID card on request. Every pro on Radon Roster comes from DEP's certification lists, with the certification number shown.",
     ("25 Pa. Code Ch. 240", "https://files.dep.state.pa.us/RadiationProtection/BureauOfRadiationProtection/BRPPortalFiles/Chapter_240_2015-04-23.pdf"), ("How we verify pros", "/how-we-verify/")),
    ("What radon level is safe?",
     "EPA recommends fixing your home if radon is 4 picocuries per liter (pCi/L) or higher, and considering a fix between 2 and 4 pCi/L. For comparison, EPA puts the average indoor level in the U.S. at about 1.3 pCi/L and the average outdoor level at about 0.4 pCi/L.",
     ("EPA", "https://www.epa.gov/radon/what-epas-action-level-radon-and-what-does-it-mean"), ("What is radon?", "/what-is-radon/")),
    ("How common is high radon in Pennsylvania?",
     "PA DEP says about 40% of Pennsylvania homes have radon above EPA's 4 pCi/L action level. In DEP's public test records, 37% of 2,644,033 basement tests came back at or above 4 pCi/L, from 12% in Philadelphia to 70% in Fulton County.",
     ("PA DEP, 2026", DEP26), ("Radon levels by county", "/pa/radon-levels-by-county/")),
    ("How long does a radon test take?",
     "A short-term test runs for at least 48 hours, and PA DEP says most kits take 2 to 4 days. A long-term test runs for more than 90 days and shows your year-round average. Start with a short-term test, and use a long-term test to confirm a result between 4 and 10 pCi/L.",
     ("PA DEP and EPA", "/radon-testing-pennsylvania/"), ("Radon testing in Pennsylvania", "/radon-testing-pennsylvania/")),
    ("Do you have to test for radon to sell a house in Pennsylvania?",
     "No. Pennsylvania sellers don't have to test, but they must disclose known material defects, and the state's disclosure form asks about radon by name and whether the home has been tested. Many buyers order a radon test during the inspection period, and real estate tests must follow DEP's anti-tampering rules.",
     ("68 Pa.C.S. § 7308", "https://www.legis.state.pa.us/WU01/LI/LI/CT/HTM/68/00.073..HTM"), ("Selling a home with radon", "/pa/real-estate-radon-disclosure/")),
    ("Is radon dangerous?",
     "Yes. Radon is the second leading cause of lung cancer in the U.S. after smoking, and the leading cause among people who have never smoked. EPA estimates it causes about 21,000 lung cancer deaths a year. It has no color, smell or taste, so a test is the only way to know your level.",
     ("EPA", "https://www.epa.gov/radon/health-risk-radon"), ("What is radon?", "/what-is-radon/")),
]
GUIDES = [
    ("/what-is-radon/", "What is radon?", "Where it comes from, the health risk and what level is safe"),
    ("/radon-testing-pennsylvania/", "Radon testing in Pennsylvania", "Kits vs. certified testers, short vs. long tests"),
    ("/testing-vs-mitigation/", "Testing vs. mitigation", "Which one you need, and in what order"),
    ("/radon-mitigation-cost/", "Radon mitigation cost", "What PA homeowners pay, and what drives the price"),
    ("/free-radon-test-kit-pennsylvania/", "Free radon test kits in PA", "Who qualifies and how to order"),
    ("/pa/real-estate-radon-disclosure/", "Buying or selling a home", "PA disclosure rules and real estate tests"),
    ("/pa/radon-map/", "Pennsylvania radon map", "All 67 counties, shaded by high tests"),
    ("/pa/radon-data-report-2026/", "2026 radon data report", "What 2.6 million PA tests show"),
]


def pros_label(n):
    return "No local pros" if n == 0 else f"{n} pro{'s' if n != 1 else ''}"


def strip_tags(x):
    return re.sub(r"<[^>]+>", "", x)


def faq_jsonld(items):
    return ('<script type="application/ld+json">' + json.dumps({
        "@context": "https://schema.org", "@type": "FAQPage",
        "mainEntity": [{"@type": "Question", "name": q, "acceptedAnswer": {"@type": "Answer", "text": strip_tags(a)}} for q, a in items]},
        ensure_ascii=False) + "</script>")


def build_home():
    allf = list(FIRMS.values())
    n_test = sum(1 for f in allf if "testing" in f["services"])
    n_fix = sum(1 for f in allf if "mitigation" in f["services"])
    n_lab = sum(1 for f in allf if "lab" in f["services"])
    top = sorted([f for f in allf if (f.get("rating") or 0) >= 4.8 and f["reviews"] >= 100 and f.get("state", "PA") == "PA"], key=lambda f: -f["reviews"])[:4]
    popular = ["pittsburgh-pa", "philadelphia-pa", "allentown-pa", "harrisburg-pa", "lancaster-pa", "york-pa", "state-college-pa", "erie-pa"]
    places = [{"l": f"{c['name']} County", "s": f"{len(dedupe(c.get('firms', [])))} certified pros", "u": f"/pa/county/{k}/", "k": "c"} for k, c in sorted(COUNTIES.items())]
    places += [{"l": c["name"], "s": f"{c['county']} County", "u": f"/pa/city/{k}/", "k": "t"} for k, c in sorted(CITIES.items())]

    cities_html = ""
    for k in popular:
        c = CITIES.get(k)
        if not c or c["pct"] is None:
            continue
        cities_html += (f'<a class="city {lvl(c["pct"])}" href="/pa/city/{k}/"><b>{e(c["name"])}</b>'
                        f'<span class="pct"><strong class="num">{c["pct"]:.0f}%</strong> of tests high</span>'
                        f'<i style="--v:{c["pct"]:.0f}%"></i></a>')

    about_items = [
        ("How do I know a pro is really certified?", f'Every listing shows the firm\'s PA DEP certification number. You can look it up in the <a href="{DEP_DIR}">PA DEP Radon Services Directory</a> or call the PA Radon Hotline at {HOTLINE}. <a href="/how-we-verify/">How we verify</a>'),
        ("What happens when I ask for quotes?", "We send your request to up to 3 certified pros near you who offer that service, and show you their names right away. They contact you directly. It's free, and you don't have to hire anyone."),
        ("How are pros ranked?", 'By Google rating and number of reviews. Pros can\'t pay to rank higher. <a href="/how-we-make-money/">How we make money</a>'),
        ("Where does your information come from?", f'Pros come from public PA DEP certification lists dated {LIST_DATE}. Radon levels come from PA DEP\'s test results since 1986. Ratings come from Google, as of {RATING_DATE}. <a href="/about-our-data/">About our data</a>'),
    ]
    home_faq = faq(about_items)
    def sa(q, a, src, more):
        rel = ' rel="noopener"' if src[1].startswith("http") else ""
        return (f'<div class="sa"><h3>{e(q)}</h3><p>{e(a)}</p><p class="srcs">Source: <a href="{e(src[1])}"{rel}>{e(src[0])}</a>'
                f' · <a class="link" href="{more[1]}">{e(more[0])}</a></p></div>')
    qa_html = "".join(sa(*x) for x in SHORT_ANSWERS)
    jsonld = faq_jsonld([(q, a) for q, a, _, _ in SHORT_ANSWERS] + about_items)
    county_links = "".join(
        f'<li><a href="/pa/county/{k}/">{e(c["name"])} County</a><small class="num">{pros_label(len(dedupe(c.get("firms", []))))} · {c["pct"]:.0f}% high</small></li>'
        for k, c in sorted(COUNTIES.items()))
    def city_li(k, c):
        pct = f" · {c['pct']:.0f}% high" if c["pct"] is not None else ""
        return f'<li><a href="/pa/city/{k}/">{e(c["name"])}</a><small>{e(c["county"])} County{pct}</small></li>'
    city_links = "".join(city_li(k, c) for k, c in sorted(CITIES.items(), key=lambda kv: kv[1]["name"]))
    guides_html = "".join(f'<a class="guide" href="{u}"><b>{e(t)}</b><span>{e(d)}</span></a>' for u, t, d in GUIDES)
    body = f'''<main id="main">
<section class="hero"><div class="wrap">
<div>
<h1>Find certified radon testing &amp; mitigation <em>near you</em></h1>
<p class="lede">Every radon tester and mitigator in Pennsylvania, all certified by PA DEP. Search all 67 counties free, and ask up to three for quotes.</p>
<form class="search" action="/pa/counties/" role="search" id="find">
<div class="seg what"><span class="lbl" id="s-need-l">Looking for</span>
<input type="hidden" id="s-need" name="need" value="">
<button type="button" class="pick-btn" id="s-need-btn" aria-haspopup="listbox" aria-expanded="false" aria-controls="s-need-ac" aria-labelledby="s-need-l s-need-btn"><span>Any service</span></button>
<div class="ac" id="s-need-ac" role="listbox" aria-labelledby="s-need-l" hidden>
<a href="#" role="option" data-v="" aria-selected="true"><i>{ic("search", 18)}</i><span>Any service<small>Every certified pro near you</small></span></a>
<a href="#" role="option" data-v="test"><i>{ic("test", 18)}</i><span>Radon testing<small>A certified tester measures your home</small></span></a>
<a href="#" role="option" data-v="mitigation"><i>{ic("fix", 18)}</i><span>Radon mitigation<small>Install a system to lower radon</small></span></a>
<a href="#" role="option" data-v="lab"><i>{ic("kit", 18)}</i><span>Mail-in lab kit<small>Test it yourself, analyzed by a DEP lab</small></span></a>
</div></div>
<div class="seg where"><label for="s-where">Where</label><input id="s-where" name="q" placeholder="City or county" autocomplete="off" role="combobox" aria-expanded="false" aria-controls="s-ac" aria-autocomplete="list">
<div class="ac" id="s-ac" role="listbox" hidden></div></div>
<button type="submit">{ic("search", 18)}<span>Search</span></button>
</form>
<p class="under">Have a ZIP code? <a class="link" href="/quotes/">Get matched with 3 pros instead</a></p>
</div>
<div class="hero-art" aria-hidden="true">
{pa_map("map")}
<p class="flag"><b>37%</b>of Pennsylvania basement tests come back at or above 4 pCi/L</p>
<p class="flag flag2"><b class="num">{len(allf)}</b>DEP-certified firms, all listed free</p>
<img src="/assets/img/inspector-detector.webp" alt="" width="688" height="960">
</div>
</div></section>

<section class="band"><div class="wrap">
<div class="sec-h"><div><h2>What do you need?</h2></div></div>
<div class="tiles">
<a class="tile" href="/quotes/?need=test" data-ga-loc="tile_test"><span class="ic">{ic("test", 22)}</span><div><h3>Test my home</h3><p>A certified tester measures your radon. Most short-term tests take 2 to 4 days.</p></div><span class="meta num">{n_test} certified testers</span></a>
<a class="tile" href="/quotes/?need=mitigation" data-ga-loc="tile_fix"><span class="ic">{ic("fix", 22)}</span><div><h3>Fix high radon</h3><p>A certified mitigator installs a system that vents radon outside. PA DEP says most cost $800–$1,200.</p></div><span class="meta num">{n_fix} certified mitigators</span></a>
<a class="tile" href="/free-radon-test-kit-pennsylvania/" data-ga-loc="tile_kit"><span class="ic">{ic("kit", 22)}</span><div><h3>Test it myself</h3><p>Use a mail-in kit from a DEP-certified lab. If you've never tested, it may be free.</p></div><span class="meta num">{n_lab} certified labs</span></a>
</div>
</div></section>

<section class="band paper2"><div class="wrap check">
<img src="/assets/img/inspector-clipboard.webp" alt="" width="676" height="960" loading="lazy">
<div class="meter" id="checker">
<h2>Already tested? See what your number means.</h2>
<p class="lede">It's on your lab report or monitor, in picocuries per liter (pCi/L).</p>
<div class="row"><label class="sr" for="m-val">Your result in pCi/L</label><input class="in num" id="m-val" type="number" inputmode="decimal" min="0" step="0.1" placeholder="0.0"><span>pCi/L</span></div>
<div class="scale" aria-hidden="true"><span class="ptr" style="left:0%"></span></div>
<div class="ticks" aria-hidden="true"><span style="left:0">0</span><span style="left:20%">2</span><span style="left:40%">4 · EPA action level</span><span style="left:100%">10+</span></div>
<div class="verdict" id="m-out" aria-live="polite"><b>Type your result above</b><p>We'll tell you what EPA recommends at that level.</p></div>
<p class="src">Based on EPA guidance. General information, not medical advice.</p>
</div>
</div></section>

<section class="band"><div class="wrap">
<div class="sec-h"><div><h2>Top-rated pros in Pennsylvania</h2><p>Ranked by Google reviews. Pros can't pay to appear here.</p></div><a class="more" href="/pa/counties/">See all</a></div>
<div class="rail">{"".join(firm_card(f, vertical=True) for f in top)}</div>
</div></section>

<section class="band"><div class="wrap">
<div class="sec-h"><div><h2>How common is high radon near you?</h2><p>Share of basement tests at or above 4 pCi/L, from PA DEP test records. Statewide it's 37%.</p></div><a class="more" href="/pa/radon-levels-by-county/">All 67 counties</a></div>
<div class="cities">{cities_html}</div>
<div class="browse" id="browse">
<div class="tabs" role="tablist"><button type="button" role="tab" aria-selected="true" data-t="b-counties">All 67 counties</button><button type="button" role="tab" aria-selected="false" data-t="b-cities">Cities</button></div>
<ul class="blist" id="b-counties">{county_links}</ul>
<ul class="blist" id="b-cities" hidden>{city_links}</ul>
</div>
</div></section>

<section class="band green"><div class="wrap">
<div class="trust">
<div>{ic("shield", 28)}<h3>Certified, with proof</h3><p>Every listing shows the pro's PA DEP certification number, so you can check it with the state.</p></div>
<div>{ic("nopay", 28)}<h3>No pay-to-rank</h3><p>Pros can't pay to rank higher or to be sent your request.</p></div>
<div>{ic("user", 28)}<h3>Free, no account</h3><p>Ask for quotes in one short form. Pros contact you, and you decide who to hire.</p></div>
</div>
</div></section>

<section class="band" id="answers"><div class="wrap">
<div class="sec-h"><div><h2>Radon in Pennsylvania: short answers</h2><p>Updated November 2026. Each answer links to its source.</p></div></div>
<div class="sas">{qa_html}</div>
</div></section>

<section class="band"><div class="wrap">
<div class="sec-h"><div><h2>Radon guides</h2><p>Plain-English guides for Pennsylvania homeowners, buyers and sellers.</p></div><a class="more" href="/guides/">All guides</a></div>
<div class="guides">{guides_html}</div>
</div></section>

<section class="band"><div class="wrap">
<div class="sec-h"><h2>About Radon Roster</h2></div>
{home_faq}
</div></section>
{jsonld}
<script type="application/json" id="rr-places">{json.dumps(places, separators=(",", ":"))}</script>
</main>'''
    page(P("index.html"), body)
    h = read(P("index.html"))
    T = "Certified Radon Testing &amp; Mitigation in Pennsylvania | Radon Roster"
    DSC = ("Find PA DEP-certified radon testers and mitigators in all 67 Pennsylvania counties. Compare Google ratings and DEP "
           "certification numbers, see local radon levels, and get up to 3 free quotes.")
    h = re.sub(r"<title>.*?</title>", f"<title>{T}</title>", h, count=1)
    h = re.sub(r'(<meta (?:name="description"|property="og:description"|name="twitter:description") content=")[^"]*"', lambda m: m.group(1) + DSC + '"', h)
    h = re.sub(r'(<meta (?:property="og:title"|name="twitter:title") content=")[^"]*"', lambda m: m.group(1) + T + '"', h)
    write(P("index.html"), h)


# ---------------------------------------------------------------- listing pages (county + city)
def listing(path, *, crumbs, h1, place, firm_ids, local_ids, stat, faq_items, related, quote_q, county_slug, pct=None):
    firms = sort_firms(dedupe(firm_ids))
    local = {f["id"] for f in dedupe(local_ids)}
    n = len(firms)
    n_fix = sum(1 for f in firms if "mitigation" in f["services"])
    n_test = sum(1 for f in firms if "testing" in f["services"])
    n_lab = sum(1 for f in firms if "lab" in f["services"])
    n_rev = sum(1 for f in firms if top_rated(f))
    fixers = [f for f in firms if "mitigation" in f["services"]]

    sub = f'{n} certified pro{"s" if n != 1 else ""}'
    sub += f' · {n_fix} install{"s" if n_fix == 1 else ""} mitigation systems' if n_fix else " · none install mitigation systems"

    # Few local mitigators? Show certified mitigators from neighbouring counties right after the list.
    nearby = []
    if county_slug and len(fixers) < 3:
        seen = {f["id"] for f in firms}
        for nb in COUNTIES.get(county_slug, {}).get("neighbors", []):
            for f in dedupe(COUNTIES.get(nb, {}).get("firms", [])):
                if "mitigation" in f["services"] and f["id"] not in seen:
                    nearby.append(f)
                    seen.add(f["id"])
        nearby = sort_firms(nearby)[:6]

    chip = lambda key, label, cnt: (f'<button class="chip" type="button" data-f="{key}" aria-pressed="{"true" if key == "all" else "false"}"'
                                    f'{" disabled" if cnt == 0 else ""}>{label} <small class="num">{cnt}</small></button>')
    toolbar = f'''<div class="toolbar"><div class="wrap" role="group" aria-label="Filter pros">
{chip("all", "All", n)}{chip("m", "Mitigation", n_fix)}{chip("t", "Testing", n_test)}{chip("l", "Lab kits", n_lab)}{chip("r", "Top rated", n_rev)}
<span class="sp"></span><div class="view" role="group" aria-label="View"><button type="button" data-v="cards" aria-pressed="true">Cards</button><button type="button" data-v="table" aria-pressed="false">Compare</button></div><label class="sr" for="sort">Sort</label>
<select id="sort"><option value="score"{" selected" if DEFAULT_SORT == "rating" else ""}>Top rated</option><option value="n">Most reviews</option><option value="town"{" selected" if DEFAULT_SORT == "town" else ""}>Town</option><option value="name">Name A–Z</option></select>
</div></div>'''

    cards = "".join(firm_card(f, here_county=county_slug) for f in firms)
    nearby_html = ""
    if nearby:
        nearby_html = (f'<div class="sub-h"><h2>Mitigators in nearby counties</h2><p>Only {len(fixers)} certified mitigator{"s are" if len(fixers) != 1 else " is"} based in {e(place)}. '
                       f'These are certified too, and many travel across county lines.</p></div><div class="cards">{"".join(firm_card(f, here_county=county_slug) for f in nearby)}</div>')

    radchip = (f'<a class="radchip {lvl(pct)}" href="#radon-data"><i aria-hidden="true"></i><b class="num">{pct:.0f}%</b> of basement tests here were high'
               f'<span>· state 37%</span></a>') if pct is not None else ""
    radband = (f'<section class="band" id="radon-data"><div class="wrap radband"><div><h2>Radon in {e(place)}</h2>'
               f'<p>Radon levels vary house to house, even on the same street. These numbers show how often tests in the area came back high. Only a test tells you your home\'s level.</p>'
               f'<p><a class="link" href="/quotes/?need=test">Get your home tested</a> or <a class="link" href="/free-radon-test-kit-pennsylvania/">see free test kits</a>.</p></div>{stat}</div></section>') if stat else ""
    body = f'''<main id="main">
<section class="lhead"><div class="wrap">
<div><nav class="crumbs" aria-label="Breadcrumb">{crumbs}</nav><h1>{e(h1)}</h1>
<p class="sub"><span>{sub}</span>{radchip}</p></div>
</div></section>
{toolbar}
<div class="wrap results">
<div>
<p class="count" id="count" aria-live="polite">{n} pros <span>· {"sorted by Google rating" if DEFAULT_SORT == "rating" else "sorted by town"}</span></p>
<div class="cards" id="list">{cards}</div>
<p class="empty" id="none" hidden>No pros match that filter. <button class="chip" type="button" data-f="all">Show all</button></p>
{nearby_html}
</div>
<div class="side">{ask_card(f"Get quotes in {place}", "Tell us what you need. We'll send it to up to 3 certified pros nearby, and show you who.", quote_q)}</div>
</div>
{radband}
<section class="band"><div class="wrap">{related}</div></section>
<section class="band"><div class="wrap"><div class="sec-h"><h2>Answers</h2></div>{faq(faq_items)}</div></section>
</main>'''
    page(path, body, "/pa/counties/", mobile_bar(f"Quotes in {place}", "Free · up to 3 certified pros", quote_q))


def stat_card(pct, label, rows, details, county=None):
    bars = "".join(f'<div class="sbar {lvl(v)}"><span>{e(k)}</span><i style="--v:{v:.0f}%"></i><b class="num">{v:.0f}%</b></div>' for k, v in rows)
    mp = ""
    if county:
        nb = COUNTIES.get(county, {}).get("neighbors", [])
        mp = (pa_map("mini", on=county, near=nb, label=f"Map of Pennsylvania with {COUNTIES[county]['name']} County highlighted")
              + '<p class="key"><span><i style="background:var(--acc)"></i>' + e(COUNTIES[county]["name"]) + ' County</span><span><i style="background:var(--r2)"></i>Darker = more high tests</span></p>')
    return f'''<div class="stat">{mp}<div class="big"><b class="num">{pct:.0f}%</b><span>{label}</span></div>
<div class="bars">{bars}</div>
<details><summary>About this data</summary><dl>{details}</dl><p>From PA DEP's radon test results, 1986 to today. These count tests, not homes, and only a test tells you your home's level.</p></details></div>'''


def related_links(title, items):
    if not items:
        return ""
    return f'<div class="sec-h"><h2>{e(title)}</h2></div><div class="places">' + "".join(f'<a class="chip" href="{u}">{e(t)}</a>' for u, t in items) + "</div>"


def build_counties():
    for slug, c in COUNTIES.items():
        path = P("pa", "county", slug, "index.html")
        if not os.path.exists(path):
            continue
        name = c["name"]
        crumbs = '<a href="/">Pennsylvania</a><span>›</span><a href="/pa/counties/">Counties</a><span>›</span><span aria-current="page">' + e(name) + "</span>"
        stat = ""
        if c.get("pct") is not None:
            stat = stat_card(c["pct"], f"of basement tests in {e(name)} County were high (4 pCi/L or more)",
                             [(f"{name}", c["pct"]), ("Pennsylvania", 37)],
                             f'<dt>Median</dt><dd>{c["median"]} pCi/L</dd><dt>Tests on record</dt><dd class="num">{c["tests"]:,}</dd>'
                             f'<dt>First floor</dt><dd>{c["pct_first"]:.0f}% high</dd><dt>Rank</dt><dd>#{c["rank"]} of 67 counties</dd>', county=slug)
        rel = []
        if c.get("cities"):
            rel.append(related_links(f"Cities in {name} County", [(f"/pa/city/{k}/", CITIES[k]["name"]) for k in c["cities"] if k in CITIES]))
        if c.get("neighbors"):
            rel.append(related_links("Nearby counties", [(f"/pa/county/{k}/", f"{COUNTIES[k]['name']} County") for k in c["neighbors"] if k in COUNTIES]))
        listing(path, crumbs=crumbs, h1=f"Radon testing & mitigation in {name} County", place=f"{name} County",
                firm_ids=c.get("firms", []), local_ids=c.get("firms", []), stat=stat,
                faq_items=[(q, e(a)) for q, a in c.get("faq", [])], related='<div style="display:grid;gap:40px">' + "".join(rel) + "</div>",
                quote_q=f"/quotes/?county={slug}", county_slug=slug, pct=c.get("pct"))


def build_cities():
    for slug, c in CITIES.items():
        path = P("pa", "city", slug, "index.html")
        if not os.path.exists(path):
            continue
        cty = COUNTIES.get(c["county_slug"], {})
        crumbs = (f'<a href="/">Pennsylvania</a><span>›</span><a href="/pa/county/{c["county_slug"]}/">{e(c["county"])} County</a>'
                  f'<span>›</span><span aria-current="page">{e(c["name"])}</span>')
        stat = ""
        if c["pct"] is not None:
            rows = [(c["name"], c["pct"])]
            if cty.get("pct") is not None:
                rows.append((f"{c['county']} Co.", cty["pct"]))
            rows.append(("Pennsylvania", 37))
            stat = stat_card(c["pct"], f"of basement tests in {e(c['name'])} were high (4 pCi/L or more)", rows,
                             f'<dt>Median</dt><dd>{c["median"]} pCi/L</dd><dt>Tests on record</dt><dd class="num">{c["tests"]:,}</dd>', county=c["county_slug"] if c["county_slug"] in COUNTIES else None)
        rel = [f'<div class="own"><p><b>Hiring in {e(c["name"])}?</b> Our guide covers what to ask, what it costs, and how to check a pro.</p><a class="btn ghost" href="{c["guide"]}">Read the {e(c["name"])} guide</a></div>'] if c.get("guide") else []
        others = [k for k, v in CITIES.items() if v["county_slug"] == c["county_slug"] and k != slug]
        rel.append(related_links("Nearby", [(f"/pa/county/{c['county_slug']}/", f"{c['county']} County")] + [(f"/pa/city/{k}/", CITIES[k]["name"]) for k in others]))
        listing(path, crumbs=crumbs, h1=f"Radon testing & mitigation in {c['name']}, PA", place=c["name"],
                firm_ids=c["firms"], local_ids=c["firms"], stat=stat, faq_items=[(q, e(a)) for q, a in c.get("faq", [])],
                related='<div style="display:grid;gap:40px">' + "".join(rel) + "</div>",
                quote_q=f"/quotes/?county={c['county_slug']}", county_slug=c["county_slug"], pct=c.get("pct"))


# ---------------------------------------------------------------- firm pages
def person_name(n):
    if "," in n:
        parts = [x.strip() for x in n.split(",") if x.strip()]
        suf = [x for x in parts[1:] if x.lower().rstrip(".") in ("jr", "sr", "ii", "iii", "iv")]
        rest = [x for x in parts[1:] if x not in suf]
        n = " ".join(rest + [parts[0]] + [s.upper() if s.lower().startswith("i") else s for s in suf])
    return n


def build_firms():
    for fid, f in FIRMS.items():
        path = P("pa", "firms", f["slug"], "index.html")
        if not os.path.exists(path):
            continue
        has = set(f["services"])
        place = f["city"] + (", " + f["state"] if f.get("state") else "")
        meta = [rating(f, long=True) if f.get("rating") else '<span class="mute">No Google reviews yet</span>', e(place)]
        if f.get("county"):
            meta.append(f'<a href="/pa/county/{f["county_slug"]}/">{e(f["county"])} County</a>')
        crumbs = '<a href="/">Pennsylvania</a><span>›</span>' + (f'<a href="/pa/county/{f["county_slug"]}/">{e(f["county"])} County</a><span>›</span>' if f.get("county") else "") + f'<span aria-current="page">{e(f["name"])}</span>'

        svc = "".join(f'<span>{ic("check", 18)}{lab}</span>' if key in has else f'<span class="no">{lab}</span>'
                      for key, lab in (("testing", "Radon testing"), ("mitigation", "Mitigation systems"), ("lab", "Lab analysis")) if key in has or key != "lab")
        lic = f'''<div class="license">{EL.format(cls=" lg")}<p class="k">PA DEP certified</p><h3>{e(f["legal_name"])}</h3>
<div class="svc">{svc}</div>
<div class="ids">{"".join(f'<span>{e(x)}</span>' for x in f["ids"])}</div>
<a class="ver" href="{DEP_DIR}" rel="noopener">Check these numbers with PA DEP</a><p class="mute">From DEP lists dated {LIST_DATE}. DEP doesn't publish expiry dates.</p></div>'''

        sections = []
        if f.get("rating"):
            revs = "".join(f'<div class="rev"><div class="who"><i>{e(initials(q["who"]))}</i><span>{e(q["who"])}<small>{e(q["ago"])} · Google</small></span></div><p>{e(q["text"])}</p></div>' for q in f["quotes"][:4])
            link = f'<p style="margin-top:20px"><a class="more" href="{e(f["maps"])}" rel="nofollow noopener">Read all {f["reviews"]:,} reviews on Google {ic("ext", 15)}</a></p>' if f.get("maps") else ""
            sections.append(f'''<section class="fsec" id="reviews"><div class="rsum"><b class="num">{f["rating"]:.1f}</b><div class="s"><span class="stars" aria-hidden="true">★★★★★</span><span>{f["reviews"]:,} Google review{"s" if f["reviews"] != 1 else ""}</span></div></div>
{('<div class="revs">' + revs + '</div>') if revs else ''}{link}
<p class="mute" style="margin-top:16px;font-size:.82rem">Ratings from Google as of {RATING_DATE}. They don't affect who gets quote requests.</p></section>''')
        if f["people"]:
            ppl = "".join(f'<div class="person"><i>{e(initials(person_name(n)))}</i><span>{e(person_name(n))}<small class="mono">{e(c)}</small></span></div>' for n, c in f["people"])
            sections.append(f'<section class="fsec"><h2>Certified people</h2><div class="people">{ppl}</div></section>')
        sections.append(f'<section class="fsec" id="certificate"><h2>Certification</h2>{lic}</section>')
        kv = f'<dt>Address</dt><dd>{e(f["address"])}</dd>' if f["address"] else ""
        if f.get("county"):
            kv += f'<dt>County</dt><dd><a class="link" href="/pa/county/{f["county_slug"]}/">{e(f["county"])} County</a></dd>'
        sections.append(f'<section class="fsec"><h2>Location</h2><dl class="kv">{kv}</dl></section>')
        sections.append(f'<section class="fsec"><div class="own"><p><b>Is this your business?</b> Add your website, service area and photos for free.</p><a class="btn quiet" href="/claim-listing/?firm={fid}">Claim this listing</a></div></section>')

        more = ""
        if f.get("county"):
            peers = [x for x in sort_firms(dedupe(COUNTIES.get(f["county_slug"], {}).get("firms", []))) if x["id"] != fid][:3]
            if peers:
                more = (f'<section class="band"><div class="wrap"><div class="sec-h"><h2>More pros in {e(f["county"])} County</h2>'
                        f'<a class="more" href="/pa/county/{f["county_slug"]}/">See all</a></div><div class="cards three">'
                        + "".join(firm_card(x, here_county=f["county_slug"]) for x in peers) + "</div></div></section>")

        q = f"/quotes/?firm={fid}"
        svc_bits = "".join(f'<span class="ok">{ic("check", 15)}{lab}</span>' if key in has else f'<span class="no">{lab}</span>'
                           for key, lab in (("testing", "Testing"), ("mitigation", "Mitigation"), ("lab", "Lab analysis")) if key in has or key != "lab")
        more_ids = f' <span class="mute">+{len(f["ids"]) - 1} more</span>' if len(f["ids"]) > 1 else ""
        certstrip = (f'<div class="certstrip">{EL.format(cls="")}<b>PA DEP certified</b>{svc_bits}'
                     f'<span class="mono">{e(f["ids"][0]) if f["ids"] else ""}</span>{more_ids}<a class="link" href="#certificate">Details</a></div>')
        body = f'''<main id="main"><div class="wrap">
<section class="fhead"><nav class="crumbs" aria-label="Breadcrumb">{crumbs}</nav><h1>{e(f["name"])}</h1>
<div class="meta">{'<span class="dot">·</span>'.join(meta)}</div>
{certstrip}</section>
<div class="fbody"><div>{"".join(sections)}</div>
<div class="side">{ask_card(f"Get a quote from {f['name']}", f"We'll send your request to {e(f['name'])} and up to 2 other certified pros nearby. They contact you directly.", q, "Request a quote")}</div></div>
</div>{more}</main>'''
        page(path, body, "", mobile_bar(f["name"], "Free quote · no obligation", q, "Request a quote"))


# ---------------------------------------------------------------- quotes
def build_quotes():
    path = P("quotes", "index.html")
    counties = json.dumps({k: c["name"] for k, c in sorted(COUNTIES.items())}, separators=(",", ":"))
    firms = json.dumps({k: f["name"] for k, f in FIRMS.items()}, separators=(",", ":"))
    opt = lambda val, icon, b, small, req="": (f'<label class="opt"><input type="radio" name="need" value="{val}"{req}><span class="ic">{ic(icon, 22)}</span>'
                                               f'<span><b>{b}</b><small>{small}</small></span></label>')
    body = f'''<main id="main"><div class="wrap qpage">
<div>
<form class="qflow" method="post" action="https://leads.radonroster.com/api/lead" data-lead novalidate>
<div class="qbar" aria-hidden="true"><span id="qbar"></span></div>
<p class="firmnote lf-firm" hidden></p>
<fieldset class="qstep on" data-step="1"><legend tabindex="-1">What do you need?</legend>
<p class="lead">We'll only send it to pros certified for that service.</p>
<div class="opts">
{opt("test", "test", "Test my home", "A certified tester measures your radon, usually over 2 to 4 days.", " required")}
{opt("mitigation", "fix", "Fix high radon", "A certified mitigator installs a system.")}
{opt("result", "result", "Help with a test result", "Tell us your number and we'll send it to the right pros.")}
{opt("kit", "kit", "A mail-in test kit", "From a DEP-certified lab.")}
</div>
<div class="lvlbox" id="lf-lvl" hidden><label class="f" for="g-level">Your result <span class="mute">(optional)</span></label>
<input class="in num" id="g-level" name="level" type="number" step="any" min="0" max="2000" inputmode="decimal" placeholder="pCi/L"><p class="hint" id="levelhint">At 4 pCi/L or more, we send it to mitigators. Under 4, to testers.</p></div>
</fieldset>

<fieldset class="qstep" data-step="2"><legend tabindex="-1">Where's the home?</legend>
<p class="lead">We'll start with certified pros closest to you.</p>
<div class="fld"><label class="f" for="g-zip">ZIP code</label><input class="in lf-zip num" id="g-zip" name="zip" inputmode="numeric" pattern="[0-9]{{5}}" maxlength="5" autocomplete="postal-code" required placeholder="e.g. 15213"><p class="hint" id="ziphint"></p></div>
<input type="hidden" name="county" id="g-county" value="">
</fieldset>

<fieldset class="qstep" data-step="3"><legend tabindex="-1">How should pros reach you?</legend>
<p class="lead">Email or phone is fine. We don't call or text you.</p>
<div class="fld"><label class="f" for="g-name">Your name</label><input class="in" id="g-name" name="name" autocomplete="name" required minlength="2" maxlength="100"></div>
<div class="pair"><div><label class="f" for="g-email">Email</label><input class="in" id="g-email" name="email" type="email" autocomplete="email" maxlength="200"></div>
<div><label class="f" for="g-phone">Phone</label><input class="in" id="g-phone" name="phone" type="tel" autocomplete="tel" maxlength="30"></div></div>
<div class="fld"><label class="f" for="g-msg">Anything pros should know? <span class="mute">(optional)</span></label><textarea class="in" id="g-msg" name="message" rows="2" maxlength="1000" placeholder="Timing, a closing date, your test result…"></textarea></div>
<div class="hp" aria-hidden="true"><label for="g-web">Leave this empty</label><input id="g-web" name="website" tabindex="-1" autocomplete="off"></div>
<input type="hidden" name="firm" value=""><input type="hidden" name="source" value=""><input type="hidden" name="idem" value="">
<label class="consent" for="g-ok"><input id="g-ok" name="consent" type="checkbox" required><span>Send my name, contact details and request to up to 3 PA DEP-certified radon firms near me so they can contact me by email or phone. I don't have to hire anyone. <a href="/privacy/">Privacy policy</a></span></label>
<label class="consent" for="g-mk"><input id="g-mk" name="marketing_opt_in" type="checkbox" value="true"><span>Also send me occasional radon tips from Radon Roster (optional).</span></label>
<div class="cf-turnstile" data-sitekey="0x4AAAAAAFVkzf_vPzU_ltim" data-size="flexible" style="margin-top:20px"></div>
<p class="lf-out" role="status" aria-live="polite"></p>
</fieldset>

<div class="qnav"><button type="button" class="back qback" hidden>Back</button><span></span>
<button type="button" class="btn lg qnext">Continue</button><button class="btn lg qsend" type="submit" hidden>Send request</button></div>
</form>
</div>
<aside><div class="summary" id="qpanel"><div class="guide"><img src="/assets/img/inspector-point.webp" alt="" width="713" height="960"><p>Three quick questions, then certified pros near you take it from there.</p></div><h2>Your request</h2><div id="qsum"><p class="empty-s">Nothing yet.</p></div>
<ol class="nsteps"><li><span><b>Up to 3 certified pros get it</b>Nearest first, starting with your county. Pros can't pay to be picked.</span></li>
<li><span><b>You see who right away</b>Their names show on the next screen and in your email.</span></li>
<li><span><b>They contact you</b>Compare quotes and DEP numbers. You don't have to hire anyone.</span></li></ol></div>
<p class="mute" style="font-size:.84rem;margin-top:16px">Prefer to choose yourself? <a class="link" href="/pa/counties/">Browse pros by county</a>.</p></aside>
</div></main>
<script>window.RR_COUNTIES={counties};</script><script>window.RR_FIRMS={firms};</script>'''
    page(path, body, "")


# ---------------------------------------------------------------- everything else: new shell, old content
def reshell():
    done = 0
    rebuilt = {P("index.html"), P("quotes", "index.html")}
    rebuilt |= {P("pa", "county", s, "index.html") for s in COUNTIES} | {P("pa", "city", s, "index.html") for s in CITIES}
    rebuilt |= {P("pa", "firms", f["slug"], "index.html") for f in FIRMS.values()}
    for path in glob.glob(P("**", "index.html"), recursive=True) + [P("404.html")]:
        if path in rebuilt or "/node_modules/" in path or "/tools/" in path or not os.path.exists(path):
            continue
        s = read(path)
        m = re.search(r"<main[^>]*>(.*?)</main>", s, re.S)
        if not m:
            continue
        inner = m.group(1)
        inner = re.sub(r'<aside class="qsbar".*?</aside>', "", inner, flags=re.S)
        body = f'<main id="main" class="legacy">{inner}</main>'
        tail = "".join(re.findall(r"<script>.*?</script>", s[s.find("</main>"):], re.S))
        h = head(path)
        if "rr-legacy.css" not in h:
            h = h.replace('<link rel="stylesheet" href="/assets/rr.css">', '<link rel="stylesheet" href="/assets/rr.css"><link rel="stylesheet" href="/assets/rr-legacy.css">')
        legacy_js = "".join(f'<script src="/assets/{j}.js" defer></script>' for j in ("quote-flow", "trust") if f"/assets/{j}.js" in s and f'src="/assets/{j}.js" defer' not in h)
        write(path, h.replace("</head>", legacy_js + "</head>") + "<body>" + header() + body + footer() + tail + "</body></html>")
        done += 1
    return done


if __name__ == "__main__":
    build_home(); build_quotes(); build_counties(); build_cities(); build_firms()
    n = reshell()
    print(f"built home, quotes, {len(COUNTIES)} counties, {len(CITIES)} cities, {len(FIRMS)} firms; new shell on {n} other pages")
