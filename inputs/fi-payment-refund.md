Fictional card payments API. Amounts are integer minor units. Currency USD (exponent 2). Test PANs only: 4242424242424242 (approve), 4000000000000002 (decline). Never invent other card numbers.
States: created → authorized → captured | voided; captured → refunded_partial | refunded; failed is terminal from created/authorized.
- POST /payments {amount, currency, pan, idempotency_key} → 201 authorized (or 402 declined). Repeat same idempotency_key + body returns the original payment, no second auth.
- POST /payments/{id}/capture {amount?} default full; partial capture allowed once; amount > authorized → 422 over_capture; already captured → 409.
- POST /payments/{id}/void allowed only from authorized → voided. After capture, void is 409 use_refund.
- POST /payments/{id}/refunds {amount, idempotency_key} from captured. Full, partial, and several partials until captured amount. Sum > remaining → 422 over_refund. Same idempotency_key + body returns the original refund, no second credit.
- Timeout: if a refund request is retried after a timeout, the client must reuse the same idempotency_key and must not assume failure.
- Webhook payment.captured / refund.succeeded may arrive twice or out of order; applying a given event id twice must not credit twice.
- Void and refund are not interchangeable.
No fees, no FX, no disputes in this spec.
