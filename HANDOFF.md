# HANDOFF (SINGLE DURABLE) — 2026-11-05T03:45:29Z

REPO: cryptoquantstatarbstrats. PRIORITY: pairs/spreads/cointegration = core edge. NO fabrication. Fail-closed. No threshold weakening.

## INITIAL TASK (CLEAR, HEAVY WORK — DO NOT INVESTIGATE-ONLY)
IMMEDIATELY HEAVY WORK:
1) Harden `utils/cointegration.py::rolling_cointegration_stability` for causal trailing windows of length 60/120. You already made it assessable (producing >=2 windows with heavy overlap/step=1 fallback, min_windows>=2 when possible). Keep real p-values from `engle_granger_test`, DO NOT raise `frac_significant >= 0.6`. Ensure it never fabricates and returns honest `insufficient_data` only when truly impossible.
2) Ensure `strategies/pairs_trading.py` uses the causal per-bar enriched gates correctly with parity to cached path (fail-closed). Verify BTC/ETH trailing 120 bars produces assessable rolling stability and gates do not flip due to caching.
3) Rerun `examples/run_pairs_multi.py` and confirm gate breakdown written to `reports/`.
4) Run universe scan `examples/run_pair_universe_scan.py` again with fresh timestamp if needed; write/read results. If ANY pair passes ALL gates (eg/joh/spread MR/hl bounds/leg stationarity/rolling stable/no structural break) with real data only -> build walk-forward OOS backtest showing nonzero trades_count/total_return/sharpe/max_drawdown with fresh proof artifact. If NONE pass -> produce an honest blocked report with per-gate reasons (no fabrication, no threshold weakening).

## CURRENT STATE (AS OF 2026-11-05T03:45Z)
- `rolling_cointegration_stability` modified to shrink aggressively and try step=1 for >=2 windows on short samples (tested synthetic n=120 gives >=2 windows).
- Ran `examples/run_pairs_multi.py` (exit 0). Results: all three pairs (BTC/ETH, ETH/SOL, BTC/SOL) show trades_count=0 / total_return=0 on full replay with enriched gates enforced causally; benchmarks positive.
- Universe scan completed previously: `reports/pairs_candidate_scan_20261105T025358Z.json` has `n_pairs_scanned` from universe across 1h/4h/1d, `n_pass_all_gates=0`, no passing candidates.
- Latest gate breakdown exists (e.g. `reports/pairs_gate_breakdown_20261105T022858Z.json`).
- `reports/portfolio_real.json` shows fail-closed state across 17 pairs. Real data only.

## BOTTLENECKS (REMOVE THEM)
- Rolling stability assessability on 60/120 bar causal windows: FIXED in principle but verify on real BTC/ETH trailing 120-bar slices and ensure strategy sees assessable windows.
- Leg stationarity is correctly fail-closed on real non-stationary legs (legitimate). Do not weaken.
- Structural breaks remain correctly blocking when flagged (legitimate). Do not weaken.
- Per-bar parity between cached/uncached enriched gates must hold.

## NEXT FOCUS CAMPAIGN (HEAVY WORK, NO COASTING)
1. VERIFY real causal windows: write a quick test script using real cached data from `data/` or load via same paths as examples to confirm `target_schema_diagnostics` gives assessable rolling stability on BTC/ETH trailing ~120 bars. If still unassessable, adjust `rolling_cointegration_stability` further (smaller min window, ensure >=2 windows) without changing thresholds.
2. IF assessable and some gate flips -> trace which gate blocks; fix ONLY if it's an assessability bug. Never touch thresholds (eg<0.05, hl 1<hl<500, rolling>=0.6, legs ADF<=0.05).
3. SCAN/CONFIRM: run `examples/run_pair_universe_scan.py` to produce fresh `reports/pairs_candidate_scan_$(date -u +%Y%m%dT%H%M%SZ).json`.
4. OUTCOME PATH:
   - If any pass all gates: generate walk-forward OOS backtest for that pair with real data, show trades_count/total_return/sharpe/max_drawdown, write fresh proof artifact under `reports/` (honest numbers, no fabrication).
   - If none pass: write honest blocked summary in `reports/` citing per-gate failures from results, no fabrication.
5. TESTS: `pytest tests/test_cointegration_campaign31_mt tests/test_cointegration_diagnostics_schema tests/test_pairs_real_market -v`. Lint/typecheck touched files: `ruff check utils/cointegration.py strategies/pairs_trading.py && mypy utils/cointegration.py strategies/pairs_trading.py`.

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
