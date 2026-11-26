Fictional inventory service. SKU-HOT starts at stock=1, no reservation. Checkout is POST /checkout {sku, qty, buyer_id} which atomically decrements stock or returns 409 out_of_stock.
Rules:
- N concurrent checkouts for qty=1 against stock=1: exactly one 200, N-1 409 out_of_stock, final stock=0.
- qty > stock → 409, stock unchanged.
- Optional hold: POST /holds {sku, qty, buyer_id, ttl_seconds} reserves stock; expired holds release stock; checkout of a valid hold succeeds and consumes it; a second checkout without a hold sees the reserved qty as unavailable.
- If stock reaches 0 between add-to-cart and pay, pay returns 409 out_of_stock and does not authorize payment.
- Coupon ONCEHOT is one redemption per buyer_id; two concurrent redeems by the same buyer: exactly one succeeds.
Warehouse sync lag is out of scope — do not invent it.
