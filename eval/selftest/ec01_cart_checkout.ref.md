| ID | Scenario | Steps | Expected (order state + payment state) |
|---|---|---|---|
| 1 | guest checkout | Guest buys SKU-A with 4242424242424242 in US-NY | order created, authorization success; tax 8.25% |
| 2 | empty cart | Checkout with no items | 422 empty_cart, no charge, no order |
| 3 | stale price | Cart SKU-A then catalog price changes | 409 price_changed, no charge |
| 4 | address tax | US-NY vs US-OR | tax 8.25% vs 0, totals differ |
| 5 | decline + retry | Pay 4000000000000002 then 4242424242424242 | first no order/no charge; retry authorizes and creates order |
| 6 | gateway timeout | Pay times out, webhook later | never charge without a matching order; never an order without a successful authorization |
| 7 | double-submit | Click pay twice | one order, one authorization |
