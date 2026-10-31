# DURABLE HANDOFF | 2026-10-31T20:19:43Z | SINGLE MANDATORY NEXT TASK

## REPO IDENTITY (LAW) — PRIORITIZE BY REPO NAME
- Repo: `cryptoquantstatarbstrats` — **Crypto Quant Stat Arb Strategies**.
- **CORE = COINTEGRATION/PAIRS TRADING.** All other work serves cointegration rigor.
- Real data only: Binance public REST via `www.binance.com`. Never fabricate.
- Coasting = failure. Every action produces checkable artifacts, tests, provenance, logs.

## CURRENT VERIFIED STATE (2026-10-31T20:19:43Z)
- Branch: `main` (clean), up to date with `origin/main`. Last commit `dd32c7c chore(kilo): checkpoint agent session`.
- `use_enriched_gates` default flipped to `True` (fail-closed) in `strategies/pairs_trading.py`.
- Enriched gate tests present (structural breaks flagged, missing/None, causality, hedge ratio guards).
- `pip install -e ".[dev]"` completed in this session (numpy, pandas, sklearn, statsmodels, scipy, pytest, ruff, mypy).
- `ruff check backtest/ strategies/ utils/ tests/ examples/` — **ALL CHECKS PASSED**.
- GREEN baseline target: ruff + pytest (>=555 passed) + mypy. Full suite partially hangs on expensive per-bar enriched-diagnostics fallback — isolate slow tests, do not skip assertions.

## BOTTLENACKS REMOVED (so progress can continue)
- Abandoned the repeatedly failing/cancelled `fix/causal-pairs-validation-2026-10-27` branch (Ruff failures + `ModuleNotFoundError: numpy/sklearn/yaml` + cancelled CI loops across 3 Python versions). Do **not** resurrect it; all work lands on `main`.
- Environment dependency gap closed (dev stack installed). Next session starts from a runnable env.
- `fix/noncompounding-overlap-pair-caps-20261030` remote branch is a destructive sidetrack (deletes data cache, tests, utils) — do NOT merge; all work lands on `main`.

## SINGLE MANDATORY OBJECTIVE (HEAVY WORK REQUIRED — UNAVOIDABLE)
**Close the cointegration rigor loop on real data.** Make every pair either (a) pass all 7 enriched gates on real Binance data, or (b) be honestly marked `blocked_or_insufficient_data` with full provenance. This is the focus campaign; future agents must not defer it.
1. Fix POL/BTC `rolling_stability` failure (all_pass False) — diagnose window instability, document or fix.
2. Expand real-data coverage so remaining pairs (BTC/SOL/ADA/ETH/DOT) with hl>500 are either improved via longer history or honestly blocked.
3. Add a causality test proving gates use trailing data only (no lookahead).
4. Re-run `examples/run_portfolio_real.py` unbuffered (`python -u`); refresh `reports/portfolio_real.json`.
5. Keep suite green; no regressions; no commits unless requested.

## HARD CONSTRAINTS
- REAL DATA ONLY — isolated tests only with explicit `fabricated_data: true`
- NO SHORTCUTS / NO FABRICATION
- PRESERVE GREEN — >=555 passed, 0 new failures
- HEAVY MANDATE — complete full campaign, no coasting
- COINTEGRATION IS LAW
- CAUSAL ONLY — no lookahead
- UNBUFFERED — `python -u`

## VERIFICATION COMMANDS (run before declaring done)
- `python -m ruff check backtest/ strategies/ utils/ tests/ examples/`
- `python -m pytest tests/ -q` (>=555 passed, 0 failures; isolate any hanging enriched-diagnostics test)
- `python -m mypy backtest/ strategies/ utils/`

(End of file)
