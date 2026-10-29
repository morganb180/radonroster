---
name: radon-roster-request-quote
description: Request quotes from PA DEP-certified radon testers, mitigators and labs for a homeowner via Radon Roster; the homeowner confirms by email before anything is sent.
---

# Request quotes through Radon Roster

Only do this when the homeowner asked you to get quotes and agreed to share their name, email (and phone, if given) with up to three certified firms.

## Steps

1. Optionally find a firm first with the search skill or `GET https://leads.radonroster.com/api/firms?site=radon&zip=<ZIP>`, and pass its `id` as `firm`.
2. Send `POST https://leads.radonroster.com/api/agent/quote?site=radon` with `Content-Type: application/json` and these fields:
   - Required: `name`, `email`, `zip` (zip (PA) or county), `need`, and `consent: true`.
   - Optional: `phone`, `firm`, `message`, and `agent` (your app's name, shown to the homeowner). Optional `level` = radon test result in pCi/L.
   - Values for `need`:
   - `test`: Radon testing
   - `mitigation`: Radon mitigation system
   - `result`: Help with a test result (routes to mitigators if >= 4 pCi/L or unknown)
   - `kit`: Mail-in lab test kit
3. You get `202` with `status: "pending_confirmation"`. Tell the homeowner to open the email from Radon Roster and click **Confirm** within 24 hours.
   - Nothing is sent to any firm until they confirm.
   - They can opt in to occasional tips on that page; you cannot do it for them.
4. After confirmation, the request goes to the chosen firm (if any) plus up to two other nearby certified firms, and the homeowner gets a copy listing who received it.

You can also use the MCP tool `request_quote` at `https://leads.radonroster.com/mcp?site=radon`; it follows the same flow.

## Errors

- `422 consent_required`: the homeowner didn't agree. Ask them; never set `consent` yourself.
- `400 <field>`: fix that field.
- `404 no_firms`: no certified firm serves that location or need.
- `429`: rate limited. Don't retry in a loop; wait an hour or send the homeowner to https://radonroster.com/get-quotes/.

## Spec

https://radonroster.com/openapi.json
