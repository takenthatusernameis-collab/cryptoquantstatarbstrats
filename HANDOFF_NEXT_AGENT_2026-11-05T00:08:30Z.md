# HANDOFF (SINGLE DURABLE) — 2026-11-05T00:08:30Z

REPO: cryptoquantstatarbstrats (Crypto Quant Stat Arb Strategies)
PRIORITY: pairs / spreads / cointegration IS THE CORE EDGE. Everything else is secondary.
MODE: NO "investigate only". DO HEAVY WORKING IMMEDIATELY. Real data only. Never fabricate candles/IV/funding/basis. Fail-closed when unassessable. No threshold weakening to hide genuine failures. Calibration = make gates assessable/genuine, not coerce to pass.

## CURRENT CONFIRMED STATE
- Deps: OK (`numpy,pandas,statsmodels,scipy,yaml`).
- Targeted tests (baseline): `tests/test_cointegration_campaign31_mt.py tests/test_cointegration_diagnostics_schema.py tests/test_pairs_real_market.py tests/test_cointegration_threshold_invariance.py` -> 40 passed (verified 2026-11-05T00:04:45Z).
- `examples/run_pairs.py` COMPLETES end-to-end (exit 0) on cached Binance 1h 2026-04-01->2026-10-28 (BTC/ETH/SOL). Writes `reports/pairs_real_market.json` but `trades_count=0`, `total_return=0`, `sharpe=0`, `max_drawdown=0`, `final_equity=100000`.
- Network: `api.binance.com` HTTP 451 in this env → loader must use `www.binance.com` or cache. Cached data present in `data/cache/` for 11 symbols.
- Provenance artifacts exist (e.g. `reports/handoff_proof_20261104T175317Z.json`, `T190006Z.json`, `T190220Z.json`) — all show zero trades.

## ROOT CAUSE (DIAGNOSED)
Strict enriched gates block all entries.
- Sole blocker: `rolling_stable_ok` (frac_significant < 0.6 on every real window)
  - BTC/ETH: EG p~0.518, rolling frac~0.176
  - ETH/SOL: EG p~0.577, rolling frac~0.115
  - BTC/SOL: EG p~0.731, rolling frac~0.066
- `examples/run_pairs.py` also loads cached `reports/portfolio_real.json` diagnostics (BTC/ETH `gates.all_pass=False`) as a STATIC all-or-nothing gate compounding the block.
- `utils/cointegration.rolling_cointegration_stability` steps window down but for small trailing samples (e.g. lookback ~60) still returns `insufficient_data` with `frac_significant=0.0` → gate becomes unassessable → fail-closed under strict mode blocks entries. `strategies/pairs_trading.py` recomputes per-bar on trailing windows and enforces enriched gates strictly.

## IMMEDIATE OBJECTIVE (NON-NEGOTIABLE)
Make the pipeline emit REAL trades with concrete metrics from real code paths, OR if NO real window can pass all gates, document the HONEST blocked result with full provenance.
Success requires EITHER:
(A) Nonzero `trades_count`, nonzero `total_return`, nonzero `sharpe`, nonzero `max_drawdown` in `reports/pairs_real_market.json` AND fresh `reports/handoff_proof_<UTC>.json` with concrete metrics, OR
(B) Zero trades BUT accompanied by `reports/pairs_gate_breakdown_<UTC>.json` (per-bar gate pass/fail, share per gate, which gate blocks and on what share, full provenance) AND fresh `reports/handoff_proof_<UTC>.json` documenting the honest blocked outcome.

Silent zero-metrics artifacts are UNACCEPTABLE.

## EXECUTE IN EXACT ORDER (REMOVE BOTTLENECKS FIRST)

### 1) HEALTH CHECK (FAST)
```bash
python -c "import numpy,pandas,statsmodels,scipy,yaml; print('ok')"
python -m pytest -v tests/test_cointegration_campaign31_mt.py tests/test_cointegration_diagnostics_schema.py tests/test_pairs_real_market.py tests/test_cointegration_threshold_invariance.py -q
```
Fix any import/env issues immediately.

### 2) MAP DATA & PROVENANCE
- Inspect `data/loader.py`, `data/cache.py`. Confirm cached Binance 1h for required symbols (BTC,ETH,SOL,...). Note `api.binance.com` HTTP 451 → prefer `www.binance.com` or cache.
- Inspect `reports/pairs_real_market.json`, `reports/cointegration_diagnostics_real.json`, `reports/portfolio_real.json`. Record `hosts_tried`, `blocked_routes`, `cache_used`, `real_data_only`/`fabricated_data` honestly.
- Keep all proof artifacts provenance-complete.

### 3) EMIT PER-BAR GATE BREAKDOWN (DIAGNOSE)
Instrument/run the enriched-gate path for BTC/ETH (and ETH/SOL, BTC/SOL) over walk-forward windows.
Write `reports/pairs_gate_breakdown_<UTC>.json` with:
- per-bar gate booleans (eg_pass, johansen_pass, spread_mr_pass, hl_bounds_pass, leg_stationarity_ok, rolling_stable_ok, no_structural_break, all_pass)
- share of bars passing per gate
- which gate is the sole/blocking gate and on what share of bars
- full provenance (data source, cache/hosts, computed_at, real_data_only/fabricated_data)

Confirm `rolling_stable_ok` is the blocker and why (insufficient_data on short windows).

### 4) UNBLOCK END-TO-END (CORE - HEAVY WORK)
Focus files: `strategies/pairs_trading.py`, `utils/cointegration.py`, `backtest/engine.py`, `examples/run_pairs.py`.
Targets:
- Make `rolling_cointegration_stability` assessable on the trailing samples actually used (e.g. lookback 60/120). Calibration ideas (sanctioned): allow fewer windows when sample is small (e.g. min_windows>=2) or use overlapping windows to get >=3 assessments when possible; prefer stepping window down further; still return `stable=False` if fraction < 0.6. Never hardcode `stable=True`. Never fabricate. If even minimal usable windows cannot be formed, remain fail-closed with explicit `reason: insufficient_data` and record it.
- Ensure `target_schema_diagnostics` propagates honest gate values; `strategies/pairs_trading.py` must not treat aggregate cached diagnostics as per-bar pass (current behavior is correct to be strict). If calibrating makes some windows assessable, ensure causal (trailing only) behavior is preserved.
- Verify causal rolling hedge ratio guards (positive, clipped [1e-6,1e6], no inf/nan), opposing legs via explicit per-asset weights (engine must not overwrite).
- Run: `timeout 1800 python examples/run_pairs.py 2>&1 | tail -200`
- Iterate until `reports/pairs_real_market.json` reflects outcome per fix direction.

### 5) HARDEN & PRODUCE PROOF (REQUIRED)
- Ensure fees/slippage/capital constraints applied.
- Write fresh `reports/handoff_proof_<UTC>.json` with: config, data provenance (real_data_only/fabricated_data/hosts_tried/blocked_routes/cache_used), gates_summary (from breakdown), trades_count, equity_curve_summary, key_metrics (total_return/sharpe/max_drawdown/Calmar/costs), files_modified, reproduction_command, artifacts, verification.
- Re-run targeted tests. Fix failures blocking core pairs path. Leave repo runnable.

## RULES
- Prioritize unblocking over docs.
- Full suite slow - use targeted runs.
- Real data only. Never fabricate.
- Stay laser-focused on pairs/spreads/cointegration.
- Commit nothing unless explicitly asked.
- No investigation-only loops. If blocked, remove bottleneck immediately.
