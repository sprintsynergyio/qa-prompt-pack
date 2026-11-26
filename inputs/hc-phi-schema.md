Synthetic patient fixture schema for a fictional clinic app (no production data).
Required payload fields:
- display_name: string, "Given Family", letters/spaces/hyphen only, not a celebrity or living-person name; use clearly fake names such as Alex Testpatient, Jordan Fixture
- mrn: string matching ^SYN-[0-9]{6}$
- ssn: string XXX-XX-XXXX; area must be 000, 666, or 900-999; never 078-05-1120
- phone: string 555-01NN (NN 00-99)
- email: string local@example.com
- address: {street, city, region, postal}; city must be the fictional "Testville"; postal 00000-09999
- dob: YYYY-MM-DD in 1990-01-01..2020-12-31
- account_no: string matching ^SYN-ACC-[0-9]{4}$
- age_band: either an integer 0-88, or the exact string "90 or older" (Age89Plus cases only)
provenance: {synthetic: true, seed: string, generator: "qa-prompt-pack/hc01"}
Invalid cases must break exactly one rule (e.g. valid-area SSN, MRN without SYN- prefix, email not @example.com, DOB out of range).
