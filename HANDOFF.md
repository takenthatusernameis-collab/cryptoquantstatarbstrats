# HANDOFF (SINGLE DURABLE HANDOFF)

TIMESTAMP: 2026-11-04T16:58:05Z
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
     `python -m pytest -v tests/test_cointegration_campaign31_mt.py tests/test_cointegration_diagnostics_schema.py tests/test_pairs_real_market.py tests/test_cointegration_threshold_invariance.py -q`
   - Targeted tests passed (40 passed) in current state - still verify environment deps (numpy/pandas/statsmodels/scipy/yaml) are present. Capture ImportError/ModuleNotFoundError and fix via pyproject.toml/requirements.txt.

2. MAP REAL DATA & PROVENANCE (BLOCKER)
   - Inspect `data/` (loaders/adapters/cache). Read `data/loader.py` and `data/cache.py`. There is cached Binance data in `data/cache/` (34 files).
   - Check existing real artifacts: `reports/pairs_real_market.json` exists with concrete results (BTC/ETH underperformed benchmark, ETH/SOL underperformed, BTC/SOL showed positive OOS/replay but below benchmark). Confirm `real_data_only` provenance in artifacts; never fabricate data.
   - `examples/run_pairs.py` uses `DataLoader.load_binance_data()` with public endpoints. If network blocked, leverage cached data paths.

3. WIRE ONE PAIRS PATH END-TO-END (CORE)
   - Focus on `strategies/pairs_trading.py` (CointegrationPairsStrategy). Trace through `backtest/engine.py` - engine correctly converts signals to weights via `_signals_to_weights()` (explicit per-asset weights take precedence), applies costs/slippage, handles regime gating.
   - Try to run: `timeout 900 python examples/run_pairs.py` (or similar). It does walk-forward sweep (4 splits, rolling) which can take time; capture full output/tracebacks.
   - Fix integration gaps (imports, args, class/function mismatches) until it runs against real data paths.

4. HARDEN STAT-ARB MATH (CORE)
   - Enforce causal rolling hedge ratio (positive, clipped, guarded) - already implemented with guards (replace inf/nan, require > 1e-18, clip 1e-6..1e6). Opposing legs preserved via explicit per-asset weights in signals - correct.
   - Engle-Granger + enriched gates (fail-closed) - strategy supports enriched diagnostics and has strict gates; ensure causal-only usage (rolling/trailing). Never fabricate gates/values.
   - Add minimal glue only if required; fix in existing modules.

5. ADD REALISM & PRODUCE PROOF (REQUIRED)
   - Ensure transaction costs/slippage/capital constraints applied (engine applies fee_rate+slippage on turnover; examples pass fee_rate=0.001, slippage=0.0005). OK.
   - Run end-to-end backtest producing concrete metrics (trades/fills, PnL, cumulative/period returns, Sharpe, max drawdown, costs). Extract from engine results/replay.
   - Write durable proof artifact: `reports/handoff_proof_<UTC_TIMESTAMP>.json` with: config, data provenance (real_data_only/fabricated_data/hosts/blocked_routes), gates summary, trades count, equity curve summary, key metrics, files modified, and reproduction command.
   - Re-run targeted tests. Fix failures blocking core pairs path. Leave repo in runnable state.

RULES:
- Prioritize unblocking execution over documentation. Write code to fix failures.
- Full test suite large/slow - use targeted runs. Only expand if blocking core path.
- Real data only. Never fabricate candles/IV/funding/basis. Follow existing provenance patterns.
- Stay laser-focused on pairs/trading spreads/cointegration per repo name.
- Commit nothing unless explicitly asked. Update THIS handoff only if removing NEW hard blocker not listed here.
- Success = modified code + working end-to-end pairs stat-arb backtest run + verifiable proof artifact with concrete metrics from real code paths.
```

---

## KNOWN STATE
- Targeted cointegration/pairs tests pass (40 passed). Full suites exist and are large.
- `strategies/pairs_trading.py`: causal rolling hedge ratio with guards, opposing legs via explicit weights, enriched gates (fail-closed), cointegration testing with caching by interval.
- `backtest/engine.py`: supports explicit per-asset weights, costs/slippage, regime gating, walk-forward utilities exist.
- `data/loader.py`, `data/cache.py`: Binance loader with retries/fallbacks; disk cache present.
- `examples/run_pairs.py` does walk-forward sweep over BTC/ETH/SOL, produces `reports/pairs_real_market.json` (already exists with results showing mixed performance vs benchmark).
- `reports/` has extensive campaign artifacts (real market results exist).

## BOTTLENECK REMOVAL PRIORITY
1. **Environment/deps** - ensure imports work (targeted tests pass now).
2. **Data loading** - leverage cache/offline capability if network issues.
3. **End-to-end execution** - actually run `examples/run_pairs.py` to completion and produce fresh proof; may need longer timeout or to debug if it hangs/fails.
4. **Stat-arb hardening** - verify causal behavior, gates enforced correctly.
5. **Proof artifact** - generate `reports/handoff_proof_YYYYMMDDTHHMMSSZ.json` with concrete metrics.

## IMMEDIATE ACTIONS FOR NEXT AGENT
- [ ] Verify deps: `python -c "import numpy,pandas,statsmodels,scipy,yaml; print('ok')"`
- [ ] Try running pairs example with sufficient timeout: `timeout 1800 python examples/run_pairs.py 2>&1 | tail -120`
- [ ] If it fails, debug imports/integration; trace CointegrationPairsStrategy.generate_signals and BacktestEngine path
- [ ] Capture full metrics from run (or from existing artifacts) and write proof artifact with provenance
- [ ] Re-run targeted tests after any changes

## SUCCESS CRITERION
Next agent has executed heavy work: modified code to remove blockers, ran targeted tests/backtests iteratively, and produced a working end-to-end crypto pairs stat-arb backtest run with concrete, verifiable metrics + proof artifact from real code paths.
