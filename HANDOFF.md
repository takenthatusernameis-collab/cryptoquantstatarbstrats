# HANDOFF (SINGLE DURABLE) — 2026-11-05T02:55:37Z

REPO: cryptoquantstatarbstrats. PRIORITY: pairs/spreads/cointegration = core edge.

## INITIAL TASK (CLEAR, HEAVY WORK — DO NOT INVESTIGATE-ONLY)
Start immediately: edit `utils/cointegration.py::rolling_cointegration_stability` to produce >=2 windows on trailing 60/120-bar causal samples (shrink window/step, heavier overlap, min_windows>=2 when >=3 impossible) while keeping real p-values from `engle_granger_test` and NOT raising `frac_significant >= 0.6`; then mirror the causal per-bar path in `strategies/pairs_trading.py`; verify on BTC/ETH trailing 120 bars; rerun `examples/run_pairs_multi.py` and confirm gate breakdown written to `reports/`. Heavy working immediately.

## STATUS (HONEST, AS OF 2026-11-05T02:54Z)
- `examples/run_pairs_multi.py` exits 0 with `trades_count=0` on real Binance 1h 2026-04-01→2026-10-28 (BTC/ETH, ETH/SOL, BTC/SOL). Re-run: `timeout 1800 python examples/run_pairs_multi.py` (~2 min).
- Latest gate breakdown: `reports/pairs_gate_breakdown_20261105T022858Z.json`. All three pairs fail `all_pass`.
- Universe scan `examples/run_pair_universe_scan.py` completed: 165 pairs × 3 timeframes (1h/4h/1d), **0 pass all gates**. Latest report `reports/pairs_candidate_scan_20261105T025358Z.json`.
- Top rolling-stability candidates (none pass other gates): 1h AVAX/SOL frac_sig=0.522; 4h AVAX/LTC frac_sig=0.462 (eg=True, spread=True, joh=True, hl=True, sb=True — only leg_stationarity=False); 1d AVAX/BTC frac_sig=0.500.
- `reports/portfolio_real.json`: nothing passes all enriched gates on real data across 17 pairs. Fail-closed working as intended. No fabrication.

## BOTTLENECKS TO REMOVE (HEAVY WORK)
1. Rolling stability assessability (biggest). `utils/cointegration_stability::rolling_cointegration_stability` must produce >=2 windows on short causal samples (trailing 60/120) without inflating threshold. Currently downgrades to `insufficient_data` → fail-closed. Shrink window/step for small n, allow heavier overlap, `min_windows>=2` when >=3 impossible, still require real p-values from `engle_granger_test`. Do NOT raise `frac_significant >= 0.6`.
2. Leg stationarity correctness (fail-closed). Legs often non-stationary on real series. Legitimate. Don't weaken to "ADF computed".
3. Structural breaks on short samples. Assessable without fabrication; if truly unassessable on very short trailing window, stay fail-closed. Fix assessability only, not the 25% heuristic.
4. Per-bar parity. `CointegrationPairsStrategy` causal per-bar path and cached path must never disagree. Gate breakdown always written honestly.

## NEXT FOCUS CAMPAIGN (NO INVESTIGATION-ONLY, HEAVY WORK)
1. FIX ROLLING STABILITY FOR CAUSAL WINDOWS: edit `utils/cointegration.py` + `strategies/pairs_trading.py`; verify on BTC/ETH trailing 120 bars.
2. SCAN ENTIRE UNIVERSE ACROSS TIMEFRAMES (1h/4h/1d) using cached Binance spot data (www.binance.com preferred; never api.binance.com). Write `reports/pairs_candidate_scan_$(date -u +%Y%m%dT%H%M%SZ).json`. Script exists: `examples/run_pair_universe_scan.py`.
3. IF ANY PAIR PASSES ALL GATES → trade it; walk-forward backtest with nonzero trades_count/total_return/sharpe/max_drawdown; fresh proof.
4. IF NONE PASS → honest blocked report; no fabrication; no threshold weakening.
5. VERIFY & TEST: pytest tests/test_cointegration_campaign31_mt tests/test_cointegration_diagnostics_schema tests/test_pairs_real_market -v; rerun examples/run_pairs_multi.py; ruff/mypy on touched files.

## RULES (NON-NEGOTIABLE)
- Real data only. Never fabricate.
- Fail-closed always.
- No threshold weakening (eg<0.05, hl 1<hl<500, rolling>=0.6, legs ADF<=0.05).
- Causal only (trailing). No full-history aggregates as per-bar gates.
- Commit nothing unless explicitly asked.
- Heavy working immediately. No investigation-only loops.

## FILES TO FOCUS ON
- `utils/cointegration.py`
- `strategies/pairs_trading.py`
- `examples/run_pairs_multi.py`, `examples/run_pair_universe_scan.py`, `reports/*`

## VERIFICATION COMMANDS
```bash
python -m pytest tests/test_cointegration_campaign31_mt.py tests/test_cointegration_diagnostics_schema.py tests/test_pairs_real_market.py tests/test_cointegration_threshold_invariance.py -v
python -m ruff check utils/cointegration.py strategies/pairs_trading.py
python -m mypy utils/cointegration.py strategies/pairs_trading.py
timeout 1800 python examples/run_pairs_multi.py
python examples/run_pair_universe_scan.py
```