#!/usr/bin/env python3
"""chain_view.py — broker-style option-chain view, format-matched to Bryan's original
May file (6e_chains_may1-20_chainview.csv): one row per strike per expiry per day,
calls on the left, strike in the middle, puts on the right.

Usage (from repo root):
  python tools/chain_view.py 2020-06-15                    one day -> opens in spreadsheet
  python tools/chain_view.py 2020-06-01 2020-06-30         a date range -> one combined file

Columns: date, root, contract, expiry_ts, underlying_fut, fut_settle, dte_days, strike,
         call_oi, call_vol, call_settle, call_iv, call_delta,
         put_oi,  put_vol,  put_settle,  put_iv,  put_delta
Note: shows strikes with OPEN POSITIONS (the panel convention); the original May file
also listed quoted-but-empty strikes as zero rows.
"""
import subprocess, sys, platform
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).parent.parent
start = sys.argv[1]
end = sys.argv[2] if len(sys.argv) > 2 and not sys.argv[2].startswith("-") else start

years = sorted({start[:4], end[:4]})
p = pd.concat([pd.read_parquet(ROOT / "panels" / f"6E_option_chain_daily_{y}.parquet")
               for y in years], ignore_index=True)
p["date"] = pd.to_datetime(p.date)
d = p[(p.date >= start) & (p.date <= end)].copy()
if d.empty:
    sys.exit(f"no sessions in {start}..{end}")

d["contract_base"] = d.contract.str.split().str[0]          # '1EUK6 P1080' -> '1EUK6'
d["root"] = d.contract_base.str[:-2]                        # '1EUK6' -> '1EU'
key = ["date", "root", "contract_base", "expiry_ts", "underlying_fut", "fut_settle",
       "dte_days", "strike"]
side = lambda r, pre: d[d.right == r].set_index(key)[["open_interest", "volume", "settlement", "iv", "delta"]] \
    .rename(columns={"open_interest": f"{pre}_oi", "volume": f"{pre}_vol",
                     "settlement": f"{pre}_settle", "iv": f"{pre}_iv", "delta": f"{pre}_delta"})
view = side("C", "call").join(side("P", "put"), how="outer").reset_index()
view = view.rename(columns={"contract_base": "contract"}).sort_values(["date", "expiry_ts", "strike"])
for c in ("call_oi", "call_vol", "put_oi", "put_vol"):
    view[c] = view[c].fillna(0)          # no positions on that side = 0 (May-file convention)
for c in ("call_iv", "put_iv", "call_delta", "put_delta"):
    view[c] = view[c].round(4)

cols = ["date", "root", "contract", "expiry_ts", "underlying_fut", "fut_settle",
        "dte_days", "strike", "call_oi", "call_vol", "call_settle", "call_iv",
        "call_delta", "put_oi", "put_vol", "put_settle", "put_iv", "put_delta"]
name = f"VIEW_chain_{start}" + ("" if end == start else f"_{end}")
out = ROOT / f"{name}.csv"
view[cols].to_csv(out, index=False)
print(f"{start}..{end}: {len(view):,} strike lines | {view.date.nunique()} session(s) | "
      f"call OI {view.call_oi.sum():,.0f} vs put OI {view.put_oi.sum():,.0f} -> {out.name}")
if platform.system() == "Darwin" and end == start:
    subprocess.run(["open", str(out)])
