Fictional ledger. Every payment allow, refuse, hold_for_review, capture, void, refund (success or failure) writes an immutable audit event.
Required fields: event_id, event_type, actor_id, account_id, channel, amount_minor, currency, outcome, correlation_id, occurred_at (ISO-8601).
Forbidden in the event body and logs: full PAN, CVV, full account number, password, raw access token, SSN. PAN if present must be first6+last4 only for test cards, or omitted.
Events cannot be updated or deleted via API (PATCH/DELETE → 405). A correction is a new event that references event_id.
correlation_id is reused across payment, capture, refund, and webhook of the same attempt.
List filters are account-scoped.
