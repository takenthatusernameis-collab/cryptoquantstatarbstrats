# HANDOFF (SINGLE DURABLE HANDOFF)

TIMESTAMP: 2026-11-04T17:27:51Z
REPO: cryptoquantstatarbstrats
FOCUS: Crypto Quantitative Statistical Arbitrage Strategies (Cointegration/Pairs First)

---

## INITIAL TASK MESSAGE (PASTE AS FIRST MESSAGE FOR NEXT AGENT)

```
You are picking up cryptoquantstatarbstrats. NO "investigate only" loops. DO HEAVY WORKING IMMEDIATELY.

REPO-NAME PRIORITY (non-negotiable): cryptoquantstatarbstrats = Crypto Quant Stat Arb
Strategies. Cointegration/pairs trading is the core edge. Everything else
(mean reversion, momentum, term structure, volatility surface) is secondary
and must not displace pairs work.

OBJECTIVE: Deliver a verifiably working, REAL-DATA-ONLY end-to-end crypto pairs
statistical arbitrage pipeline (pair selection -> cointegration/spread
construction -> z-score signals -> realistic backtest with costs) that produces
concrete, reproducible metrics from real code paths. Treat "cointegration is
the core edge" as non-negotiable. Real data only. Never fabricate candles/IV/
funding/basis. Follow existing provenance patterns (real_data_only,
fabricated_data, blocked_routes, computed_at, rationale).

EXECUTE IN THIS EXACT ORDER (remove bottlenecks first):

1. TARGETED HEALTH CHECK (FAST)
   - Verify deps: `python -c "import numpy,pandas,statsmodels,scipy,yaml; print('ok')"`
   - Run targeted pairs/cointegration tests first (NOT the full suite):
     `python -m pytest -v tests/test_cointegration_campaign31_mt.py
      tests/test_cointegration_diagnostics_schema.py tests/test_pairs_real_market.py
      tests/test_cointegration_threshold_invariance.py -q`
   - Capture any ImportError/ModuleNotFoundError and fix via pyproject.toml/
     requirements.txt. Expected baseline: 40 passed.

2. MAP REAL DATA & PROVENANCE (BLOCKER REMOVAL)
   - Inspect `data/` (loaders/adapters/cache). Read `data/loader.py` and
     `data/cache.py`. There is cached Binance data in `data/cache/`.
   - Confirm `real_data_only` provenance in `reports/pairs_real_market.json` and
     `reports/cointegration_diagnostics_real.json`; never fabricate data.
   - `examples/run_pairs.py` uses `DataLoader.load_binance_data()` with public
     endpoints. `api.binance.com` returns HTTP 451 here; the loader host chain
     tries `www.binance.com` first (public spot klines). If network is blocked,
     leverage cached data paths. Record hosts/blocked_routes honestly.

3. WIRE ONE PAIRS PATH END-TO-END (CORE - HEAVY WORK)
   - Focus on `strategies/pairs_trading.py` (CointegrationPairsStrategy).
     Trace through `backtest/engine.py` - engine converts signals to weights via
     `_signals_to_weights()` (explicit per-asset weights take precedence),
     applies costs/slippage, handles regime gating.
   - Run: `timeout 1800 python examples/run_pairs.py 2>&1 | tail -120` (BTC/ETH,
     walk-forward sweep 4 splits rolling; can take minutes; capture full
     output/tracebacks).
   - Fix integration gaps (imports, args, class/function mismatches) until it
     runs against real data paths. Do not mark done until the script completes
     and writes `reports/pairs_real_market.json`.

4. HARDEN STAT-ARB MATH (CORE)
   - Enforce causal rolling hedge ratio (positive, clipped, guarded): replace
     inf/nan, require > 1e-18, clip [1e-6, 1e6]. Opposing legs preserved via
     explicit per-asset weights.
   - Engle-Granger + enriched gates (fail-closed): causal-only usage
     (rolling/trailing). `use_enriched_gates=True`, `strict_enriched_gates=True`
     (fail-closed): any missing/None/false gate value blocks entries. Never
     fabricate gates/values.
   - Add minimal glue only if required; fix in existing modules.

5. ADD REALISM & PRODUCE PROOF (REQUIRED - HEAVY WORK)
   - Ensure transaction costs/slippage/capital constraints applied (engine
     applies fee_rate+slippage on turnover; examples pass fee_rate=0.001,
     slippage=0.0005).
   - Run end-to-end backtest producing concrete metrics (trades/fills, PnL,
     cumulative/period returns, Sharpe, max drawdown, calmar, costs). Extract
     from engine results/replay.
   - Write durable proof artifact: `reports/handoff_proof_<UTC_TIMESTAMP>.json`
     with: config, data provenance (real_data_only/fabricated_data/hosts/
     blocked_routes), gates summary, trades count, equity curve summary, key
     metrics, files modified, and reproduction command.
   - Re-run targeted tests. Fix failures blocking core pairs path. Leave repo in
     runnable state.

RULES:
- Prioritize unblocking execution over documentation. Write code to fix failures.
- Full test suite large/slow - use targeted runs. Only expand if blocking core
  pairs path.
- Real data only. Never fabricate candles/IV/funding/basis.
- Stay laser-focused on pairs/trading spreads/cointegration per repo name.
- Commit nothing unless explicitly asked. Update THIS handoff only if removing a
  NEW hard blocker not listed here.
- Success = modified code + working end-to-end pairs stat-arb backtest run +
  verifiable proof artifact with concrete metrics from real code paths.

FOCUS CAMPAIGN (future agents must do heavy work - no skipping):
- Every session must re-run the targeted pairs/cointegration tests (40 passed
  baseline) and confirm `examples/run_pairs.py` completes end-to-end against
  real data before declaring progress.
- Any new pair added must pass the full enriched cointegration gate set
  (eg_pass, johansen_pass, spread_mr_pass, hl_bounds_pass, leg_stationarity_ok,
  rolling_stable_ok, all_pass) with full provenance.
- A session is not complete until a fresh `reports/handoff_proof_*.json` exists
  with concrete metrics from a real-code-path run.
```

---

## KNOWN STATE
- Targeted cointegration/pairs tests pass (40 passed). Full suites exist and are large.
- `strategies/pairs_trading.py`: causal rolling hedge ratio with guards, opposing legs via explicit weights, enriched gates (fail-closed), cointegration testing with caching by interval.
- `backtest/engine.py`: supports explicit per-asset weights, costs/slippage, regime gating, walk-forward utilities exist.
- `data/loader.py`, `data/cache.py`: Binance loader with retries/fallbacks; disk cache present.
- `examples/run_pairs.py` does walk-forward sweep over BTC/ETH/SOL, produces `reports/pairs_real_market.json` (already exists with results showing mixed performance vs benchmark).
- `reports/` has extensive campaign artifacts (real market results exist).
- End-to-end `examples/run_pairs.py` confirmed runnable (completes without crash; statsmodels warnings only).

## BOTTLENECK REMOVAL PRIORITY
1. **Environment/deps** - ensure imports work (targeted tests pass now).
2. **Data loading** - leverage cache/offline capability if network issues (`api.binance.com` = HTTP 451; `www.binance.com` works).
3. **End-to-end execution** - actually run `examples/run_pairs.py` to completion and produce fresh proof; may need longer timeout or to debug if it hangs/fails.
4. **Stat-arb hardening** - verify causal behavior, gates enforced correctly.
5. **Proof artifact** - generate `reports/handoff_proof_YYYYMMDDTHHMMSSZ.json` with concrete metrics.

## IMMEDIATE ACTIONS FOR NEXT AGENT
- [ ] Verify deps: `python -c "import numpy,pandas,statsmodels,scipy,yaml; print('ok')"`
- [ ] Run targeted pairs tests: `python -m pytest -v tests/test_cointegration_campaign31_mt.py tests/test_cointegration_diagnostics_schema.py tests/test_pairs_real_market.py tests/test_cointegration_threshold_invariance.py -q`
- [ ] Run pairs example end-to-end: `timeout 1800 python examples/run_pairs.py 2>&1 | tail -120`
- [ ] If it fails, debug imports/integration; trace CointegrationPairsStrategy.generate_signals and BacktestEngine path
- [ ] Capture full metrics from run and write proof artifact with provenance
- [ ] Re-run targeted tests after any changes

## SUCCESS CRITERION
Next agent has executed heavy work: modified code to remove blockers, ran targeted tests/backtests iteratively, and produced a working end-to-end crypto pairs stat-arb backtest run with concrete, verifiable metrics + proof artifact from real code paths.
