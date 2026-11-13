"""
ETH backtest strategy — AIProve bounty `eth-pnl-fixed`.

Rule (deliberately simple, 3 parameters, chosen for robustness not max fit):
  EMA(12) vs EMA(48) on close, with a 5 bp deadband and a 30-minute
  post-trade cooldown. Position is -1 / 0 / +1 ETH, decided from bars
  up to and including minute i, executed at close[i].

  - spread = (EMA12 - EMA48) / EMA48
  - target = +1 if spread > +0.0005, -1 if spread < -0.0005, else 0
  - if target != current position and < 30 min since the last trade,
    keep the current position (cooldown).

No look-ahead: every decision uses closes <= i only.
Stdlib only. Usage:
    python3 strategy.py [bars.csv] [positions.csv]
Writes positions.csv: minute,position
"""
import csv
import sys


def ema(values, n):
    k = 2.0 / (n + 1)
    out = []
    e = values[0]
    for v in values:
        e = v * k + e * (1 - k) if out else v
        out.append(e)
    return out


def positions(closes, fast=12, slow=48, deadband=0.0005, cooldown=30):
    ef = ema(closes, fast)
    es = ema(closes, slow)
    out = []
    current = 0
    last_trade = -10 ** 9
    for i in range(len(closes)):
        spread = (ef[i] - es[i]) / es[i]
        target = 1 if spread > deadband else (-1 if spread < -deadband else 0)
        if target != current and i - last_trade < cooldown:
            target = current
        if target != current:
            last_trade = i
        current = target
        out.append(current)
    return out


def main():
    bars_path = sys.argv[1] if len(sys.argv) > 1 else "bars.csv"
    out_path = sys.argv[2] if len(sys.argv) > 2 else "positions.csv"
    with open(bars_path, newline="") as f:
        rows = list(csv.DictReader(f))
    closes = [float(r["close"]) for r in rows]
    pos = positions(closes)
    with open(out_path, "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["minute", "position"])
        for i, p in enumerate(pos):
            w.writerow([i, p])
    print(f"wrote {out_path}: {len(pos)} minutes, "
          f"long {pos.count(1)}, flat {pos.count(0)}, short {pos.count(-1)}")


if __name__ == "__main__":
    main()
