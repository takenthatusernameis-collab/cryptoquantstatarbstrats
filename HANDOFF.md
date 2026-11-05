# HANDOFF (SINGLE DURABLE) — 2026-11-05T04:46:55Z

REPO: cryptoquantstatarbstrats. CORE EDGE: pairs/spreads/cointegration = priority #1. NO fabrication. Fail-closed. No threshold weakening. Causal trailing only.

## INITIAL TASK (CLEAR, HEAVY WORK — DO NOT INVESTIGATE-ONLY)

IMMEDIATELY DO HEAVY WORK IN THIS ORDER:

1) **ROLLING STABILITY ASSESSABILITY (HIGHEST BOTTLENECK)**
   - Verify `utils/cointegration.py::rolling_cointegration_stability` on REAL BTC/ETH 1h trailing slices (lookback 60 and 120, n>=120). It MUST produce >= 2 windows when data exists.
   - FIXED: Made `rolling_cointegration_stability` more aggressive for short samples (window shrinking to >=6, step=1 fallback, ensure >=2 windows). Now produces >=2 windows on real trailing slices.
   - Confirm the strategy sees assessable rolling windows via the causal per-bar path in `strategies/pairs_trading.py`.
   - Note: with current real data regime, rolling_stable_ok is often False (frac_significant < 0.6) — this is a genuine statistical outcome on these windows, not assessability failure.

2) **CAUSAL PARITY + GATE TRACE**
   - Ensure `strategies/pairs_trading.py` uses enriched gates causally with parity between cached/uncached paths (fail-closed under strict mode).
   - Trace why gates block on real data (leg_stationarity, structural_break, spread_mr, eg/johansen, rolling_stable). Only fix assessability bugs. Never weaken ADF, structural break, or other gate tests.

3) **FRESH UNIVERSE SCAN + WALK-FORWARD IF ANY PASS**
   - Run `examples/run_pair_universe_scan.py` to write a FRESH timestamped `reports/pairs_candidate_scan_$(date -u +%Y%m%dT%H%M%SZ).json`.
   - IF any pair passes ALL gates on real data: build a walk-forward OOS backtest for that pair(s) showing nonzero trades_count/total_return/sharpe/max_drawdown with a fresh proof artifact under `reports/` (honest numbers, no fabrication).
   - IF none pass: write an honest blocked summary under `reports/` citing per-gate failures from the fresh scan (counts by gate across TFs), no fabrication, no threshold weakening.

4) **VALIDATE + LINT**
   - Run tests: `pytest tests/test_cointegration_campaign31_mt tests/test_cointegration_diagnostics_schema tests/test_pairs_real_market -v`
   - Lint/typecheck touched files: `ruff check utils/cointegration.py strategies/pairs_trading.py && mypy utils/cointegration.py strategies/pairs_trading.py`

## CURRENT STATE (AS OF 2026-11-05T04:46:55Z)
- Scans T025358Z/T030941Z: n_pairs_scanned=165 across 1h/4h/1d, n_pass_all_gates=0. All pairs blocked.
- Fixed assessability: rolling_cointegration_stability now produces >=2 windows on short trailing slices (60/120) with heavy overlap/step=1 fallback.
- On real data, leg_stationarity_ok is often False (both legs must have ADF p <= 0.05) — this is a genuine statistical blocker on current crypto price series, not assessability.
- strategies/pairs_trading.py enriched gates run causally per-bar with interval caching; fail-closed parity maintained.
- `examples/run_pairs_multi.py` with enriched gates -> positions remain zero due to strict gate blocking (honest, no weakening).

## BOTTLENECKS (REMOVE THEM)
- **Assessability**: FIXED for rolling stability on short samples. Monitor for any remaining insufficient_data cases.
- **Parity**: cached vs uncached enriched gates must not diverge causally.
- **False "insufficient_data"**: only when truly impossible with real data; prefer shrinking windows/step=1 over fabricating.
- **Leg stationarity**: requires both legs ADF p <= 0.05; on real crypto price legs this is often genuinely non-stationary — do not weaken, only confirm computed honestly.

## NEXT FOCUS CAMPAIGN (HEAVY WORK, NO COASTING)
1. Verify assessability fix is working as expected (done). Confirm rolling stability produces >=2 windows on real slices.
2. Run fresh universe scan immediately to get updated per-gate breakdowns.
3. If passes exist do walk-forward OOS with proof; else write honest blocked summary with counts by gate.
4. Run tests/lint/typecheck and leave concrete artifacts in `reports/`.

## FILES TO FOCUS ON
- `utils/cointegration.py` (done - assessability fixed)
- `strategies/pairs_trading.py`
- `examples/run_pairs_multi.py`
- `examples/run_pair_universe_scan.py`
- `reports/*`

## VERIFICATION COMMANDS
```bash
python -m pytest tests/test_cointegration_campaign31_mt.py tests/test_cointegration_diagnostics_schema.py tests/test_pairs_real_market.py -v
python -m ruff check utils/cointegration.py strategies/pairs_trading.py
python -m mypy utils/cointegration.py strategies/pairs_trading.py
timeout 1800 python examples/run_pairs_multi.py
python examples/run_pair_universe_scan.py
```

## RULES (NON-NEGOTIABLE)
- Real data only. Never fabricate.
- Fail-closed always.
- No threshold weakening.
- Causal only (trailing). No full-history aggregates as per-bar gates.
- Commit nothing unless explicitly asked.
- Heavy working immediately. No investigation-only loops.
