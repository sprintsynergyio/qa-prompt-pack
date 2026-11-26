| ID | Control | WCAG | Type | Steps | Expected |
|---|---|---|---|---|---|
| 1 | skip link | 2.4.1 | P | Tab to first control, activate | focus moves to main heading |
| 2 | h1 | 1.3.1 / 2.4.6 | P | Inspect heading | one h1 "Book an appointment" |
| 3 | Clinic select | 1.3.1 / 4.1.2 | P | Check accessible name | visible label "Clinic", required |
| 4 | Date | 1.3.1 | P | Check label | visible label "Date" |
| 5 | radios | 4.1.2 | P | Each slot radio | name is the clock time |
| 6 | keyboard | 2.1.1 / 2.1.2 | P | Tab through | order 1-9, no trap, no modal |
| 7 | focus | 2.4.7 | P | Tab | focus visible on each control |
| 8 | error region | 3.3.1 / 4.1.3 | N | Submit with empty clinic | role=alert announces the error |
| 9 | status | 4.1.3 | P | Successful book | status message "Appointment booked for {date} at {time}." |
| 10 | contrast | 1.4.3 | P | Check #222 on #fff and error #c00 on #fff | contrast meets AA |
| 11 | target size | 2.5.8 | P | Measure submit | 44×44 CSS px |
| 12 | required | 3.3.2 | N | Submit empty required fields | errors announced, no book |
