---
title: "Privacy Policy (Draft) | Radon Roster"
description: "Draft privacy policy for Radon Roster: what quote requests collect, who receives them, and how long anything is kept."
canonical: https://radonroster.com/privacy/
---

# Privacy policy

**DRAFT - NEEDS LEGAL REVIEW BEFORE LAUNCH.** This draft describes how the quote-request system is built. Placeholders are in [brackets]; an attorney should review it, the consent wording on the quote form, and the contractor emails before the form goes live.

Last updated: [date]. This policy covers Radon Roster (radonroster.com, "we"), operated by [legal entity], [physical mailing address].

## Quote requests

* **What you enter:** your name, email and/or phone, ZIP code or county, the service you need, and optionally your radon test result and a note.
* **Who gets it:** when you check the consent box and submit, we send your request by email to **up to 3 PA DEP-certified radon firms** that offer that service and are based in or near your county. Only those firms get your contact details. We email you a list of the firms we contacted.
* **What we keep:** we don't store your name, email, phone, note or test result. Our server keeps only routing records: a request ID, the date and time, county, first three digits of your ZIP, the service requested and which firms were contacted. These records are kept for up to [13 months] to run and improve the service.
* **Email delivery:** requests are sent through our email provider [SendGrid (Twilio)], which processes the message to deliver it and keeps delivery logs under its own retention policy. Firms that receive your request keep it under their own policies; contact them directly to ask them to delete it.
* **Spam protection:** forms use Cloudflare Turnstile and per-connection rate limits. To rate-limit, we keep a one-way hash of your IP address for about an hour.

## Clicks on firm contact links

When you click a firm's phone, website or email link, your browser sends us an anonymous count (firm ID and link type only) so we can show firms how many people contacted them each month. No cookies or personal data are involved.

## Listing claims and corrections

We use the contact and business details you send to verify and process listing changes.

## Usage data

Our host keeps standard server logs. [Name any analytics tool, if added.]

## What we don't do

* We don't sell your personal information.
* We don't share quote requests with anyone other than the matched firms and our service providers (Cloudflare for hosting and form processing, [SendGrid] for email).
* We don't text or call you, and firms don't get permission to text you through this form.

## Contractors

Business listings come from public PA DEP certification records (see [About our data](https://radonroster.com/about-our-data/)). Firms receive homeowner requests by email; every request email has a one-click link to stop receiving them, and firms can [claim, correct or remove](https://radonroster.com/claim-listing/) their listing.

## Your choices

Questions or deletion requests: email hello@radonroster.com or use the [contact page](https://radonroster.com/contact/). Because we don't keep your request details, we can't retrieve or delete what the firms received; contact the firms listed in your confirmation email.

## Changes to this policy

We will post any changes here and update the date above. Material changes to how quote requests are shared will be highlighted at the top of this page before they take effect.
