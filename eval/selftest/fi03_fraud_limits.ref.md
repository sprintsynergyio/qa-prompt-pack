| ID | Rule | Setup | Action | Expected |
|---|---|---|---|---|
| 1 | per-tx inclusive | limit 200000 | transfer 200000 | allow, audit allow |
| 2 | per-tx over | limit 200000 | transfer 200001 | refuse |
| 3 | daily across channels | 250000 web then 250000 mobile | second transfer | allow (daily 500000 inclusive) |
| 4 | daily +1 | after 500000 | transfer 1 | refuse |
| 5 | velocity | 4 completed transfers in 10 minutes | 5th | hold_for_review, funds not released |
| 6 | cooling | first transfer to a new payee | transfer | hold_for_review |
| 7 | processor decline | card 4000000000000002 | pay | refuse, not hold_for_review |
