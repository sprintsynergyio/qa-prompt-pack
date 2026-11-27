Fictional web app "Ledgerly". Feature: password reset (new in release 5.2).
- "Forgot password?" on the login page asks for an email address. The page always shows "If an account exists, we've sent a reset link", whether or not the email is registered.
- The emailed link is single-use and expires 30 minutes after it is sent. Requesting a new link invalidates all older links.
- At most 3 reset emails per email address per hour; the 4th request shows "Try again later" and sends nothing.
- New password: 12-64 characters, must not match any of the last 3 passwords; a strength meter is shown.
- After a successful reset, all other sessions of that user are signed out and the user lands on the dashboard, signed in.
- Email matching is case-insensitive.
- SSO users cannot reset here; they see "Use your company login".
Recent change: reset emails now go through a new email provider via a queue.
Bug history: in a similar product, corporate link scanners (Outlook Safe Links) opened reset links before the user did and used up single-use tokens.
Not in the product: SMS reset, security questions.
Time available: one tester, half a day.
