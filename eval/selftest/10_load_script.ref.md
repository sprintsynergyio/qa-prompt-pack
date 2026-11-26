```js
import http from 'k6/http'; import { check, sleep } from 'k6';
export const options = { vus: 50, duration: '5m', thresholds: { http_req_duration: ['p(95)<800'], http_req_failed: ['rate<0.01'] } };
const API = 'https://jsonplaceholder.typicode.com';
export default function () {
  check(http.get(`${API}/todos/1`), { 'get 200': r => r.status === 200 }); sleep(Math.random() * 2 + 1);
  check(http.post(`${API}/todos`, JSON.stringify({ userId: 1, title: 'buy milk', completed: false }), { headers: { 'Content-Type': 'application/json' } }), { 'post 201': r => r.status === 201 });
  sleep(Math.random() * 2 + 1);
}
```
