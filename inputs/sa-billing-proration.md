Currency USD, exponent 2, half_up. Monthly period is 30 days. Plans: Starter 40.00, Pro 80.00.
Method (required): unused credit = half_up(remaining_days/30 * current_plan). new_charge = half_up(remaining_days/30 * new_plan). due = new_charge - credit (this may differ by 0.01 from half_up(remaining_days/30 * (new-current))).
"now" day index is 0-based from period start (day 0 is the start). remaining_days = 30 - day_index.
Cases:
- upgrade_day10: Starter → Pro on day 10 (remaining 20)
- downgrade_day10: Pro → Starter on day 10 (due may be negative: credit issued, access becomes Starter immediately)
- cancel_day10: Starter cancelled on day 10; no cash refund (customer keeps Starter until period end). credit=0, new_charge=0, due=0, access starter_until_period_end
- upgrade_day0: Starter → Pro on day 0 (remaining 30)
- upgrade_day29: Starter → Pro on day 29 (remaining 1)
- webhook_replay: the upgrade_day10 invoice.paid webhook is delivered twice with the same event_id; the account must change once (one invoice, one due).
access values: starter, pro, starter_until_period_end.
webhook_effect: applied or ignored_duplicate.
