Fictional shop "Fixture Mart". Currency USD. Catalog: SKU-A 4000 cents, SKU-B 1550 cents, SKU-HOT 2500 cents (stock is a separate input). Regions: US-NY (tax 8.25%), US-OR (tax 0%). Guest checkout is allowed. Payment methods: test card 4242424242424242 approve, 4000000000000002 decline. No other methods, no gift cards, no BNPL.
Invariants: (1) a charge must not exist without a matching order; (2) an order must not exist without a successful authorization. Timeout, double-submit, and webhook replay must land on one of those two end states.
Price changes: if catalog price changes after the cart was created, checkout must reject with 409 price_changed (do not silently charge the stale amount).
Empty cart checkout → 422 empty_cart.
