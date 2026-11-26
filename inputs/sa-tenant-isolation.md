Shared-schema SaaS, fictional tenants TenantA, TenantB, TenantC. Auth: session cookie. Tenant scope is taken only from the session's tenant_id. A X-Tenant-Id header, path prefix, or body tenant_id must be ignored (or 400 if it disagrees with the session) — never used as the scope.
Resources: Project, Invoice, Export, Job. Each has a UUID. IDs are not guessable but tests reuse a known foreign UUID.
Rules:
- Cross-tenant GET/POST-update/DELETE of a foreign UUID → 404 (not 403).
- List, search, export, and dashboard counts for TenantA never include TenantB or TenantC rows or totals.
- After TenantA warms a cache, TenantB requesting the same URL must not receive TenantA's body.
- A background Job created by TenantA must not read or write TenantB rows.
- Use three tenants so pagination and cache keys cannot collide by accident.
- Support/super-admin access is out of scope — do not invent it.
