# HANDOFF (SINGLE DURABLE HANDOFF)

TIMESTAMP: 2026-11-04T18:31:33Z
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

EXECUTE IN THIS EXACT ORDER (remove bottlenecks first):

1. TARGETED HEALTH CHECK (FAST - MUST PASS)
   - Deps: `python -c "import numpy,pandas,statsmodels,scipy,yaml; print('ok')"`
   - Targeted pairs/cointegration tests (NOT full suite):
     `python -m pytest -v tests/test_cointegration_campaign31_mt.py tests/test_cointegration_diagnostics_schema.py tests/test_pairs_real_market.py tests/test_cointegration_threshold_invariance.py -q`
   - Expected: 40 passed. Fix any import/env issues in pyproject/requirements immediately.

2. MAP REAL DATA & PROVENANCE (BLOCKER REMOVAL)
   - Inspect `data/loader.py`, `data/cache.py`. Cached Binance data exists in `data/cache/`.
   - Check `reports/pairs_real_market.json` and `reports/cointegration_diagnostics_real.json` for provenance.
   - `api.binance.com` returns HTTP 451 in this env; loader must try `www.binance.com` first or use cache.
   - Record hosts_tried/blocked_routes/cache_used honestly in all proof artifacts.

3. WIRE ONE PAIRS PATH END-TO-END (CORE - HEAVY WORK)
   - Focus: `strategies/pairs_trading.py` (CointegrationPairsStrategy), trace `backtest/engine.py`
     (`_signals_to_weights` gives explicit per-asset weights precedence), costs/slippage/regime gating.
   - Run: `timeout 1800 python examples/run_pairs.py 2>&1 | tail -150` (BTC/ETH, walk-forward 4 splits rolling).
   - Fix integration gaps until script completes and writes `reports/pairs_real_market.json`. No stubs/fabrication.

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
- Every session re-runs targeted pairs/cointegration tests (40 passed baseline) and confirms `examples/run_pairs.py` completes end-to-end against real data before declaring progress.
- Any new pair must pass full enriched cointegration gate set with full provenance.
- Not complete until fresh `reports/handoff_proof_*.json` exists with concrete metrics from real-code-path run.
- If blocked/inefficient, remove bottlenecks immediately - no investigation-only loops.
```

## KNOWN STATE (INFERRED)
- Targeted tests: 40 passed (verified 2026-11-04T18:30:52Z).
- `strategies/pairs_trading.py`: causal rolling hedge ratio with guards, opposing legs via explicit weights, enriched gates (fail-closed), cointegration with caching.
- `backtest/engine.py`: explicit per-asset weights precedence, costs/slippage, regime gating, walk-forward utilities.
- `data/loader.py`, `data/cache.py`: Binance loader with retries/fallbacks; disk cache present.
- `examples/run_pairs.py`: walk-forward sweep BTC/ETH/SOL, writes `reports/pairs_real_market.json`.
- `reports/handoff_proof_20261104T175317Z.json` exists from prior session (trades_count 0 on that run).
- Network: `api.binance.com` HTTP 451; use `www.binance.com` or cached data.

## BOTTLENECK REMOVAL PRIORITY
1. Environment/deps - ensure imports work.
2. Data loading - leverage cache/offline if network blocked.
3. End-to-end execution - run `examples/run_pairs.py` to completion, capture full output.
4. Stat-arb hardening - verify causal behavior and gate enforcement.
5. Proof artifact - generate fresh `reports/handoff_proof_<UTC_TIMESTAMP>.json` with concrete metrics.

## IMMEDIATE ACTIONS FOR NEXT AGENT
- [ ] Verify deps: `python -c "import numpy,pandas,statsmodels,scipy,yaml; print('ok')"`
- [ ] Run targeted tests: `python -m pytest -v tests/test_cointegration_campaign31_mt.py tests/test_cointegration_diagnostics_schema.py tests/test_pairs_real_market.py tests/test_cointegration_threshold_invariance.py -q`
- [ ] Run pairs example: `timeout 1800 python examples/run_pairs.py 2>&1 | tail -200`
- [ ] If fails, debug imports/integration (trace CointegrationPairsStrategy.generate_signals + BacktestEngine). Fix in existing modules.
- [ ] Extract metrics and write fresh proof artifact with full provenance
- [ ] Re-run targeted tests after changes
