# Radon Roster v2 redesign

Goal: a directory with Airbnb-level UX craft, and an official, authoritative voice. Each screen has one promise and one action; detail sits behind a click.

## How it builds
```
python3 tools/redesign/extract.py     # reads the ORIGINAL generator output into data.json (run on pristine pages only)
python3 tools/redesign/legacy_css.py  # old theme CSS, scoped to <main class="legacy">
python3 tools/redesign/build.py       # rewrites home, /quotes, 67 counties, 40 cities, 413 firms; reshells the other 65 pages
```
`extract.py` parses the old page markup (reviews, addresses, people, stats), so it must run before `build.py` has touched those pages. To re-extract, check out the pre-redesign pages first (`git checkout main -- index.html quotes pa`). `data.json` is committed, so `build.py` alone reproduces this PR.

Each page keeps its own `<head>`, so canonicals, OG tags and JSON-LD are unchanged. URLs are unchanged. The quote form keeps every field name, the endpoint, Turnstile and consent, so `lead.js` still does the submit and `analytics.js` still fires.

**The real generator lives with grokbot.** If the generator regenerates the site, these changes are overwritten. Port the templates in `build.py`, plus `assets/rr.css`, `assets/rr.js` and `assets/img/`, into it.

## Brand rules
- **One CTA color.** `--cta` (#108548) is used only on primary buttons and the search button. Nothing else on the site may be green. Everything else uses ink, paper and the radon ramp.
- **Type:** Public Sans throughout (the USWDS government typeface), with headlines at 800 weight, and Plex Mono for DEP certificate numbers.
- **Ground:** paper (#f7f4ee). White is used only for things you can open or fill in: cards, inputs, the quote card.
- **Radon ramp:** the radon map's warm ramp (#f6e3c6 → #7a2c0c), used for anything measured.
- **Logo:** the "86 · Rn · Radon" element tile, the same badge as on the inspector's helmet.
- **Mascot:** the YouTube inspector (`assets/img/inspector-*.webp`) appears in the hero, the result checker and the quote flow.
- **County maps:** every county and city page shows a PA map with its county highlighted (`pa_map.json`, from /pa/radon-map/).

## What changed
- **Header:** the utility bar is gone. The header is the logo, four links and "For radon pros", with a menu on phones.
- **Home:**
  - The hero has one search, "Looking for" plus "Where". Both fields use the same popover; "Where" autocompletes all 67 counties and 40 cities.
  - Below the hero: service tiles, a result checker, top-rated pros, and city radon levels with a browse list of every county and city.
  - Then a trust band, then "Radon in Pennsylvania: short answers": 8 sourced Q&As as visible text with matching FAQPage JSON-LD, written for AEO.
  - Then guides, then "About Radon Roster".
  - The title, H1 and meta description now target "certified radon testing & mitigation in Pennsylvania".
- **County and city pages:**
  - A compact header with one line of facts and a radon stat chip; pros start above the fold.
  - Filter chips (Mitigation, Testing, Lab kits, Top rated), a Cards/Compare toggle and a sort menu.
  - The map and radon data sit below the list.
  - When fewer than 3 mitigators are local, certified mitigators from neighbouring counties are listed.
- **Pro cards:**
  - **Rating tile:** a "Top rated" callout appears only at 4.5+ stars with 20+ reviews.
  - **Facts:**
    - What they do: "Tests, installs and retests" or "Testing only, no system to sell you".
    - Team size, and the latest review date.
    - Kind of business, but only when the firm's name says so.
  - **Review quote:** shown only when it mentions radon.
  - **Footer:** faces of the certified techs and the DEP number.
- **Firm pages:**
  - A slim certification strip sits under the name, and reviews appear above the fold.
  - The full certificate, certified people, location and a claim prompt sit below.
  - A sticky quote card on desktop becomes a bottom bar on phones.
- **Quotes:** one question per screen, with large options that auto-advance, a progress bar, and a side panel with a live summary.
- **Data cleanup:**
  - Display names are cleaned: "Steven Buffone", "Daniel Casciato Jr.", "JK Mechanical".
  - LLC and Inc. are dropped from card titles; the legal name stays on the firm page.
  - Names DEP truncated are completed, and duplicate DEP rows are merged into one card.
- **Fine print:** disclaimers live once, in the footer.
- **Copy fix:** test length now reads "2 to 4 days", per PA DEP as cited in the testing guide. The old site said "2–7 days".

## Open decisions
1. **Default sort is "Top rated"** (Google rating weighted by review count). The /how-we-make-money/ page still says free listings are "ordered by location and name". Either update that page, or set `DEFAULT_SORT = "town"` in build.py.
2. **Consent wording** on /quotes was shortened with the same meaning. It's legal copy, so review it.
3. **Legacy pages** (guides, 40 city hiring guides, radon map, policy pages) have the new shell and type but their old content layouts.
4. **13 counties have no local pros.** Their pages list nearby mitigators only; nearby testers and mail-in kits should be added.

## Next data (for richer cards)
- **Google Places:** business category, lat/long (for distance), and how many reviews mention radon.
- **Claim flow:** test price, mitigation price range, warranty, whether a follow-up test is included, service area, next opening, and a photo of an installed system.
