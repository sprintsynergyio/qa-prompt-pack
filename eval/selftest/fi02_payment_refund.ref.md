| ID | Transition | Setup | Action | Expected state+amounts |
|---|---|---|---|---|
| 1 | authorize | new payment 1000, PAN 4242424242424242, idempotency key K1 | POST /payments | 201 authorized 1000 minor units |
| 2 | decline | PAN 4000000000000002 | POST /payments | 402 declined, no capture |
| 3 | idempotency | repeat body + K1 | POST /payments | original payment, no second auth |
| 4 | capture full | authorized 1000 | POST capture | captured 1000 |
| 5 | partial capture | authorized 1000 | capture 400 | captured 400 once |
| 6 | over_capture | authorized 1000 | capture 1001 | 422 over_capture |
| 7 | void | authorized | POST void | voided |
| 8 | use_refund | already captured | POST void | 409 use_refund |
| 9 | full refund | captured 1000 | refund 1000 key R1 | refunded 1000 |
| 10 | partial refund | captured 1000 | refund 400 | refunded_partial remaining 600 |
| 11 | multiple partial | remaining 600 | refund 600 | refunded |
| 12 | over_refund | remaining 0 | refund 1 | 422 over_refund |
| 13 | timeout | refund R2 timed out | retry same idempotency_key | original refund, no second credit |
| 14 | webhook replay | event id E1 already applied | deliver E1 again | no second credit |
