"""
Backtest replay — AIProve bounty `eth-pnl-fixed`.

Replays positions.csv against bars.csv with an explicit cost model.
Trade at close[i] when the target position changes; PnL accrues on the
position held from close[i] to close[i+1]. Starting capital $10,000,
1 ETH per unit of position.

COST MODEL (ASSUMED — the sandbox's exact maker/taker fees and slippage
scale are NOT published in the bounty brief or the public grader repo,
so this is the documented assumption; see README.md sensitivity table):
  fee     = 5 bps (0.0005) per leg on notional traded
  slippage= 2 bps (0.0002) per leg on notional traded

Usage:
    python3 backtest.py [bars.csv] [positions.csv] [--fee 0.0005] [--slip 0.0002]
Writes results.json and equity.csv, prints a summary incl. IS/OOS split
(first 720 bars / last 720 bars) and max drawdown.
Stdlib only.
"""
import argparse
import csv
import json


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("bars", nargs="?", default="bars.csv")
    ap.add_argument("positions", nargs="?", default="positions.csv")
    ap.add_argument("--fee", type=float, default=0.0005)
    ap.add_argument("--slip", type=float, default=0.0002)
    ap.add_argument("--capital", type=float, default=10000.0)
    args = ap.parse_args()

    with open(args.bars, newline="") as f:
        bars = list(csv.DictReader(f))
    closes = [float(r["close"]) for r in bars]
    with open(args.positions, newline="") as f:
        pos_rows = list(csv.DictReader(f))
    pos = [int(r["position"]) for r in pos_rows]
    assert len(pos) == len(closes), "positions/bars length mismatch"

    cash = args.capital
    held = 0.0
    peak = cash
    mdd = 0.0
    trades = 0
    gross = 0.0
    costs = 0.0
    equity = [cash]
    for i in range(len(closes) - 1):
        if pos[i] != held:
            notional = abs(pos[i] - held) * closes[i]
            c = notional * (args.fee + args.slip)
            costs += c
            cash -= c
            trades += 1
            held = pos[i]
        d = held * (closes[i + 1] - closes[i])
        gross += d
        cash += d
        equity.append(cash)
        peak = max(peak, cash)
        mdd = max(mdd, (peak - cash) / peak)

    def split(a, b):
        # PnL over bars a..b-1, replayed standalone from flat, same costs
        c0 = args.capital
        h = 0.0
        for i in range(a, b - 1):
            if pos[i] != h:
                c0 -= abs(pos[i] - h) * closes[i] * (args.fee + args.slip)
                h = pos[i]
            c0 += h * (closes[i + 1] - closes[i])
        return c0 - args.capital

    # buy & hold benchmark: +1 ETH for the whole sample
    bh = closes[-1] - closes[0]

    results = {
        "bounty": "eth-pnl-fixed",
        "capital_usd": args.capital,
        "position_size_eth": 1,
        "fee_per_leg": args.fee,
        "slippage_per_leg": args.slip,
        "bars": len(closes),
        "net_pnl_usd": round(cash - args.capital, 2),
        "gross_pnl_usd": round(gross, 2),
        "total_costs_usd": round(costs, 2),
        "trades": trades,
        "max_drawdown_pct": round(mdd * 100, 2),
        "in_sample_pnl_usd_bars_0_720": round(split(0, 720), 2),
        "out_of_sample_pnl_usd_bars_720_1440": round(split(720, 1440), 2),
        "buy_and_hold_1eth_pnl_usd": round(bh, 2),
        "final_equity_usd": round(cash, 2),
    }
    with open("results.json", "w") as f:
        json.dump(results, f, indent=2)
    with open("equity.csv", "w", newline="") as f:
        w = csv.writer(f)
        w.writerow(["minute", "equity_usd"])
        for i, e in enumerate(equity):
            w.writerow([i, round(e, 2)])
    print(json.dumps(results, indent=2))


if __name__ == "__main__":
    main()
