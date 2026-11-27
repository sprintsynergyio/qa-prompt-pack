Sprint 22 regression, build 4.2.0-rc2, staging, 20-24 Nov 2026. Release decision is Monday.
Results by module (planned | passed | failed | blocked | not run):
- Login: 20 | 20 | 0 | 0 | 0
- Cart: 30 | 27 | 2 | 1 | 0
- Checkout: 40 | 31 | 4 | 3 | 2
- Order history: 18 | 14 | 1 | 2 | 1
- Profile: 12 | 6 | 1 | 0 | 5
Defects:
- BUG-311 Critical, open: card payment is charged twice when the user retries after a timeout (Checkout).
- BUG-312 High, fixed and verified: cart quantity resets to 1 on refresh.
- BUG-315 High, open: order history shows the date one day early for users east of UTC.
- BUG-318 Medium, open: profile avatar upload fails for PNG files over 2 MB.
- BUG-320 Low, open: typo on the order confirmation page.
Blocked cases are waiting on the payment sandbox, which was down on 22 Nov.
Lead's draft note: "112 executed, 95% pass rate, ready to ship."
