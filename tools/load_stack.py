#!/usr/bin/env python3
"""load_stack.py — load the full 12-year 6E option-chain stack + health check.
Run from the repo root:  python tools/load_stack.py
"""
import glob
from pathlib import Path
import pandas as pd

ROOT = Path(__file__).parent.parent
frames = []
for f in sorted(glob.glob(str(ROOT / "panels" / "6E_option_chain_daily_*.parquet"))):
    year = int(Path(f).stem[-4:])
    p = pd.read_parquet(f)
    p["date"] = pd.to_datetime(p.date)
    frames.append(p[p.date.dt.year == year])          # year-trim rule (manifest)
stack = pd.concat(frames, ignore_index=True)

print("6E OPTION-CHAIN STACK — HEALTH CHECK")
print(f"  rows: {len(stack):,}   sessions: {stack.date.dt.date.nunique():,}")
print(f"  span: {stack.date.min().date()} -> {stack.date.max().date()}")
print(f"  duplicate keys: {stack.duplicated(['date','contract','strike','right']).sum()} (must be 0)")
print(f"  negative dte: {(stack.dte_days<0).sum()} (must be 0)")
print(f"  calls: {(stack.right=='C').sum():,}   puts: {(stack.right=='P').sum():,}")
print(f"  median chain size/day: {stack.groupby(stack.date.dt.date).size().median():.0f} options")
print("ready — `stack` holds the full history (import this file or copy the loop).")
