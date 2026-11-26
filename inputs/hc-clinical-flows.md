Fictional clinic portal. Roles: Patient, Clinician, Clerk. No real patients.
Appointment (30-min slots, clinic TZ America/New_York, hours 09:00-17:00 weekdays):
- Patient or Clerk books a free slot for the signed-in patient only; response 201 {appointment_id, status: scheduled, start, end}.
- Double-book of the same slot → 409 slot_taken; no second appointment created.
- Start in the past → 422 slot_in_past.
- Reschedule: Patient/Clerk may move a scheduled appointment to a free future slot → 200 status remains scheduled, new start/end.
- Cancel by Patient or Clerk → 200 status cancelled. Clinician can also cancel.
- No-show: Clinician marks scheduled + start in the past → 200 status no_show.
- Patient cannot book, reschedule, or cancel another patient's appointment → 404 (do not confirm the other appointment exists).
Prescription:
- Clinician creates a prescription for a patient they may treat → 201 {rx_id, status: active, drug_code, sig, start, refills_remaining}.
- Clerk and Patient cannot create prescriptions → 403.
- Refill: Patient requests when refills_remaining > 0 and last_fill + min_days_between_fills (document: 30 days) has elapsed → 200 refills_remaining decremented.
- Refill too soon → 422 refill_too_soon.
- Allergy block: if the patient's allergy list includes the drug_code, create is 422 allergy_conflict (Clinician may not override in this spec).
- Unlisted drug_code, missing sig, or unknown interaction tables are out of scope — do not invent them.
