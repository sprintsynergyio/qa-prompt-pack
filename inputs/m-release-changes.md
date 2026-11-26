Fictional shop "Northwind Market", release 3.4 to production on Thursday. One tester, 3 hours for regression.
Critical paths: sign in; search → add to cart → checkout with a card; order history.
Changes in this release:
- CHG-101: The coupon field moved from the cart page to the payment step of checkout.
- CHG-102: Fix: sales tax was rounded per line item; it is now calculated on the order total and rounded half-up to 2 decimals.
- CHG-103: Guest checkout now requires a phone number in E.164 format (e.g. +14155550123).
- CHG-104: Date library upgraded (used for order-history dates and the delivery estimate).
- CHG-105: Search results show 24 items per page instead of 20.
- CHG-106: Updated README and internal API docs (no runtime change).
Known flaky area: the delivery estimate around midnight UTC.
