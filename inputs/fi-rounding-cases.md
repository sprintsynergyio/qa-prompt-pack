Currency exponents: USD 2, JPY 0, BHD 3.
Modes: half_up (0.5 away from 0 at the keep-digit), half_even (banker's, ties to even keep-digit).
Work in decimal minor units. id and inputs:
- usd_half_up_125: USD 10.125, half_up → expected 2 dp
- usd_half_up_124: USD 10.124, half_up
- usd_half_up_135: USD 10.135, half_up
- usd_half_even_125: USD 10.125, half_even
- usd_half_even_135: USD 10.135, half_even
- jpy_half_up_1234: JPY 123.4, half_up (integer)
- jpy_half_up_1235: JPY 123.5, half_up (integer)
- bhd_half_up_12345: BHD 1.2345, half_up (3 dp)
- usd_split_10_three: split 10.00 USD across 3 recipients, remainder of 0.01 to the last; expected is a 3-value string "3.33,3.33,3.34"
- usd_fee_2pct_10_01: 2% fee on 10.01 USD, half_up to 2 dp
