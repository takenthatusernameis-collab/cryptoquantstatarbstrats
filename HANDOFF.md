# HANDOFF (SINGLE DURABLE HANDOFF)

TIMESTAMP: 2026-11-04T19:31:37Z
REPO: cryptoquantstatarbstrats
FOCUS: Crypto Quantitative Statistical Arbitrage Strategies (Cointegration/Pairs First)

---

## INITIAL TASK MESSAGE (PASTE AS FIRST MESSAGE FOR NEXT AGENT)

```
You are picking up cryptoquantstatarbstrats. NO "investigate only" loops. DO HEAVY WORKING IMMEDIATELY.

REPO-NAME PRIORITY (non-negotiable): cryptoquantstatarbstrats = Crypto Quant Stat Arb Strategies.
Cointegration/pairs trading IS the core edge. Everything else (mean reversion, momentum, term structure,
volatility surface) is secondary and must not displace pairs work.

OBJECTIVE: Deliver a verifiably working, REAL-DATA-ONLY end-to-end crypto pairs statistical arbitrage pipeline
(pair selection -> cointegration/spread construction -> z-score signals -> realistic backtest with costs)
that produces concrete, reproducible metrics from real code paths. Treat "cointegration is the core edge"
as non-negotiable. Real data only. Never fabricate candles/IV/funding/basis. Follow existing provenance
patterns (real_data_only, fabricated_data, blocked_routes, computed_at, rationale).

PRIMARY BLOCKER (INFERRED - REMOVE FIRST):
  `examples/run_pairs.py` now completes end-to-end (exit 0, 5064 bars BTC/ETH/SOL, walk-forward sweep) but
  `reports/pairs_real_market.json` shows trades_count=0, total_return=0, sharpe=0, maxDD=0, final_equity=100000.
  Inferred root cause: `strategies/pairs_trading.py` enriched gates are fail-closed under strict mode
  (`use_enriched_gates=True`, `strict_enriched_gates=True`). `rolling_stable_ok` requires a 720-bar trailing
  window (utils/cointegration.py), but walk-forward test windows are only 100 bars (train=500/test=100), so
  per-bar diagnostics report insufficient_data -> rolling_stable_ok=False -> enriched_ok_arr=0 -> state=0 on
  every bar -> zero entries -> zero trades. Even the full 5064-bar replay yields zero, confirming gates block
  all entries rather than a window-length artifact only.
  FIX DIRECTION (not a mandate, but the inferred bottleneck):
    - Diagnose exactly which gate(s) fail and on what share of bars (emit per-bar gate breakdown to a report).
    - Make the pipeline emit real trades with concrete metrics: either the gates genuinely pass on a subset of
      bars and entries should fire, or the gate thresholds/window need to be calibrated so the edge is exercised
      on real data without fabrication. Never coerce a failing gate to pass; fail-closed stays.
    - Target: nonzero trades_count, nonzero total_return, nonzero sharpe/maxDD in pairs_real_market.json and a
      fresh reports/handoff_proof_<UTC>.json.

EXECUTE IN THIS EXACT ORDER (remove bottlenecks first):

1. TARGETED HEALTH CHECK (FAST - MUST PASS)
   - Deps: `python -c "import numpy,pandas,statsmodels,scipy,yaml; print('ok')"`
   - Targeted pairs/cointegration tests (NOT full suite):
     `python -m pytest -v tests/test_cointegration_campaign31_mt.py tests/test_cointegration_diagnostics_schema.py tests/test_pairs_real_market.py tests/test_cointegration_threshold_invariance.py -q`
   - Expected: 40 passed. Fix any import/env issues in pyproject/requirements immediately.

2. MAP REAL DATA & PROVENANCE (BLOCKER REMOVAL)
   - Inspect `data/loader.py`, `data/cache.py`. Cached Binance data exists in `data/cache/` (BTC, ETH, SOL,
     ADA, AVAX, BNB, DOT, LINK, LTC, POL, XRP at 1h, 2026-04-01 -> 2026-10-30).
   - Check `reports/pairs_real_market.json` and `reports/cointegration_diagnostics_real.json` for provenance.
   - `api.binance.com` returns HTTP 451 in this env; loader must try `www.binance.com` first or use cache.
   - Record hosts_tried/blocked_routes/cache_used honestly in all proof artifacts.

3. WIRE ONE PAIRS PATH END-TO-END (CORE - HEAVY WORK)
   - Focus: `strategies/pairs_trading.py` (CointegrationPairsStrategy), trace `backtest/engine.py`
     (`_signals_to_weights` gives explicit per-asset weights precedence), costs/slippage/regime gating.
   - Run: `timeout 1800 python examples/run_pairs.py 2>&1 | tail -150` (BTC/ETH, walk-forward 4 splits rolling).
   - Fix integration gaps until script completes and writes `reports/pairs_real_market.json` WITH NONZERO
     trades and metrics. No stubs/fabrication. Resolve the PRIMARY BLOCKER above.

4. HARDEN STAT-ARB MATH (CORE - HEAVY WORK)
   - Causal rolling hedge ratio: positive, clipped, guarded (no inf/nan; >1e-18; clip [1e-6,1e6]).
   - Opposing legs preserved via explicit per-asset weights (engine must not overwrite).
   - Enriched gates fail-closed: `use_enriched_gates=True`, `strict_enriched_gates=True`. Any missing/None/false blocks entries.
   - Engle-Granger + Johansen + spread MR + HL bounds + leg stationarity + rolling stability + structural breaks.
   - Causal/trailing only. Never fabricate gate values.

5. ADD REALISM & PRODUCE PROOF (REQUIRED - HEAVY WORK)
   - Ensure fee_rate/slippage/capital constraints applied (engine handles turnover costs).
   - Extract concrete metrics from engine/results (trades, fills, PnL, cum returns, Sharpe, maxDD, Calmar, costs).
   - Write durable proof: `reports/handoff_proof_<UTC_TIMESTAMP>.json` with config, data provenance
     (real_data_only/fabricated_data/hosts/blocked_routes/cache_used), gates_summary, trades_count,
     equity_curve_summary, key_metrics, files_modified, reproduction_command, artifacts, verification.
   - Re-run targeted tests. Fix failures blocking core pairs path. Leave repo runnable.

RULES:
- Prioritize unblocking execution over docs. Write code to fix failures.
- Full suite large/slow - use targeted runs. Expand only if blocking core pairs.
- Real data only. Never fabricate candles/IV/funding/basis.
- Stay laser-focused on pairs/spreads/cointegration per repo name.
- Commit nothing unless explicitly asked. Update handoff only for new hard blockers.
- Success = modified code + working end-to-end pairs stat-arb run + verifiable proof artifact with concrete metrics from real code paths.

FOCUS CAMPAIGN (future agents MUST do heavy work):
- Every session re-runs targeted pairs/cointegration tests (40 passed baseline) and confirms `examples/run_pairs.py`
  completes end-to-end against real data BEFORE declaring progress. A run that completes with zero trades is NOT
  progress - it is the blocker to fix.
- Any new pair must pass full enriched cointegration gate set with full provenance.
- Not complete until a fresh `reports/handoff_proof_*.json` exists with concrete metrics (nonzero trades,
  nonzero total_return/sharpe/maxDD) from a real-code-path run.
- If blocked/inefficient, remove bottlenecks immediately - no investigation-only loops. The inferred zero-trades
  gate blocker (strategies/pairs_trading.py:276-381, rolling 720-bar stability vs short test windows) must be
  resolved before any session is considered effective.
```

---

## KNOWN STATE (INFERRED)
- Deps: OK (`numpy,pandas,statsmodels,scipy,yaml` import).
- Targeted tests: 40 passed (verified 2026-11-04T19:26Z).
- `examples/run_pairs.py`: COMPLETES end-to-end (exit 0), 5064 hourly bars BTC/ETH/SOL 2026-04-01->2026-10-28,
  writes `reports/pairs_real_market.json`, BUT trades_count=0, total_return=0, sharpe=0, maxDD=0,
  final_equity=100000 (PRIMARY BLOCKER - see above).
- `strategies/pairs_trading.py`: causal rolling hedge ratio with guards, opposing legs via explicit weights,
  enriched gates (fail-closed, strict default). Gates block all entries currently.
- `backtest/engine.py`: explicit per-asset weights precedence (_signals_to_weights), costs/slippage, regime gating,
  walk-forward utilities (train=500/test=100, rolling, 4 splits).
- `data/loader.py`, `data/cache.py`: Binance loader with retries/fallbacks; disk cache present for 11 symbols
  1h 2026-04-01->2026-10-30.
- Network: `api.binance.com` HTTP 451; use `www.binance.com` or cached data.
- Existing proofs: `reports/handoff_proof_20261104T175317Z.json`, `...T190006Z.json`, `...T190220Z.json` (all
  trades_count 0 on those runs).

## BOTTLENECK REMOVAL PRIORITY
1. Environment/deps - ensure imports work (verified OK).
2. Zero-trades gate blocker - diagnose per-bar gate failures in pairs_trading.py enriched-gate path
   (rolling 720-bar stability vs short walk-forward windows); make pipeline emit real trades/metrics.
3. End-to-end execution - run `examples/run_pairs.py` to completion with nonzero trades; capture full output.
4. Stat-arb hardening - verify causal behavior and gate enforcement without fabrication.
5. Proof artifact - generate fresh `reports/handoff_proof_<UTC_TIMESTAMP>.json` with concrete metrics.

## IMMEDIATE ACTIONS FOR NEXT AGENT
- [ ] Verify deps: `python -c "import numpy,pandas,statsmodels,scipy,yaml; print('ok')"`
- [ ] Run targeted tests: `python -m pytest -v tests/test_cointegration_campaign31_mt.py tests/test_cointegration_diagnostics_schema.py tests/test_pairs_real_market.py tests/test_cointegration_threshold_invariance.py -q` (expect 40 passed)
- [ ] Run pairs example: `timeout 1800 python examples/run_pairs.py 2>&1 | tail -200` (confirm zero-trades blocker)
- [ ] Diagnose per-bar enriched-gate failures (strategies/pairs_trading.py:276-381); identify which gate blocks entries and on what share of bars.
- [ ] Fix so pipeline emits real trades with concrete metrics; re-run example until pairs_real_market.json has nonzero trades_count/total_return/sharpe/maxDD.
- [ ] Extract metrics and write fresh proof artifact with full provenance
- [ ] Re-run targeted tests after changes; leave repo runnable
