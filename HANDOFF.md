# HANDOFF (SINGLE DURABLE) — 2026-11-05T03:47:25Z

REPO: cryptoquantstatarbstrats. CORE EDGE: pairs/spreads/cointegration = priority #1. NO fabrication. Fail-closed. No threshold weakening. Causal trailing only.

## INITIAL TASK (CLEAR, HEAVY WORK — DO NOT INVESTIGATE-ONLY)
IMMEDIATELY DO HEAVY WORK IN THIS ORDER:

1) **ROLLING STABILITY ASSESSABILITY (HIGHEST BOTTLENECK)**
   - Verify `utils/cointegration.py::rolling_cointegration_stability` on REAL BTC/ETH 1h trailing slices (n>=120). It MUST produce >= 2 windows when data exists.
   - If frac_significant == 0.0 or it reports insufficient_data on fixable real windows, adjust ONLY windowing (smaller min_window, step=1 fallback, ensure >=2 windows). DO NOT change thresholds (need frac_significant >= 0.6).
   - Confirm the strategy sees assessable rolling windows via the causal per-bar path.

2) **CAUSAL PARITY + GATE TRACE**
   - Ensure `strategies/pairs_trading.py` uses enriched gates causally with parity between cached/uncached paths (fail-closed under strict mode).
   - Trace why gates block on real data (leg_stationarity, structural_break, spread_mr, eg/johansen). Only fix assessability bugs. Never weaken ADF, structural break, or other gate tests.

3) **FRESH UNIVERSE SCAN + WALK-FORWARD IF ANY PASS**
   - Run `examples/run_pair_universe_scan.py` to write a FRESH timestamped `reports/pairs_candidate_scan_$(date -u +%Y%m%dT%H%M%SZ).json`.
   - IF any pair passes ALL gates on real data: build a walk-forward OOS backtest for that pair(s) showing nonzero trades_count/total_return/sharpe/max_drawdown with a fresh proof artifact under `reports/` (honest numbers, no fabrication).
   - IF none pass: write an honest blocked summary under `reports/` citing per-gate failures from the fresh scan (counts by gate across TFs), no fabrication, no threshold weakening.

4) **VALIDATE + LINT**
   - Run tests: `pytest tests/test_cointegration_campaign31_mt tests/test_cointegration_diagnostics_schema tests/test_pairs_real_market -v`
   - Lint/typecheck touched files: `ruff check utils/cointegration.py strategies/pairs_trading.py && mypy utils/cointegration.py strategies/pairs_trading.py`

## CURRENT STATE (AS OF 2026-11-05T03:47Z)
- Last scan (20261105T025358Z): n_pairs_scanned=165 across 1h/4h/1d, n_pass_all_gates=0. All pairs blocked.
- Rolling stability frac_significant often 0.0-0.11 with small n_windows; leg_stationarity and structural_break are common blockers on real data.
- `examples/run_pairs_multi.py` ran with enriched gates enforced causally -> trades_count=0/total_return=0 for BTC/ETH, ETH/SOL, BTC/SOL.
- Gate breakdowns and portfolio_real.json confirm fail-closed behavior.

## BOTTLENECKS (REMOVE THEM)
- **Assessability**: rolling_cointegration_stability must return >=2 windows on real trailing 60/120-bar slices when possible (fix windowing only).
- **Parity**: cached vs uncached enriched gates must not diverge causally.
- **False "insufficient_data"**: only when truly impossible with real data; prefer shrinking windows/step=1 over fabricating.

## NEXT FOCUS CAMPAIGN (HEAVY WORK, NO COASTING)
1. Write/quick-run a diagnostic using real cached data from `data/` (or same loader as examples) to confirm assessable rolling stability on BTC/ETH trailing ~120 bars. If unassessable -> fix windowing in `utils/cointegration.py`.
2. If assessable but gates still block -> trace per-gate with evidence from fresh scan; fix ONLY assessability bugs. Never touch gate thresholds.
3. Fresh scan -> if passes exist do walk-forward OOS with proof; else honest blocked report.
4. Run tests/lint/typecheck and leave concrete artifacts in `reports/`.

## FILES TO FOCUS ON
- `utils/cointegration.py`
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
