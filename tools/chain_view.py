#!/usr/bin/env python3
"""chain_view.py — broker-style option-chain screen for any date.
Run from the repo root:  python tools/chain_view.py 2020-06-15  [--front]
Writes VIEW_chain_<date>.csv and opens it (macOS `open`; on Windows/Linux open manually).
"""
import subprocess, sys, platform
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).parent.parent
day = sys.argv[1]
front_only = "--front" in sys.argv

p = pd.read_parquet(ROOT / "panels" / f"6E_option_chain_daily_{day[:4]}.parquet")
p["date"] = pd.to_datetime(p.date)
d = p[p.date == day].copy()
if d.empty:
    sys.exit(f"no session on {day} (weekend/holiday/vendor-absent?) — try a nearby weekday")

d["expiry"] = pd.to_datetime(d.expiry_ts).dt.date
spot = d.fut_settle.dropna().median()
calls = d[d.right == "C"].set_index(["expiry", "strike"])
puts = d[d.right == "P"].set_index(["expiry", "strike"])
view = pd.DataFrame({
    "call_OI": calls.open_interest, "call_vol": calls.volume, "call_settle": calls.settlement,
    "call_iv": calls.iv.round(4),
}).join(pd.DataFrame({
    "put_settle": puts.settlement, "put_vol": puts.volume, "put_OI": puts.open_interest,
    "put_iv": puts.iv.round(4),
}), how="outer").reset_index()
view.insert(2, "dte", (pd.to_datetime(view.expiry) - pd.Timestamp(day)).dt.days)
view["near_spot"] = (view.strike - spot).abs() < 0.01
view = view.sort_values(["expiry", "strike"])
if front_only:
    view = view[view.expiry.isin(sorted(view.expiry.unique())[:3])]

out = ROOT / f"VIEW_chain_{day}.csv"
cols = ["expiry", "dte", "call_OI", "call_vol", "call_settle", "call_iv",
        "strike", "put_iv", "put_settle", "put_vol", "put_OI", "near_spot"]
view[cols].to_csv(out, index=False)
print(f"{day}: {len(view)} strike-expiry lines | spot ~{spot:.4f} | "
      f"call OI {view.call_OI.sum():,.0f} vs put OI {view.put_OI.sum():,.0f} -> {out.name}")
if platform.system() == "Darwin":
    subprocess.run(["open", str(out)])
