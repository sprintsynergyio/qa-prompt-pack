| ID | Action | Outcome | Fields asserted | Forbidden fields | Expected |
|---|---|---|---|---|---|
| 1 | payment allow | allow | event_id, event_type, actor_id, account_id, channel, amount_minor, currency, outcome, correlation_id, occurred_at | PAN, CVV, token | event written |
| 2 | payment refuse | refuse | same required fields, correlation_id | full account number | event written |
| 3 | hold_for_review | hold_for_review | required fields | raw access token | event written, funds not released |
| 4 | refund failure | fail | required fields + correlation_id reused | PAN | event written |
| 5 | immutability | n/a | PATCH/DELETE event | — | 405, correction is a new event |
