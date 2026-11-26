| ID | Flow | Rule | Type | Steps | Expected |
|---|---|---|---|---|---|
| A1 | appointment | book | P | Patient books a free weekday slot | 201 status scheduled |
| A2 | appointment | double-book | N | Second book of the same slot | 409 slot_taken, no second appointment |
| A3 | appointment | past | N | Start in the past | 422 slot_in_past |
| A4 | appointment | reschedule | P | Move scheduled appointment to a free future slot | 200 scheduled, new start/end |
| A5 | appointment | cancel | P | Patient cancels | 200 cancelled |
| A6 | appointment | no-show | P | Clinician marks scheduled past start | 200 no_show |
| A7 | appointment | cross-patient | N | Patient books for another patient | 404 |
| R1 | prescription | create | P | Clinician creates rx | 201 active with rx_id |
| R2 | prescription | forbidden | N | Clerk or Patient creates rx | 403 |
| R3 | prescription | refill | P | Patient refill after 30 days with remaining | 200 refills_remaining decremented |
| R4 | prescription | refill too soon | N | Refill before 30 days | 422 refill_too_soon |
| R5 | prescription | allergy | N | drug_code on allergy list | 422 allergy_conflict |
