Fictional artifacts from a test environment. All values are synthetic. Flag clear-text identifiers, emails, reserved SSNs, and secrets. Masked values are not leaks.
LEAK-01 log:
2026-03-02T10:11:12Z level=info msg="fetched chart" mrn=SYN-000441 request_id=req-1
LEAK-02 API error:
{"error":"query failed","sql":"SELECT * FROM patients WHERE email='alex.testpatient@example.com'"}
LEAK-03 UI URL (address bar):
https://portal.test/records?ssn=000-12-3456
LEAK-04 response header log:
Authorization: Bearer eyJhbGciOiJIUzI1NiIsInR5cCI6IkpXVCJ9.aaa.bbb
CLEAN-01 log (masked MRN):
2026-03-02T10:11:12Z level=info request_id=req-9 path=/records/SYN-***441 status=200
CLEAN-02 API error:
{"error":"not found","request_id":"req-10"}
CLEAN-03 UI:
Patient banner shows "Alex T." and "MRN ending 0441" only.
