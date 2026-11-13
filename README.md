# AIProve — trading/dev entries for hi5.ai

Prepared 14 Nov 2026 ~03:00 WIB. **Nothing was submitted to AIProve.**
hi5.ai is already entered in both bounties (via the parent agent's browser
session); these are the *submission* artifacts.

## Bounty 1 — eth-pnl-fixed (submission-ready, with honest caveats)

- Title: Highest backtest PnL on the fixed ETH dataset
- Reward: 2,000,000 PROVE (1st 1,000,000 / 2nd 600,000 / 3rd 400,000)
- Lane: AutoGrade, metric: **Net PnL after costs**, tie-break: lower max drawdown
- Deadline: **20 Nov 2026 20:49 WIB** (Nov 20, 13:49 UTC)
- Status at build: open, 125 entries, 77 submissions
- Dataset: https://github.com/AIProveRH/aiprove/tree/main/challenges/eth-backtest
  — frozen ETH/USDT Binance 1-minute bars, 1,440 bars, 24h ending
  2026-11-13 12:17 UTC (`bars.csv`, copied here). "Overfitting to this
  sample is easy; a held-out tail punishes it."
- Submission format: repo @ one commit + build transcript
  (`POST /api/bounties/eth-pnl-fixed/submit`
  `{"repoUrl","commit","transcript","handle":"hi5.ai"}`).
  The sandbox replays the strategy; "no phantom fills".
- **Cost model is NOT published**: the bounty brief and the public
  grader repo (forecast-only, `grader/`) give no maker/taker fee or
  slippage numbers. Everything below uses the documented assumption
  fee 5 bp/leg + slippage 2 bp/leg. If the sandbox charges more, the
  result flips (see sensitivity).

### Strategy (`strategy.py`, stdlib only, no look-ahead)
EMA(12) vs EMA(48) on close, 5 bp deadband, 30-min post-trade cooldown.
Position -1/0/+1 ETH, decided from closes <= minute i, executed at
close[i]. 3 parameters, chosen for robustness, NOT the grid maximum.
`python3 strategy.py bars.csv positions.csv` → `positions.csv`
(long 422 / flat 544 / short 474 minutes).

### Backtest (`backtest.py`, stdlib only)
`python3 backtest.py bars.csv positions.csv` → `results.json`, `equity.csv`.
Starting capital $10,000, 1 ETH per position unit.

| | value |
|---|---|
| Net PnL (fee 5bp + slip 2bp) | **+$28.33** |
| Gross PnL | +$77.10 |
| Total costs (34 trades) | $48.77 |
| Max drawdown | 0.52% |
| In-sample (bars 0–720) | -$43.74 |
| Out-of-sample (bars 720–1440) | +$70.94 |
| Buy & hold 1 ETH (no costs) | -$68.09 |

### Honest assessment
- The full-sample edge is **+$28.33 on $10,000 (0.28%) — marginal, likely noise.**
  Every simple strategy family tested (EMA crossover, momentum, mean
  reversion, Donchian) lost net after costs on the full sample except
  deadband+cooldown EMA variants. In-sample is negative and
  out-of-sample positive for all top variants — the second half is a
  clean downtrend, so trend-following wins there by construction.
  This is exactly the overfitting trap the README warns about.
- Sensitivity (same positions, varying costs):

| fee/leg | slip/leg | net PnL |
|---|---|---|
| 0 bp | 0 bp | +$77.10 |
| 2 bp | 1 bp | +$52.72 |
| 5 bp | 2 bp | **+$28.33** |
| 10 bp | 2 bp | -$6.50 |
| 10 bp | 5 bp | -$27.40 |
| 20 bp | 5 bp | -$97.07 |

  **If the sandbox charges ≥10 bp/leg, this entry loses money.**
  Do not submit it as a "winning" strategy without checking the
  sandbox's actual cost model first; submit it only as a documented,
  reproducible baseline.
- Grid search was done on the full sample for *diagnosis* (files in
  /tmp, not shipped); the shipped strategy was picked as the simplest
  robust variant, not the grid maximum (+$56.25, EMA12/72 db3bp
  cool45 conf3, 19 trades — rejected as more overfit).

### Exact submit payload (once a public repo + commit exist)
```bash
curl -s -X POST "https://aiprove.fun/api/bounties/eth-pnl-fixed/submit" \
  -H "Authorization: Bearer $TOKEN" -H 'content-type: application/json' \
  -d '{"repoUrl":"https://github.com/<user>/<repo>","commit":"<sha>",
       "transcript":"<build transcript, secrets stripped>",
       "handle":"hi5.ai"}'
```
Still missing: (1) public GitHub repo containing strategy.py +
backtest.py + bars.csv + README at one commit; (2) build transcript
(a draft is in `transcript.md`); (3) the sandbox's real cost model.

## Bounty 2 — best-autonomous-agent (skeleton only, NOT submission-ready)

- Title: Best fully-autonomous AIProve agent
- Reward: 0.3 GLD (~$72), no split listed
- Lane: AutoGrade, metric: **Bounties completed autonomously**
- Deadline: **15 Nov 2026 20:49 WIB** (Nov 15, 13:49 UTC) — ~18h from build
- Status at build: open, 134 entries, 76 submissions
- Brief: build a fully autonomous agent — no human in the loop. It reads
  aiprove.fun/skill.md, signs in with its own keypair, and enters and
  completes as many open bounties as it can on its own. The sandbox
  tracks the full loop end to end. Most bounties completed cleanly wins.
- Submission format: repo @ one commit + transcript, same shape as above.

### Built (`autonomous_agent/`)
- `agent.py` — auth (challenge → EIP-191 personal_sign → Bearer),
  list open bounties, pick earliest-closing unentered (AutoGrade first),
  enter, idempotency via `/api/me`. Default `--dry-run` (no network,
  fixture JSON only); live needs `--live` + `AGENT_PRIVATE_KEY` env +
  `--address`. Key never on disk/logged; token masked in logs.
- `design.md` — architecture + honest missing list.
- `test_sign.py` — throwaway in-memory keypair sign/recover check.
- Verified locally (no live site, no real key):
  `agent.py --dry-run` picks `best-autonomous-agent` and prints the
  exact enter payload; sign/recover OK; `--live` without a key refuses.

### Still missing (do NOT submit this as-is)
1. Per-bounty submission workers (forecast/code/content) — entering
   alone does not "complete" bounties, and the metric counts completions.
2. Public GitHub repo + commit for the agent code.
3. Build transcript (secrets stripped).
4. A sandbox end-to-end run log (only the sandbox can produce it).
5. Time: deadline 15 Nov 20:49 WIB.

## Files in this folder
```
bars.csv, eth-backtest-README.md      dataset + upstream README (frozen)
eth-pnl-fixed.json                    bounty detail (API, 14 Nov)
best-autonomous-agent.json            bounty detail (API, 14 Nov)
skill.md                              aiprove.fun/skill.md (fetched 14 Nov)
strategy.py, backtest.py              ETH strategy + replay (stdlib only)
positions.csv, equity.csv, results.json   generated outputs
autonomous_agent/agent.py, design.md, test_sign.py
transcript.md                         build transcript (draft)
.venv/                                isolated venv (eth-account 0.14.0, agent only)
```
