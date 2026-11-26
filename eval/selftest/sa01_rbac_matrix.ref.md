```json
[
  {
    "id": "C01",
    "role": "owner",
    "action": "settings.write",
    "expected_http": 200,
    "expect_change": true
  },
  {
    "id": "C02",
    "role": "owner",
    "action": "members.invite",
    "expected_http": 200,
    "expect_change": true
  },
  {
    "id": "C03",
    "role": "owner",
    "action": "members.remove",
    "expected_http": 200,
    "expect_change": true
  },
  {
    "id": "C04",
    "role": "owner",
    "action": "billing.view",
    "expected_http": 200,
    "expect_change": true
  },
  {
    "id": "C05",
    "role": "owner",
    "action": "billing.change_plan",
    "expected_http": 200,
    "expect_change": true
  },
  {
    "id": "C06",
    "role": "owner",
    "action": "project.create",
    "expected_http": 200,
    "expect_change": true
  },
  {
    "id": "C07",
    "role": "owner",
    "action": "project.edit",
    "expected_http": 200,
    "expect_change": true
  },
  {
    "id": "C08",
    "role": "owner",
    "action": "project.delete",
    "expected_http": 200,
    "expect_change": true
  },
  {
    "id": "C09",
    "role": "owner",
    "action": "project.view",
    "expected_http": 200,
    "expect_change": true
  },
  {
    "id": "C10",
    "role": "owner",
    "action": "audit.export",
    "expected_http": 200,
    "expect_change": true
  },
  {
    "id": "C11",
    "role": "owner",
    "action": "tenant.delete",
    "expected_http": 200,
    "expect_change": true
  },
  {
    "id": "C12",
    "role": "admin",
    "action": "settings.write",
    "expected_http": 200,
    "expect_change": true
  },
  {
    "id": "C13",
    "role": "admin",
    "action": "members.invite",
    "expected_http": 200,
    "expect_change": true
  },
  {
    "id": "C14",
    "role": "admin",
    "action": "members.remove",
    "expected_http": 403,
    "expect_change": false
  },
  {
    "id": "C15",
    "role": "admin",
    "action": "billing.view",
    "expected_http": 200,
    "expect_change": true
  },
  {
    "id": "C16",
    "role": "admin",
    "action": "billing.change_plan",
    "expected_http": 403,
    "expect_change": false
  },
  {
    "id": "C17",
    "role": "admin",
    "action": "project.create",
    "expected_http": 200,
    "expect_change": true
  },
  {
    "id": "C18",
    "role": "admin",
    "action": "project.edit",
    "expected_http": 200,
    "expect_change": true
  },
  {
    "id": "C19",
    "role": "admin",
    "action": "project.delete",
    "expected_http": 200,
    "expect_change": true
  },
  {
    "id": "C20",
    "role": "admin",
    "action": "project.view",
    "expected_http": 200,
    "expect_change": true
  },
  {
    "id": "C21",
    "role": "admin",
    "action": "audit.export",
    "expected_http": 200,
    "expect_change": true
  },
  {
    "id": "C22",
    "role": "admin",
    "action": "tenant.delete",
    "expected_http": 403,
    "expect_change": false
  },
  {
    "id": "C23",
    "role": "editor",
    "action": "settings.write",
    "expected_http": 403,
    "expect_change": false
  },
  {
    "id": "C24",
    "role": "editor",
    "action": "members.invite",
    "expected_http": 403,
    "expect_change": false
  },
  {
    "id": "C25",
    "role": "editor",
    "action": "members.remove",
    "expected_http": 403,
    "expect_change": false
  },
  {
    "id": "C26",
    "role": "editor",
    "action": "billing.view",
    "expected_http": 403,
    "expect_change": false
  },
  {
    "id": "C27",
    "role": "editor",
    "action": "billing.change_plan",
    "expected_http": 403,
    "expect_change": false
  },
  {
    "id": "C28",
    "role": "editor",
    "action": "project.create",
    "expected_http": 200,
    "expect_change": true
  },
  {
    "id": "C29",
    "role": "editor",
    "action": "project.edit",
    "expected_http": 200,
    "expect_change": true
  },
  {
    "id": "C30",
    "role": "editor",
    "action": "project.delete",
    "expected_http": 403,
    "expect_change": false
  },
  {
    "id": "C31",
    "role": "editor",
    "action": "project.view",
    "expected_http": 200,
    "expect_change": true
  },
  {
    "id": "C32",
    "role": "editor",
    "action": "audit.export",
    "expected_http": 403,
    "expect_change": false
  },
  {
    "id": "C33",
    "role": "editor",
    "action": "tenant.delete",
    "expected_http": 403,
    "expect_change": false
  },
  {
    "id": "C34",
    "role": "viewer",
    "action": "settings.write",
    "expected_http": 403,
    "expect_change": false
  },
  {
    "id": "C35",
    "role": "viewer",
    "action": "members.invite",
    "expected_http": 403,
    "expect_change": false
  },
  {
    "id": "C36",
    "role": "viewer",
    "action": "members.remove",
    "expected_http": 403,
    "expect_change": false
  },
  {
    "id": "C37",
    "role": "viewer",
    "action": "billing.view",
    "expected_http": 403,
    "expect_change": false
  },
  {
    "id": "C38",
    "role": "viewer",
    "action": "billing.change_plan",
    "expected_http": 403,
    "expect_change": false
  },
  {
    "id": "C39",
    "role": "viewer",
    "action": "project.create",
    "expected_http": 403,
    "expect_change": false
  },
  {
    "id": "C40",
    "role": "viewer",
    "action": "project.edit",
    "expected_http": 403,
    "expect_change": false
  },
  {
    "id": "C41",
    "role": "viewer",
    "action": "project.delete",
    "expected_http": 403,
    "expect_change": false
  },
  {
    "id": "C42",
    "role": "viewer",
    "action": "project.view",
    "expected_http": 200,
    "expect_change": true
  },
  {
    "id": "C43",
    "role": "viewer",
    "action": "audit.export",
    "expected_http": 403,
    "expect_change": false
  },
  {
    "id": "C44",
    "role": "viewer",
    "action": "tenant.delete",
    "expected_http": 403,
    "expect_change": false
  },
  {
    "id": "C45",
    "role": "billing_manager",
    "action": "settings.write",
    "expected_http": 403,
    "expect_change": false
  },
  {
    "id": "C46",
    "role": "billing_manager",
    "action": "members.invite",
    "expected_http": 403,
    "expect_change": false
  },
  {
    "id": "C47",
    "role": "billing_manager",
    "action": "members.remove",
    "expected_http": 403,
    "expect_change": false
  },
  {
    "id": "C48",
    "role": "billing_manager",
    "action": "billing.view",
    "expected_http": 200,
    "expect_change": true
  },
  {
    "id": "C49",
    "role": "billing_manager",
    "action": "billing.change_plan",
    "expected_http": 200,
    "expect_change": true
  },
  {
    "id": "C50",
    "role": "billing_manager",
    "action": "project.create",
    "expected_http": 403,
    "expect_change": false
  },
  {
    "id": "C51",
    "role": "billing_manager",
    "action": "project.edit",
    "expected_http": 403,
    "expect_change": false
  },
  {
    "id": "C52",
    "role": "billing_manager",
    "action": "project.delete",
    "expected_http": 403,
    "expect_change": false
  },
  {
    "id": "C53",
    "role": "billing_manager",
    "action": "project.view",
    "expected_http": 200,
    "expect_change": true
  },
  {
    "id": "C54",
    "role": "billing_manager",
    "action": "audit.export",
    "expected_http": 403,
    "expect_change": false
  },
  {
    "id": "C55",
    "role": "billing_manager",
    "action": "tenant.delete",
    "expected_http": 403,
    "expect_change": false
  }
]
```
