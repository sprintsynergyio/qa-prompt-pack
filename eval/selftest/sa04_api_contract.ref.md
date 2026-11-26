| ID | Op | Request | Expected status | Schema assertions |
|---|---|---|---|---|
| 1 | GET /v1/projects | page=1 per_page=20 bearer | 200 | items[], page, per_page, total; each Project id uuid, name string, created_at iso-8601 |
| 2 | GET /v1/projects | no auth | 401 | error.code unauthorized, message string |
| 3 | GET /v1/projects | per_page=101 | 400 | error.code invalid_page |
| 4 | GET /v1/projects/{id} | known id | 200 | Project schema |
| 5 | GET /v1/projects/{id} | unknown or cross-tenant id | 404 | error.code not_found |
| 6 | POST /v1/projects | {name: 1..80} | 201 | Project schema |
| 7 | POST /v1/projects | empty or too long name | 400 | error.code invalid_name |
| 8 | POST /v1/projects | no auth | 401 | error.code unauthorized |
