# HANDOFF (SINGLE DURABLE HANDOFF)

TIMESTAMP: 2026-11-04T15:59:57Z
REPO: cryptoquantstatarbstrats
FOCUS: Crypto Quantitative Statistical Arbitrage Strategies (Cointegration/Pairs First)

---

## INITIAL TASK MESSAGE (PASTE AS FIRST MESSAGE FOR NEXT AGENT)

```
You are picking up cryptoquantstatarbstrats. NO "investigate only" loops. DO HEAVY WORKING IMMEDIATELY.

OBJECTIVE: Unblock and deliver a verifiably working, REAL-DATA-ONLY end-to-end crypto pairs statistical arbitrage pipeline (pair selection -> cointegration/spread construction -> z-score signals -> realistic backtest with costs) that produces concrete, reproducible metrics from real code paths. Treat "cointegration is the core edge" as non-negotiable.

EXECUTE IN THIS EXACT ORDER (remove bottlenecks first):

1. TARGETED HEALTH CHECK (FAST)
   - Do NOT run the full test suite blindly. Run targeted tests for the pairs/cointegration path first:
     `pytest -v tests/test_cointegration_campaign31_mt.py tests/test_cointegration_diagnostics_schema.py tests/test_pairs_real_market.py tests/test_cointegration_threshold_invariance.py -q`
   - Capture any ImportError/ModuleNotFoundError. Fix deps/path issues using pyproject.toml/requirements.txt before expanding scope.

2. MAP REAL DATA & PROVENANCE (BLOCKER)
   - Inspect `data/` (loaders/adapters/cache). Read `data/loader.py` and `data/cache.py` to understand how real Binance data is fetched.
   - Check existing real artifacts: `reports/pairs_real_market.json`, `reports/portfolio_real.json` for schema/provenance. Confirm `real_data_only` and no fabricated data.
   - If network is blocked in env, use cached data/reports and fix adapters to work offline where possible.

3. WIRE ONE PAIRS PATH END-TO-END (CORE)
   - Focus on `strategies/pairs_trading.py` (CointegrationPairsStrategy). Trace through `backtest/engine.py` to a runnable entrypoint.
   - Run a concrete example: `python examples/run_pairs.py` or `python examples/run_pairs_multi.py`. Capture full output/tracebacks.
   - Fix integration gaps (imports, class/function mismatches, args) until it runs against real data paths.

4. HARDEN STAT-ARB MATH (CORE)
   - Enforce causal rolling hedge ratio (positive, clipped, guarded), opposing legs preserved, Engle-Granger + enriched gates (fail-closed), z-score hysteresis.
   - Ensure enriched diagnostics/gates are respected. Never fabricate gates/values.
   - Add minimal glue only if required; fix in existing modules.

5. ADD REALISM & PRODUCE PROOF (REQUIRED)
   - Ensure transaction costs/slippage/capital constraints are applied in the backtest path.
   - Run the end-to-end backtest and produce concrete metrics (trades/fills, PnL, cumulative/period returns, Sharpe, max drawdown, costs).
   - Write a durable proof artifact: `reports/handoff_proof_<UTC_TIMESTAMP>.json` with: config, data provenance (real_data_only/fabricated_data/hosts/blocked_routes), gates summary, trades count, equity curve summary, key metrics, and file paths modified.
   - Re-run targeted tests. Fix failures blocking the core pairs path. Leave repo in a runnable state.

RULES:
- Prioritize unblocking execution over documentation. Write code to fix failures.
- Full test suite is large/slow - use targeted runs. Only expand to broader tests if they block the core path.
- Real data only. Never fabricate candles/IV/funding/basis. Follow existing provenance patterns.
- Stay laser-focused on pairs/trading spreads/cointegration per repo name.
- Commit nothing unless explicitly asked. Update THIS handoff only if you remove a NEW hard blocker not listed here.
- Success = modified code + working end-to-end pairs stat-arb backtest run + verifiable proof artifact with concrete metrics from real code paths.
```

---

## KNOWN STATE
- `README.md` present (reference only)
- Core dirs: `strategies/`, `backtest/`, `data/`, `utils/`, `tests/`, `scripts/`, `examples/`, `research_state/`, `reports/`
- Packaging: `pyproject.toml`, `requirements.txt`
- Heavy test suite exists; many campaign tests passing individually
- Pairs strategy has enriched cointegration gates (fail-closed). Loader has Binance host fallbacks. Rich real-market artifacts exist.

## BOTTLENECK REMOVAL PRIORITY
1. **Targeted tests/imports** - fix blockers in pairs/cointegration path first
2. **Data loading/schema/provenance** - adapt to actual files/network constraints
3. **Strategy/backtest integration** - wire end-to-end for CointegrationPairsStrategy
4. **Stat-arb core logic gaps** (cointegration/spread/signals/gates) - harden
5. **Costs/realism + proof artifact** - produce verifiable metrics

## IMMEDIATE ACTIONS FOR NEXT AGENT
- [ ] `pytest -v tests/test_cointegration_campaign31_mt.py tests/test_cointegration_diagnostics_schema.py tests/test_pairs_real_market.py -q` (targeted)
- [ ] `ls -la data/` and read `data/loader.py`, `data/cache.py`
- [ ] `python examples/run_pairs.py 2>&1 | tail -80` or `python examples/run_pairs_multi.py 2>&1 | tail -80`
- [ ] Trace `CointegrationPairsStrategy.generate_signals` -> `BacktestEngine.run` with real data
- [ ] Produce `reports/handoff_proof_*.json` with concrete metrics

## SUCCESS CRITERION
Next agent has executed heavy work: modified code to remove blockers, ran targeted tests/backtests iteratively, and produced a working end-to-end crypto pairs stat-arb backtest run with concrete, verifiable metrics + proof artifact from real code paths.
