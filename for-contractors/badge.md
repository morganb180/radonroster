---
title: "PA DEP-Certified Radon Badge for Your Website | Radon Roster"
description: "Free badges for PA DEP-certified radon testers, mitigators and labs. They show your certification type and link to your listing so homeowners can verify it."
canonical: https://radonroster.com/for-contractors/badge/
---

# Certification badge kit for radon firms

Show homeowners you're PA DEP-certified, and let them check it in one click. Each badge leads with your certification type and links to your free listing, which is built from DEP's public certification lists.

## Styles

- Seal (round): https://radonroster.com/badges/dep-certified-professional-seal.svg (140×140)
- Horizontal, light: https://radonroster.com/badges/dep-certified-professional-light.svg (269×72)
- Horizontal, dark: https://radonroster.com/badges/dep-certified-professional-dark.svg (269×72)
- Compact: https://radonroster.com/badges/dep-certified-professional-compact.svg (279×28)

Small line on every badge: "Verify on Radon Roster · DEP list Oct 2026" (the seal reads "VERIFY ON RADON ROSTER" and "AS OF OCT 2026"; the compact badge reads "Verify ›").

## Certification wording

| Badge wording | Requires DEP certification for |
| --- | --- |
| PA DEP-Certified Radon Professional | any DEP certification |
| PA DEP-Certified Radon Tester | testing |
| PA DEP-Certified Radon Mitigator | mitigation |
| PA DEP-Certified Radon Tester & Mitigator | mitigation + testing |
| PA DEP-Certified Radon Laboratory | lab |
| PA DEP-Certified Radon Lab & Tester | lab + testing |

Files: `https://radonroster.com/badges/dep-certified-<type>-<style>.svg`, type = professional, tester, mitigator, tester-mitigator, lab, lab-tester; style = seal, light, dark, compact.

## Badge code

```html
<a href="https://radonroster.com/pa/firms/YOUR-FIRM-PAGE/" title="Check our PA DEP certification listing on Radon Roster"><img src="https://radonroster.com/badges/dep-certified-professional-light.svg" alt="PA DEP-Certified Radon Professional. Verify this firm&#x27;s listing on Radon Roster." width="269" height="72" style="border:0"></a>
```

Example for M Webster Construction Inc (DEP: mitigation + testing):

```html
<a href="https://radonroster.com/pa/firms/m-webster-construction-inc-f2948/" title="Check M Webster Construction Inc's PA DEP certification listing on Radon Roster"><img src="https://radonroster.com/badges/dep-certified-tester-mitigator-light.svg" alt="PA DEP-Certified Radon Tester &amp; Mitigator. Verify this firm&#x27;s listing on Radon Roster." width="297" height="72" style="border:0"></a>
```

## How listing links work

- All firms (in-state and out-of-state): `https://radonroster.com/pa/firms/<name>-<firm-id>/` (example: https://radonroster.com/pa/firms/m-webster-construction-inc-f2948/). Full list: https://radonroster.com/pa/firms/
- Older badge links to a county page anchor (`/pa/county/<county>/#<firm-id>`) keep working.
- The firm ID ("F" plus a number) appears in your listing's "Claim, correct or remove this listing" link.

## Badge rules

- **What it says:** your firm appears on Pennsylvania DEP's radon certification list for the type shown, as of the DEP list date printed on the badge. Clicking it takes people to your Radon Roster listing, so they can check your DEP certification details themselves.
- **Who certifies:** radon certification is issued only by PA DEP. Radon Roster does not certify, license, inspect or endorse any firm. The badge is not issued, approved or endorsed by PA DEP, and Radon Roster is not affiliated with DEP.
- **Pick an accurate type.** Only use a type you hold: "Radon Professional" fits any DEP-certified firm. Tester, Mitigator and Laboratory must match your DEP certification. The code generator only offers types on DEP's list for your firm.
- **Only while certified.** Use the badge only while your firm is on DEP's current certification lists. If your certification lapses, we remove your listing and you must remove the badge.
- Free and optional. It does not change your listing order. Free listings are ordered by location and name, never by payment.
- Don't modify the artwork or wording, combine it with government seals or logos, or describe it as "DEP-approved" or "Radon Roster certified". You may scale it. Keep the seal at least 120 px wide.

Corrections: https://radonroster.com/claim-listing/ · Contact: hello@radonroster.com
