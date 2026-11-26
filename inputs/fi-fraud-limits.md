Published rules for a fictional wallet (amounts in USD minor units). Do not invent unpublished scores or bypasses.
- Per-transaction limit: 200000 (inclusive). 200000 succeeds; 200001 is refused.
- Daily cumulative limit: 500000 per account, inclusive, across web and mobile. 250000 web then 250000 mobile succeeds; a further 1 is refused.
- Velocity: 4 completed transfers in 10 minutes is allowed; the 5th in that window is hold_for_review (funds not released).
- New beneficiary cooling: first transfer to a new payee is hold_for_review; after 24h cooling, subsequent transfers follow the other rules.
- Decline card 4000000000000002 is refused (processor decline), not hold_for_review.
Outcomes: allow, refuse, hold_for_review. Each outcome writes an audit event (see audit spec) without rule-weight internals.
