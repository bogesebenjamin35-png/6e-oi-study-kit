# 6E Option-Chain Study Kit

Complete daily option-chain history for **6E (Euro FX futures, CME)** — every strike
anyone held, every expiry, puts and calls, one row per option per trading day.

**Coverage: 2015-01-02 → 2026-08-17 · 2,941 sessions · ~2.6M rows · 12 yearly files.**

Built and certified from official CME end-of-day records (Databento GLBX.MDP3):
33-window audit battery, double-purchase reproducibility (2×), known-answer proof
(May-2026 rebuilt and matched an independently built table 100.000% on positions,
prices, and volumes). Full conventions + certification chain: `panels/PANELS_MANIFEST.md`.
Column meanings: `DATA_DICTIONARY.md`.

## ⚠️ PRIVATE — do not make this repo public
This is licensed CME market data (via Databento). Use across the owner's own devices
is fine; **public redistribution of the raw prints may violate CME licensing.**
Keep the repo private. Derived analytics (measurements, findings, charts) are the
shareable layer, not these files.

## Setup on any device (Mac / Windows / Linux)
1. Install Python 3.10+
2. `pip install pandas pyarrow`
3. Clone this repo. Done.

## Load everything (the 12-year stack)
```python
python tools/load_stack.py          # loads all years + prints a health check
```
or in your own code:
```python
import pandas as pd, glob
frames = []
for f in sorted(glob.glob("panels/6E_option_chain_daily_*.parquet")):
    year = int(f[-12:-8])
    p = pd.read_parquet(f)
    p["date"] = pd.to_datetime(p.date)
    frames.append(p[p.date.dt.year == year])   # year-trim rule (see manifest)
stack = pd.concat(frames, ignore_index=True)
```

## View any day like a broker screen
```python
python tools/chain_view.py 2020-06-15       # opens calls | strike | puts in a spreadsheet
```

## The three rules to never break (short version — manifest has all eight)
1. Open interest dated day *d* was PUBLISHED the morning of *d+1* — never let a
   study "know" it earlier (look-ahead bias).
2. NaN means the exchange didn't report — never fill it in.
3. Use `iv_flag == "ok"` rows for any implied-vol work.
