Patient portal — Book appointment (fictional). Controls in tab order:
1. Skip to main content (link)
2. Main heading "Book an appointment" (h1)
3. Clinic select, visible label "Clinic", required
4. Date input, visible label "Date", required, format YYYY-MM-DD
5. Slot list (radios) "Available times", each radio labelled with the clock time
6. Reason textarea, visible label "Reason (optional)", 0-200 characters
7. Submit button "Book appointment"
8. Error region (empty until submit): must be role=alert and announced when a required field is missing
9. Success status: "Appointment booked for {date} at {time}." must be a status message
Colour: body text #222 on #fff; error text is #c00 on #fff; submit is a 44×44 CSS px target.
No other controls. Keyboard: Tab moves in the order above; Escape does not close the page; no modal.
