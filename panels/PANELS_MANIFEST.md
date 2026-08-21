# PANELS_MANIFEST — the 6E option-chain study tables (v3 FINAL, 2026-08-20)
*THE conventions page. Any study (or future agent) reads this before touching a table.
Files: `6E_option_chain_daily_<YYYY>.parquet` (12 years). Built by chain_builder.py v3
from the ACCEPTED raw dataset (ACCEPTANCE_CERTIFICATE.md); all 12 built by ONE code
version in one run, 12/12 gates PASS; earlier versions archived in _v2_archive/ and
_prerulec_archive/ (nothing deleted, ever).*

## WHAT A TABLE IS
One parquet per year. One row = one option on one session — the FULL chain per day
(every strike anyone held, every expiry, calls + puts; ~600-1,200 options/day).
Schema: date, contract, strike, right (C/P), expiry_ts, dte_days, open_interest,
volume, settlement, session_high, session_low, highest_bid, lowest_offer,
underlying_fut, fut_settle, iv, delta, iv_flag, n_listed_universe.
open_interest is a LEVEL (contracts held at that day's close), not a change; day-over-
day builds (ΔOI) are computed downstream by differencing. Human viewing: chain_view.py
<date> opens a broker-style screen (calls | strike | puts) for any session.

## THE STACK (how studies load it)
Stack all 12 with each row taken from its OWNING calendar year's table (tables carry a
few boundary-buffer days of neighbors; the owning year's version is the final print —
the only cross-table differences are ~247 Jan-2 buffer rows, prelim-vs-final).
After year-trim: **2,602,683 rows · 2,941 sessions · 2015-01-02 → 2026-08-17 ·
zero duplicate keys · zero negative-dte rows** (verified 2026-08-20).

## THE v3 STORY (why these replaced the v2 tables — full disclosure)
Bryan eyeballed a random 2020 day and caught rows with negative days-to-expiry.
Root cause: **CME recycles instrument ids** (2020: 18% of ids carried >1 contract
within the year); v2 joined each id to its FIRST definition → 1.22% of rows wore the
wrong contract's name. v3 fixes: (1) TIME-AWARE join — each print attaches to the
definition version active on its session date; (2) recycling-boundary rule — a print
cannot belong to an expired contract; if the id's next version begins within 5 days,
it attaches there (definition records can lag a recycled contract's first trades by
~1 day); (3) post-expiry runoff prints (exchange cleanup records, e.g. final OI=0
the morning after expiry) are dropped + counted, threshold-gated; (4) PERMANENT gate:
any surviving negative-dte row fails the build loudly. Side benefit: IV health
improved ~1-3 points every year (mislabeled junk removed).

## BINDING CONVENTIONS (every study inherits these)
1. **As-of rule:** open interest dated session d is PUBLISHED d+1 morning — usable for
   inference from d+1 on. Tables store the SESSION date.
2. **The one clock:** dte = calendar days to expiry, floor 0.5, /365 (B2 canonical).
   Skew/IV thresholds derive from THESE series, never pilot printouts (pilot used a
   slightly different clock; RR25 comparisons carry a 0.5 vol-pt tolerance).
3. **Keep-last:** prelim/final multi-prints resolve to the chronologically final print.
4. **NaN = not-reported, never imputed** (12 vendor-absent days; holiday-session
   settlement gaps — register in ACCEPTANCE_CERTIFICATE §3).
5. **Session dates:** 2016+ native exchange stamps (feed transition verified at the
   2015→2016 boundary). 2015 = RULE C derived (oi_dates.py; kept-value error ≤0.06%).
6. **IV discipline:** use iv_flag == "ok" rows for vol work; expiry_ts is tz-naive.
   Black-76 r=0; exact for 2015-16 XT European-style, approximation for American.
7. **Levels rule:** chain prices NEVER join the ratio-adjusted 1m master at price
   level — returns/timing joins only.
8. **Era comparability:** normalize universe-sensitive features by n_listed_universe;
   roots 6E/XT/6E1-5/1Q-5Q (2015-16) → EUU/xEU/MO/WE/TU/TH (2017+).

## GATE SCORECARD (v3 final run, all 12 in one pass, 2026-08-20; hand-checks 3/3 each)
| year | rows | sessions | IV ok | fut_settle | derived dates |
|---|---|---|---|---|---|
| 2015 | 206,806 | 253 | 83.0% | 100.0% | **90.1%** (RULE C) |
| 2016 | 144,659 | 253 | 86.4% | 100.0% | 0.0% (native) |
| 2017 | 174,757 | 253 | 85.4% | 98.9% | 0.0% |
| 2018 | 243,552 | 258 | 80.5% | 97.7% | 0.0% |
| 2019 | 200,926 | 252 | 88.7% | 100.0% | 0.0% |
| 2020 | 252,062 | 254 | 95.3% | 100.0% | 0.0% |
| 2021 | 204,963 | 254 | 95.3% | 100.0% | 0.0% |
| 2022 | 248,109 | 252 | 91.6% | 99.6% | 0.0% |
| 2023 | 235,629 | 251 | 91.0% | 100.0% | 0.0% |
| 2024 | 223,861 | 253 | 92.5% | 99.6% | 0.0% |
| 2025 | 304,116 | 256 | 87.4% | 98.4% | 0.0% |
| 2026 | 170,013 | 160* | 90.9% | 98.9% | 0.0% |

*2026 through Aug-17 (connection intentionally severed; daily capture ready to re-enable).

## CERTIFICATION CHAIN
Raw accepted (33-window audit battery, continuity 27/27, $35 portal-reconciled, raw
receipts verified byte-identical 721/721 on 2026-08-20) → v3 known-answer proof:
**May-2026 rebuilt and matched the pilot table 100.000% on OI + settlement + volume,
theory-anchor exact** → 12/12 year gates in one uniform run → stack sweep clean
(0 dups, 0 negative-dte). Three line-stops during v3 development, each diagnosed to
the exact row and converted to a permanent rule — none shipped.

## SHARING NOTE
⚠️ This is CME market data licensed via Databento: Bryan may USE it; redistribution
of raw prints (public posting) may violate CME licensing. Derived analytics are
generally safe to share. Audience decision + license check REQUIRED before any file
leaves this machine. DATA_DICTIONARY for recipients: pending Bryan's go.

## NEXT (Phase C door)
Feature layer runs on THE STACK only after Bryan locks
`_projects/oi_hedging_unwind_master/PHASE_C_FEATURE_SPEC_DRAFT.md` (15 open questions).
