# HANDOFF (SINGLE DURABLE) — 2026-11-05T04:57:01Z
REPO: cryptoquantstatarbstrats. CORE EDGE: pairs/spreads/cointegration = priority #1 (repo name mandate). NO fabrication. Fail-closed. No threshold weakening. Causal trailing only.

## INITIAL TASK (CLEAR, HEAVY WORK — DO NOT INVESTIGATE-ONLY)

IMMEDIATELY DO HEAVY WORK IN THIS ORDER:

1) **FRESH UNIVERSE SCAN + PER-GATE BREAKDOWN (HIGHEST PRIORITY, UNBLOCKED)**
   - Run `python examples/run_pair_universe_scan.py` to write a FRESH timestamped `reports/pairs_candidate_scan_$(date -u +%Y%m%dT%H%M%SZ).json`.
   - This produces counts by gate across 1h/4h/1d (eg_pass, johansen_pass, spread_mr_pass, hl_bounds_pass, leg_stationarity_ok, rolling_stable_ok, no_structural_break, all_pass) for all 55 pairs × 3 TFs = 165 scans.
   - Output must be real Binance spot data only; no fabrication; no threshold weakening.

2) **HONEST BLOCKED SUMMARY (IF NO PAIR PASSES — EXPECTED OUTCOME)**
   - IF any pair passes ALL gates on real data: build a walk-forward OOS backtest for that pair(s) showing nonzero trades_count/total_return/sharpe/max_drawdown with a fresh proof artifact under `reports/` (honest numbers, no fabrication).
   - IF none pass: write an honest blocked summary under `reports/pairs_blocked_summary_$(date -u +%Y%m%dT%H%M%SZ).json` citing per-gate failures from the fresh scan (counts by gate across TFs), no fabrication, no threshold weakening. Do not coerce any gate to True.

3) **CAUSAL PARITY + GATE TRACE (VERIFY, NO WEAKENING)**
   - Confirm `strategies/pairs_trading.py` uses enriched gates causally with parity between cached/uncached paths (fail-closed under strict mode).
   - Confirm gates block honestly on real data (leg_stationarity, structural_break, spread_mr, eg/johansen, rolling_stable). Only fix assessability bugs. Never weaken ADF, structural break, or other gate tests.

4) **VALIDATE + LINT**
   - Run tests: `python -m pytest tests/test_cointegration_campaign31_mt.py tests/test_cointegration_diagnostics_schema.py tests/test_pairs_real_market.py -v`
   - Lint/typecheck touched files: `python -m ruff check utils/cointegration.py strategies/pairs_trading.py && python -m mypy utils/cointegration.py strategies/pairs_trading.py`

## CURRENT STATE (AS OF 2026-11-05T04:57:01Z)
- Branch `main` is clean, up to date with origin/main, working tree clean.
- Tests pass: `tests/test_cointegration_campaign31_mt.py`, `tests/test_cointegration_diagnostics_schema.py`, `tests/test_pairs_real_market.py` → 35 passed.
- `ruff check` and `mypy` on `utils/cointegration.py` + `strategies/pairs_trading.py` → clean.
- Scans T025358Z/T030941Z: n_pairs_scanned=165 across 1h/4h/1d, n_pass_all_gates=0. All pairs blocked. STALE — need fresh scan.
- FIXED: `rolling_cointegration_stability` now produces >=2 windows on short trailing slices (60/120) with heavy overlap/step=1 fallback. Assessability bottleneck removed.
- On real data, `leg_stationarity_ok` is often False (both legs must have ADF p <= 0.05) — this is a genuine statistical blocker on current crypto price series, NOT assessability failure. Do not weaken.
- `strategies/pairs_trading.py` enriched gates run causally per-bar with interval caching; fail-closed parity maintained.
- `examples/run_pairs_multi.py` with enriched gates → positions remain zero due to strict gate blocking (honest, no weakening).

## BOTTLENECKS (REMOVED / REMAINING)
- **Assessability (rolling stability)**: REMOVED. `rolling_cointegration_stability` produces >=2 windows on short samples (60/120). Monitor for any remaining `insufficient_data` cases.
- **Parity (cached vs uncached)**: Verified on main; per-bar interval caching matches cached path under strict fail-closed. No divergence.
- **False "insufficient_data"**: Removed via window shrinking + step=1 fallback; only truly impossible cases remain unassessable.
- **Leg stationarity (REMAINING, CANNOT BE WEAKENED)**: Requires both legs ADF p <= 0.05; on real crypto price legs this is genuinely non-stationary. This is the primary blocker keeping n_pass_all_gates=0. Path forward: confirm honestly via fresh scan, document per-gate counts, do NOT weaken. Do not spend sessions investigating ways around it — that is prohibited.

## NEXT FOCUS CAMPAIGN (HEAVY WORK, NO COASTING — MANDATORY)
1. Run fresh universe scan immediately (`python examples/run_pair_universe_scan.py`) → fresh timestamped JSON in `reports/`.
2. If any pair passes all gates → walk-forward OOS backtest with proof artifact under `reports/`.
3. If none pass → write honest blocked summary (`reports/pairs_blocked_summary_<UTC>.json`) with per-gate failure counts across TFs.
4. Verify causal parity + gate trace (no weakening).
5. Run tests + ruff + mypy; leave concrete artifacts in `reports/`.
Every session must end with at least one new concrete artifact in `reports/`. Investigation-only loops without an artifact are prohibited.

## FILES TO FOCUS ON
- `examples/run_pair_universe_scan.py` (run it — produces the scan artifact)
- `utils/cointegration.py` (assessability fixed; do not touch gate logic)
- `strategies/pairs_trading.py` (causal parity, fail-closed — verify only)
- `reports/*` (scan output + blocked summary artifacts)

## VERIFICATION COMMANDS
```bash
python examples/run_pair_universe_scan.py
python -m pytest tests/test_cointegration_campaign31_mt.py tests/test_cointegration_diagnostics_schema.py tests/test_pairs_real_market.py -v
python -m ruff check utils/cointegration.py strategies/pairs_trading.py
python -m mypy utils/cointegration.py strategies/pairs_trading.py
```

## REPO SNAPSHOT (2026-11-05T04:57:01Z)
- Branch: main, clean, up to date with origin/main.
- Top-level: backtest/, data/, examples/, reports/, research_state/, scripts/, strategies/, tests/, utils/.
- Key files: utils/cointegration.py, strategies/pairs_trading.py, examples/run_pair_universe_scan.py.
- Tests: 35 passed (cointegration campaign31 MT, diagnostics schema, pairs real market).
- Lint/typecheck: ruff + mypy clean on utils/cointegration.py + strategies/pairs_trading.py.
- Last non-checkpoint commits: 3c5e1a7 chore: capture completed workflow run diagnostics; 20a205c chore(handoff): finalize cointegration parity campaign.

## RULES (NON-NEGOTIABLE)
- Real data only. Never fabricate.
- Fail-closed always.
- No threshold weakening.
- Causal only (trailing). No full-history aggregates as per-bar gates.
- Commit nothing unless explicitly asked.
- Heavy working immediately. No investigation-only loops. Every session must leave a concrete artifact in `reports/`.
