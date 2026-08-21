# Data Dictionary — 6E_option_chain_daily_<YYYY>.parquet

One row = **one option on one trading day**. A typical day carries the full chain:
~600–1,200 rows (every strike with open positions, all expiries, calls + puts).

| column | plain meaning | notes |
|---|---|---|
| `date` | The trading session this row describes | Session date; the OI number was *published* the next morning (as-of rule) |
| `contract` | The exchange's name for this option | e.g. `EUUM6 P1170` = monthly June-2026 put, strike 1.1700 |
| `strike` | The strike price | e.g. 1.1700 dollars per euro |
| `right` | `C` = call, `P` = put | one row per side — puts and calls are separate rows |
| `expiry_ts` | When the option expires | timezone-naive timestamp |
| `dte_days` | Calendar days until expiry | 0 = expires today; never negative (gated) |
| `open_interest` | **Contracts held at that day's close** | a LEVEL, not a change; the positioning number |
| `volume` | Contracts traded that session | |
| `settlement` | Official closing price | in price points (e.g. 0.0074) |
| `session_high` / `session_low` | That option's traded range | often empty for untraded strikes |
| `highest_bid` / `lowest_offer` | Best quote prints | often empty |
| `underlying_fut` | Which future the option is on | e.g. `6EU5` = Sep-2015 future |
| `fut_settle` | That future's official close, same day | the "spot" reference |
| `iv` | Implied volatility (the priced-in fear gauge) | computed via Black-76, r=0 |
| `delta` | Hedge sensitivity (−1…+1) | computed |
| `iv_flag` | Health of the iv/delta math | use `"ok"` rows for vol work; other values mark near-worthless / expiry-day rows where the math is fragile |
| `n_listed_universe` | How many options existed that day | divide by this to compare 2015 fairly to 2026 |

## Known limitations (on the record — see panels/PANELS_MANIFEST.md for all)
- 12 trading days across 2010–2018 don't exist at the data vendor (exchange feed
  skips, mostly holiday-adjacent) — itemized in the manifest.
- Holiday part-sessions sometimes report positions without prices (price = NaN).
- 2015 session dates are derived by a validated rule (measured error ≤0.06% of
  values); 2016+ are native exchange stamps.
- Pre-2017 product names differ (6E/XT/6E1-5/1Q-5Q vs modern EUU/1EU-5EU/MO/WE/TU/TH)
  — same underlying market, verified continuous across the rename.
