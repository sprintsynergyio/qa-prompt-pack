Currency USD, exponent 2, half_up. Tax is applied after discounts, on the discounted merchandise total, using the shipping address region.
Cart for the numbered cases unless a case says otherwise: 2× SKU-A @ 40.00 and 1× SKU-B @ 15.50 (merchandise 95.50). Address US-NY tax 8.25% unless noted.
Coupons (all caps, one code per request):
- SAVE10: 10% off eligible merchandise, not stackable, min spend 50.00, excludes SKU-B, expires 2026-12-31T23:59:59Z
- FIVEOFF: 5.00 fixed off merchandise, not stackable, min spend 20.00, no exclusions, expires 2026-12-31T23:59:59Z
- EXPIRED: 10% off, expired 2026-01-01T00:00:00Z
- STACKME: 5% off, stackable with SAVE10 only, min spend 0, no exclusions
Cases (evaluate "now" = 2026-06-15T12:00:00Z):
- save10_ny: apply SAVE10 in US-NY
- fiveoff_ny: apply FIVEOFF in US-NY
- below_min: cart is 1× SKU-B only, apply SAVE10 → rejected_min_spend, discount 0, tax and total on 15.50
- expired: apply EXPIRED to the default cart → rejected_expired, discount 0
- stack_rejected: apply SAVE10 then FIVEOFF → second code rejected_stack; first discount remains
- stack_ok: apply SAVE10 then STACKME (SAVE10 first on eligible, then 5% on remaining merchandise)
- oregon_save10: SAVE10, address US-OR (tax 0)
For each case output discount, tax, total as strings with 2 dp, and outcome applied or rejected_*.
