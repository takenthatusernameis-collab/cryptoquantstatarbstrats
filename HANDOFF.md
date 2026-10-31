# DURABLE HANDOFF | 2026-10-31T20:01:18Z | SINGLE MANDATORY NEXT TASK

## REPO IDENTITY (LAW) — PRIORITIZE BY REPO NAME
- Repo: `cryptoquantstatarbstrats` — **Crypto Quant Stat Arb Strategies**.
- **CORE = COINTEGRATION/PAIRS TRADING.** All other work serves cointegration rigor.
- Real data only: Binance public REST via www.binance.com. Never fabricate.
- Coasting = failure. Every action produces checkable artifacts, tests, provenance, logs.

## CURRENT VERIFIED STATE (2026-10-31T20:01:18Z)
- Branch: `main` (clean).
- `use_enriched_gates` default flipped to `True` (fail-closed) in `strategies/pairs_trading.py`.
- Enriched gate tests present (structural breaks flagged, missing/None, causality, hedge ratio guards).
- GREEN baseline target: ruff + pytest (>=555 passed) + mypy.

## SINGLE MANDATORY OBJECTIVE (HEAVY WORK REQUIRED)
**Close the cointegration rigor loop on real data.** Make every pair either (a) pass all 7 enriched gates on real Binance data, or (b) be honestly marked `blocked_or_insufficient_data` with full provenance. Priority order:
1. Fix POL/BTC rolling_stability failure (all_pass False) — diagnose window instability, document or fix.
2. Expand real-data coverage so remaining pairs (BTC/SOL/ADA/ETH/DOT) with hl>500 are either improved via longer history or honestly blocked.
3. Add a causality test proving gates use trailing data only (no lookahead).
4. Re-run `examples/run_portfolio_real.py` unbuffered; refresh `reports/portfolio_real.json`.
5. Keep suite green; no regressions; no commits unless requested.

## HARD CONSTRAINTS
- REAL DATA ONLY — isolated tests only with explicit `fabricated_data: true`
- NO SHORTCUTS / NO FABRICATION
- PRESERVE GREEN — >=555 passed, 0 new failures
- HEAVY MANDATE — complete full campaign, no coasting
- COINTEGRATION IS LAW
- CAUSAL ONLY — no lookahead
- UNBUFFERED — `python -u`

(End of file)
