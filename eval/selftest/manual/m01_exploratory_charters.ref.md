C1 (60 min) Explore the reset link lifecycle with two browsers and a timer to discover token bugs.
Probes: use the link twice (single-use); open after 30 min (expiry); request a new link and try the older link (invalidate); Outlook Safe Links scanner opening it first.
Oracle: you'll know it's wrong if any used, old or expired link still sets a password.
C2 (45 min) Explore the request page with registered, unregistered and mixed-case emails to discover enumeration and matching bugs. Probes: unknown email message identical; UPPERCASE email; 4th request in an hour shows Try again later; SSO user sees company login; queue delay from the new email provider.
C3 (45 min) Explore the new-password form with 11/12/64/65 chars and last 3 passwords to discover rule gaps; check other sessions are signed out.
Questions: none.
Template: tried / saw / bugs / questions
