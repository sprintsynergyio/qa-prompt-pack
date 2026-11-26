```ts
import { test, expect } from '@playwright/test';
const API = 'https://jsonplaceholder.typicode.com';
test('POST /todos echoes body with id 201', async ({ request }) => {
  const body = { userId: 1, title: 'buy milk', completed: false };
  const r = await request.post(`${API}/todos`, { data: body });
  expect(r.status()).toBe(201);
  expect(await r.json()).toEqual({ ...body, id: 201 });
});
test('GET /todos/1 returns documented fields', async ({ request }) => {
  const r = await request.get(`${API}/todos/1`);
  expect(r.status()).toBe(200);
  const j = await r.json();
  expect(Object.keys(j).sort()).toEqual(['completed', 'id', 'title', 'userId']);
});
test('GET unknown id is 404 {}', async ({ request }) => {
  const r = await request.get(`${API}/todos/99999`);
  expect(r.status()).toBe(404);
  expect(await r.json()).toEqual({});
});
test.fixme('POST with missing fields is rejected', async () => { /* spec defines no validation */ });
```
