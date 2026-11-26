```js
import http from 'k6/http';
import { check, sleep } from 'k6';
import { randomIntBetween } from 'https://jslib.k6.io/k6-utils/1.4.0/index.js';

export const options = {
  stages: [
    { duration: '2m', target: 100 },
    { duration: '5m', target: 100 },
    { duration: '1m', target: 300 },
    { duration: '3m', target: 50 },
  ],
  thresholds: {
    http_req_duration: ['p(95)<800', 'p(99)<1500'],
    http_req_failed: ['rate<0.02'],
  },
};

export default function () {
  const base = 'https://shop.test';
  const cat = http.get(`${base}/catalog`);
  check(cat, { 'catalog 200': (r) => r.status === 200 });
  sleep(randomIntBetween(1, 3));
  const cart = http.post(`${base}/cart`, JSON.stringify({ sku: 'SKU-HOT', qty: 1 }), { headers: { 'Content-Type': 'application/json' } });
  check(cart, { 'cart 200': (r) => r.status === 200 });
  sleep(randomIntBetween(1, 3));
  const pay = http.post(`${base}/checkout`, JSON.stringify({ cart_id: cart.json('id') }), { headers: { 'Content-Type': 'application/json' } });
  check(pay, { 'paid or sold out': (r) => r.status === 200 || r.status === 409 });
  sleep(randomIntBetween(1, 3));
}
```
