| ID | Scenario | Concurrency | Assertions (exact counts/statuses) |
|---|---|---|---|
| 1 | last unit race | N buyers, stock=1, qty=1 | exactly one 200, N-1 409 out_of_stock, final stock=0, stock decreases by 1 |
| 2 | qty > stock | 1 buyer, qty=2, stock=1 | 409, stock unchanged |
| 3 | hold + expiry | hold qty=1 ttl expires | stock released; later checkout can succeed |
| 4 | hold consumes | valid hold then checkout | checkout 200, hold consumed |
| 5 | sold-out between cart and pay | stock 0 after add-to-cart | pay 409 out_of_stock, no authorization |
| 6 | coupon race | two concurrent ONCEHOT redeems, same buyer | exactly one succeeds |
