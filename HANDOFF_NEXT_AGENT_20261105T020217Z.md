# HANDOFF (SINGLE DURABLE) — 2026-11-05T02:03:17Z

REPO: cryptoquantstatarbstrats. PRIORITY: pairs/spreads/cointegration = core edge.

## STATUS (HONEST)
- `examples/run_pairs_multi.py` exits 0 with `trades_count=0` on real Binance 1h 2026-04-01→2026-10-28 (BTC/ETH, ETH/SOL, BTC/SOL).
- Gate breakdown: `reports/pairs_gate_breakdown_20261105T010211Z.json`. All three pairs fail `all_pass`.
- Primary blockers: `rolling_stable_ok` critically low (frac_significant 0.066–0.176), `eg_pass` false (p 0.518–0.731), `spread_mr_pass`/`leg_stationarity_ok` often false. ETH/SOL also flags `no_structural_break` false.
- `reports/portfolio_real.json` shows the same across all 17 pairs: nothing passes all enriched gates on real data. No fabrication. Fail-closed is working as intended.

## BOTTLENECKS TO REMOVE (HEAVY WORK)
1. **Rolling stability assessability** (biggest blocker). `utils/cointegration.py::rolling_cointegration_stability` needs to reliably produce >=2 windows on short causal samples (trailing 60/120) without inflating the stability threshold. Currently it downgrades to `insufficient_data` → strategy fails closed. Fix: shrink window/step aggressively for small n, allow heavier overlap, set `min_windows>=2` when `>=3` impossible, still require real p-values from `engle_granger_test`. Do NOT raise `frac_significant >= 0.6`.
2. **Leg stationarity correctness** (now correctly fail-closed). With the fix, legs are often non-stationary on real series. This is legitimate. Don't weaken to "ADF computed".
3. **Structural breaks on short samples**. `structural_break_check` should be assessable without fabricating; if truly unassessable on a very short trailing window, strategy must stay fail-closed (current behavior correct). Only fix assessability, not the 25% heuristic.
4. **Per-bar parity**. Ensure `CointegrationPairsStrategy` (strategies/pairs_trading.py) causal per-bar path and cached path never disagree. The gate breakdown must always be written honestly.

## NEXT FOCUS CAMPAIGN (NO INVESTIGATION-ONLY, HEAVY WORK)
Execute in this order:

### 1) FIX ROLLING STABILITY FOR CAUSAL WINDOWS (IMMEDIATE)
- Edit `utils/cointegration.py`:
  - In `rolling_cointegration_stability`: when `n < win*3`, try `win = max(30, win//2)` down to `min(60, max(30, n//6))` with `step = max(1, win//6)`. Allow `min_windows = 2` if possible. Still return honest `insufficient_data` only if < 2 windows possible with smallest safe window.
  - Keep `frac_significant >= 0.6` and never coerce to True.
- Edit `strategies/pairs_trading.py`: ensure trailing samples (lookback 60/120) can actually produce assessable rolling stability; don't pass full-history aggregates as per-bar gates.
- Verify with a quick manual check on BTC/ETH trailing 120 bars (target_schema_diagnostics).

### 2) SCAN ENTIRE UNIVERSE ACROSS TIMEFRAMES (FIND ANY PASSING WINDOW)
- Use cached Binance spot data (www.binance.com preferred). Do NOT call api.binance.com.
- Scan ALL symbols in `reports/portfolio_real.json` pairs + any cached in `data/` across `1h`, `4h`, `1d`.
- For each candidate pair/timeframe run `target_schema_diagnostics` (real data only). Write `reports/pairs_candidate_scan_$(date -u +%Y%m%dT%H%M%SZ).json` with: pair, timeframe, all_pass, gates, blocked_routes, frac_significant, eg_pvalue, leg ADF pvalues, hl, structural_breaks.flagged, provenance.
- Be exhaustive. Don't stop at first fail.

### 3) IF ANY PAIR PASSES ALL GATES → TRADE IT
- If found with `all_pass: true` and real provenance: run walk-forward backtest on that pair/timeframe producing nonzero `trades_count`, `total_return`, `sharpe_ratio`, `max_drawdown`. Update with fresh proof.
- If multiple pass, pick highest quality (all gates clean, good rolling stability) and still document others.

### 4) IF NONE PASS → HONEST BLOCKED, NO FABRICATION
- Write `reports/pairs_universe_scan_blocked_$(date -u +%Y%m%dT%H%M%SZ).json` with per-pair/per-timeframe gate heatmap + blocked_routes + rationale.
- Do NOT weaken thresholds. Do NOT fabricate candles/IV/funding.
- Stop. Document exactly what's blocking.

### 5) VERIFY & TEST
- Re-run: `pytest tests/test_cointegration_campaign31_mt tests/test_cointegration_diagnostics_schema tests/test_pairs_real_market -v`
- Re-run: `python examples/run_pairs_multi.py` and capture `reports/pairs_gate_breakdown_$(date -u +%Y%m%dT%H%M%SZ).json`
- Ensure `mypy`/`ruff` still pass on touched files.

## RULES (NON-NEGOTIABLE)
- Real data only. Never fabricate.
- Fail-closed always. Missing/unassessable gate = block (or honest insufficient_data).
- No threshold weakening (eg<0.05, hl 1<hl<500, rolling>=0.6, legs ADF<=0.05).
- Causal only (trailing). No full-history aggregates as per-bar gates.
- Commit nothing unless explicitly asked.
- Heavy working immediately. No investigation-only loops.

## FILES TO FOCUS ON
- `utils/cointegration.py` (rolling_cointegration_stability, structural_break_check, target_schema_diagnostics)
- `strategies/pairs_trading.py` (enriched gates, per-bar caching, breakdown)
- `examples/run_pairs_multi.py`, `reports/*` for provenance
