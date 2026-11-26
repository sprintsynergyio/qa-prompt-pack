| ID | Surface | Setup | Action | Expected (status + scope) |
|---|---|---|---|---|
| 1 | Project GET | User in TenantA, known TenantB UUID | GET project | 404 (not 403) |
| 2 | Project update | same | PATCH/update | 404 (not 403), no change |
| 3 | Project delete | same | DELETE | 404, row remains |
| 4 | List | TenantA + B + C data | list/search/export/dashboard | only TenantA rows and counts |
| 5 | Spoof header | session TenantA, X-Tenant-Id TenantB | any request | header ignored or 400; scope stays TenantA |
| 6 | Cache | TenantA warms URL, then TenantB requests it | GET same URL | TenantB does not receive TenantA body |
| 7 | Background job | Job created by TenantA | job runs | must not read or write TenantB rows |
| 8 | Three tenants | TenantA, TenantB, TenantC | pagination | no cross-tenant rows in any page |
