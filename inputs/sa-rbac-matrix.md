Single-tenant RBAC for a fictional SaaS. Roles: owner, admin, editor, viewer, billing_manager.
Actions and allowed roles:
- settings.write: owner, admin
- members.invite: owner, admin
- members.remove: owner
- billing.view: owner, admin, billing_manager
- billing.change_plan: owner, billing_manager
- project.create: owner, admin, editor
- project.edit: owner, admin, editor
- project.delete: owner, admin
- project.view: owner, admin, editor, viewer, billing_manager
- audit.export: owner, admin
- tenant.delete: owner
Allowed: HTTP 200 or 204, mutation persists. Denied: HTTP 403, no mutation (including partial). Viewer never mutates. Do not add roles or actions.
