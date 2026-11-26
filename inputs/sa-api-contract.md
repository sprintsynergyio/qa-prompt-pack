Public API https://api.saas.test/v1 (fictional). Auth: Bearer token. Content-Type application/json.
GET /v1/projects?page=1&per_page=20
  200 {items: Project[], page: number, per_page: number, total: number}
  401 {error: {code:"unauthorized", message:string}}
Project: {id: uuid, name: string, created_at: iso-8601}
per_page max 100; per_page=101 → 400 {error:{code:"invalid_page", message:string}}
GET /v1/projects/{id}
  200 Project
  401 as above
  404 {error:{code:"not_found", message:string}}  (also used for cross-tenant ids)
POST /v1/projects {name: 1..80 chars}
  201 Project
  400 {error:{code:"invalid_name", message:string}} when name missing/empty/too long
  401 as above
No other paths, fields, or status codes are documented. Pagination is 1-based. Idempotency is not documented for POST.
