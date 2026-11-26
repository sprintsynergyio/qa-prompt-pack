Base URL https://shop.test (fictional). Journey:
1. GET /catalog (200)
2. POST /cart {sku:"SKU-HOT", qty:1} (200)
3. POST /checkout {cart_id} → 200 paid or 409 out_of_stock (hot SKU may sell out under the spike). Any 5xx is a failure.
Think time 1-3s random between steps. Use stages and thresholds from the prompt. Do not call any other host.
