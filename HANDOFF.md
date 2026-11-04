# HANDOFF (SINGLE DURABLE HANDOFF)

TIMESTAMP: 2026-11-04T22:33:09Z
REPO: cryptoquantstatarbstrats
FOCUS: Crypto Quantitative Statistical Arbitrage Strategies (Cointegration/Pairs First)

---

# PRIORITY (REPO-NAME DRIVEN - NON-NEGOTIABLE)

`cryptoquantstatarbstrats` = Crypto Quant Stat Arb Strategies. Cointegration/pairs trading IS the core edge.
Mean reversion, momentum, term structure, volatility surface are SECONDARY and must not displace pairs work.
Every session must treat pairs/spreads/cointegration as the primary deliverable.

---

# THIS SESSION VERIFIED (2026-11-04T22:33Z)

- Deps OK: `numpy,pandas,statsmodels,scipy,yaml` import clean.
- Targeted pairs/cointegration tests: 40 passed
  (`tests/test_cointegration_campaign31_mt.py tests/test_cointegration_diagnostics_schema.py
  tests/test_pairs_real_market.py tests/test_cointegration_threshold_invariance.py -q`).
- `examples/run_pairs.py` COMPLETES end-to-end (exit 0), 5064 hourly bars BTC/ETH/SOL
  2026-04-01->2026-10-28, cached Binance data, network-independent, writes
  `reports/pairs_real_market.json` BUT trades_count=0, total_return=0, sharpe=0,
  max_drawdown=0, final_equity=100000 (PRIMARY BLOCKER - confirmed below).
- `strategies/pairs_trading.py`: causal rolling hedge ratio (guarded >1e-18, clip [1e-6,1e6]),
  opposing legs via explicit per-asset weights, enriched gates fail-closed
  (use_enriched_gates=True, strict_enriched_gates=True default). Gates block all entries.
- `backtest/engine.py`: explicit per-asset weights precedence (`_signals_to_weights`),
  costs/slippage, walk-forward (train=500/test=100, rolling, 4 splits).
- `data/loader.py`, `data/cache.py`: Binance loader with retries/fallbacks; disk cache present
  for 11 symbols 1h 2026-04-01->2026-10-30. Network: api.binance.com HTTP 451; loader uses
  www.binance.com or cache.
- `reports/pairs_gate_diagnosis_real.json` confirms: all three pairs fail the cointegration
  screen on every real window (EG p 0.518/0.577/0.731; rolling frac 0.176/0.115/0.066,
  all < 0.6). `rolling_stable_ok` is FALSE on all 182 rolling windows for every pair.
- Root cause CONFIRMED: `rolling_stable_ok` is the SOLE gate blocker -> enriched_ok=0
  everywhere -> state=0 every bar -> zero entries -> zero trades -> zero metrics.
- `examples/run_pairs.py` compounds this by loading `reports/portfolio_real.json` cached
  diagnostics (BTC/ETH gates.all_pass=False) as a STATIC all-or-nothing gate, blocking even
  bars where sub-gates pass.
- Working tree clean; all prior sessions were checkpoints (no uncommitted changes).

---

# INITIAL TASK MESSAGE (PASTE AS FIRST MESSAGE FOR NEXT AGENT)

```
You are picking up cryptoquantstatarbstrats. NO "investigate only" loops. DO HEAVY WORKING IMMEDIATELY.

REPO-NAME PRIORITY (non-negotiable): cryptoquantstatarbstrats = Crypto Quant Stat Arb Strategies.
Cointegration/pairs trading IS the core edge. Everything else is secondary and must not displace pairs work.

OBJECTIVE: Deliver a verifiably working, REAL-DATA-ONLY end-to-end crypto pairs statistical arbitrage pipeline
(pair selection -> cointegration/spread construction -> z-score signals -> realistic backtest with costs)
that produces concrete, reproducible metrics from real code paths. Treat "cointegration is the core edge" as
non-negotiable. Real data only. Never fabricate candles/IV/funding/basis. Follow existing provenance patterns
(real_data_only, fabricated_data, blocked_routes, computed_at, rationale).

CURRENT STATE (CONFIRMED 2026-11-04T22:33Z):
- Deps OK (`numpy,pandas,statsmodels,scipy,yaml` import). Targeted tests: 40 passed (baseline).
- `examples/run_pairs.py` COMPLETES end-to-end (exit 0, 5064 hourly bars BTC/ETH/SOL 2026-04-01->2026-10-28,
  cached Binance data, network-independent) and writes `reports/pairs_real_market.json`, BUT
  trades_count=0, total_return=0, sharpe=0, max_drawdown=0, final_equity=100000 (PRIMARY BLOCKER - see below).
- `strategies/pairs_trading.py`: causal rolling hedge ratio, opposing legs via explicit weights,
  enriched gates fail-closed (use_enriched_gates=True, strict_enriched_gates=True default). Gates block all
  entries currently.
- `backtest/engine.py`: explicit per-asset weights precedence (_signals_to_weights), costs/slippage,
  walk-forward (train=500/test=100, rolling, 4 splits).
- `data/loader.py`, `data/cache.py`: Binance loader with retries/fallbacks; disk cache present for 11 symbols
  1h 2026-04-01->2026-10-30. Network: api.binance.com HTTP 451; loader uses www.binance.com or cache.

DIAGNOSED BLOCKER (ROOT CAUSE CONFIRMED - REMOVE FIRST):
  Strict enriched cointegration gates are fail-closed and block all entries. Root cause identified:
  `rolling_stable_ok` is the SOLE gate blocker - every other gate (EG, Johansen, spread MR, half-life bounds,
  leg stationarity, no structural break) can pass on a subset of bars, but rolling_stable_ok never passes
  because `frac_significant >= 0.6` is not met on any real window for any pair:
    - BTC/ETH: EG p=0.518, rolling frac=0.176 over full 5064-bar history (stable=False)
    - ETH/SOL: EG p=0.577, rolling frac=0.115 (stable=False)
    - BTC/SOL: EG p=0.731, rolling frac=0.066 (stable=False)
  None of the three pairs passes the cointegration screen on any real window -> enriched_ok=0 everywhere ->
  state=0 on every bar -> zero entries -> zero trades -> zero metrics. This is the CORRECT strict-gate research
  result: no pair here is stably cointegrated, so the enriched screen correctly keeps the strategy in cash.
  `examples/run_pairs.py` compounds this by loading `reports/portfolio_real.json` cached diagnostics
  (BTC/ETH gates.all_pass=False) as a STATIC all-or-nothing gate, so even bars where sub-gates pass are blocked.

FIX DIRECTION (sanctioned by this handoff; NOT a mandate to coerce):
  1. Diagnose exactly which gate(s) fail and on what share of bars; emit a per-bar gate breakdown report
     (`reports/pairs_gate_breakdown_<UTC>.json`) with per-bar gate pass/fail and share of bars per gate.
  2. Make the pipeline emit real trades with concrete metrics: EITHER calibrate the rolling-stability/window
     assessment so the gate genuinely evaluates (fix the `insufficient_data` auto-fail on short windows) and can
     genuinely pass on real windows where a pair IS cointegrated, producing nonzero trades_count/total_return/
     sharpe/maxDD in pairs_real_market.json; OR, if no real window passes all gates, document the honest
     blocked result with the full per-bar gate breakdown + provenance (zero trades is then the honest outcome,
     but it must be documented with the gate breakdown, not left as a silent zero-metrics artifact).
  3. Constraints: Never coerce a failing gate to pass; fail-closed stays; no fabrication of candles/IV/funding/basis;
     no threshold weakening that hides a genuine failure. Calibration = making the gate assessable/genuine, not
     hardcoding True.
  4. Target: nonzero trades_count, nonzero total_return, nonzero sharpe/maxDD in pairs_real_market.json AND a
     fresh `reports/handoff_proof_<UTC>.json` with config, data provenance (real_data_only/fabricated_data/
     hosts_tried/blocked_routes/cache_used), gates_summary, trades_count, equity_curve_summary, key_metrics,
     files_modified, reproduction_command, artifacts, verification.

EXECUTE IN THIS EXACT ORDER (remove bottlenecks first):

1. TARGETED HEALTH CHECK (FAST - MUST PASS)
   - Deps: `python -c "import numpy,pandas,statsmodels,scipy,yaml; print('ok')"`
   - Targeted pairs/cointegration tests (NOT full suite):
     `python -m pytest -v tests/test_cointegration_campaign31_mt.py tests/test_cointegration_diagnostics_schema.py tests/test_pairs_real_market.py tests/test_cointegration_threshold_invariance.py -q`
   - Expected: 40 passed. Fix any import/env issues in pyproject/requirements immediately.

2. MAP REAL DATA & PROVENANCE (BLOCKER REMOVAL)
   - Inspect `data/loader.py`, `data/cache.py`. Cached Binance data exists in `data/cache/` (BTC, ETH, SOL,
     ADA, AVAX, BNB, DOT, LINK, LTC, POL, XRP at 1h, 2026-04-01 -> 2026-10-30).
   - Check `reports/pairs_real_market.json` and `reports/cointegration_diagnostics_real.json` for provenance.
   - `api.binance.com` returns HTTP 451 in this env; loader must try `www.binance.com` first or use cache.
   - Record hosts_tried/blocked_routes/cache_used honestly in all proof artifacts.

3. EMIT PER-BAR GATE BREAKDOWN (DIAGNOSE THE BLOCKER)
   - Instrument/run the enriched-gate path so each bar's gate pass/fail is recorded for BTC/ETH (and ETH/SOL,
     BTC/SOL) over the walk-forward windows.
   - Write `reports/pairs_gate_breakdown_<UTC>.json`: per-bar gate booleans, share-of-bars passing per gate,
     which gate is the blocker and on what share of bars, full provenance per bar.
   - Confirm rolling_stable_ok is the sole blocker on what share of bars.

4. WIRE ONE PAIRS PATH END-TO-END (CORE - HEAVY WORK)
   - Focus: `strategies/pairs_trading.py` (CointegrationPairsStrategy), trace `backtest/engine.py`
     (`_signals_to_weights` gives explicit per-asset weights precedence), costs/slippage/regime gating.
   - Run: `timeout 1800 python examples/run_pairs.py 2>&1 | tail -150` (BTC/ETH, walk-forward 4 splits rolling).
   - Fix integration gaps until the script completes and writes `reports/pairs_real_market.json` per the fix
     direction above (nonzero trades via sanctioned calibration, OR honest documented blocked result). No
     stubs/fabrication. Resolve the diagnosed blocker.

5. HARDEN STAT-ARB MATH (CORE - HEAVY WORK)
   - Causal rolling hedge ratio: positive, clipped, guarded (no inf/nan; >1e-18; clip [1e-6,1e6]).
   - Opposing legs preserved via explicit per-asset weights (engine must not overwrite).
   - Enriched gates fail-closed: `use_enriched_gates=True`, `strict_enriched_gates=True`. Any missing/None/false
     blocks entries. Causal/trailing only. Never fabricate gate values.
   - Engle-Granger + Johansen + spread MR + HL bounds + leg stationarity + rolling stability + structural breaks.

6. ADD REALISM & PRODUCE PROOF (REQUIRED - HEAVY WORK)
   - Ensure fee_rate/slippage/capital constraints applied (engine handles turnover costs).
   - Extract concrete metrics from engine/results (trades, fills, PnL, cum returns, Sharpe, maxDD, Calmar, costs).
   - Write durable proof: `reports/handoff_proof_<UTC_TIMESTAMP>.json` with config, data provenance
     (real_data_only/fabricated_data/hosts/blocked_routes/cache_used), gates_summary, trades_count,
     equity_curve_summary, key_metrics, files_modified, reproduction_command, artifacts, verification.
   - Re-run targeted tests. Fix failures blocking core pairs path. Leave repo runnable.

RULES:
- Prioritize unblocking execution over docs. Write code to fix failures.
- Full suite large/slow - use targeted runs. Expand only if blocking core pairs.
- Real data only. Never fabricate candles/IV/funding/basis.
- Stay laser-focused on pairs/spreads/cointegration per repo name.
- Commit nothing unless explicitly asked. Update handoff only for new hard blockers.
- Success = modified code + working end-to-end pairs stat-arb run + verifiable proof artifact with concrete
  metrics from real code paths. A run that completes with zero trades is NOT progress unless it is accompanied
  by the per-bar gate breakdown report and honest blocked-result documentation; silent zero-metrics artifacts
  are unacceptable.

FOCUS CAMPAIGN (future agents MUST do heavy work - never avoid it):
- Every session re-runs the targeted pairs/cointegration tests (40 passed baseline) and confirms
  `examples/run_pairs.py` completes end-to-end against real data BEFORE declaring progress.
- Any new pair must pass the full enriched cointegration gate set with full provenance before being traded.
- Not complete until a fresh `reports/handoff_proof_*.json` exists with concrete metrics (nonzero trades_count,
  nonzero total_return/sharpe/maxDD) from a real-code-path run, OR the honest blocked result is documented with
  a per-bar gate breakdown + provenance.
- If blocked/inefficient, remove bottlenecks immediately - no investigation-only loops. The diagnosed
  rolling_stable_ok blocker (strategies/pairs_trading.py:276-381; rolling 720-bar stability vs short
  walk-forward windows; frac 0.066-0.176 < 0.6 on all three real pairs) is the blocker to resolve before any
  session is considered effective. Calibrate the gate so it genuinely evaluates on real windows (fail-closed,
  no coercion), or document the honest blocked outcome with full per-bar gate breakdown.
```

---

# KNOWN STATE (INFERRED / CONFIRMED)

- Deps: OK (`numpy,pandas,statsmodels,scipy,yaml` import). Verified 2026-11-04T22:33Z.
- Targeted tests: 40 passed (verified 2026-11-04T22:33Z).
- `examples/run_pairs.py`: COMPLETES end-to-end (exit 0), 5064 hourly bars BTC/ETH/SOL 2026-04-01->2026-10-28,
  writes `reports/pairs_real_market.json`, BUT trades_count=0, total_return=0, sharpe=0, max_drawdown=0,
  final_equity=100000 (PRIMARY BLOCKER - diagnosed above).
- `strategies/pairs_trading.py`: causal rolling hedge ratio with guards, opposing legs via explicit weights,
  enriched gates (fail-closed, strict default). Gates block all entries currently.
- `backtest/engine.py`: explicit per-asset weights precedence (_signals_to_weights), costs/slippage, regime gating,
  walk-forward utilities (train=500/test=100, rolling, 4 splits).
- `data/loader.py`, `data/cache.py`: Binance loader with retries/fallbacks; disk cache present for 11 symbols
  1h 2026-04-01->2026-10-30.
- Network: `api.binance.com` HTTP 451; use `www.binance.com` or cached data.
- Existing proofs: `reports/handoff_proof_20261104T175317Z.json`, `...T190006Z.json`, `...T190220Z.json` (all
  trades_count 0 on those runs).
- Root cause CONFIRMED: `rolling_stable_ok` sole gate blocker; no pair (BTC/ETH, ETH/SOL, BTC/SOL) passes the
  cointegration screen on any real window (EG p 0.518/0.577/0.731; rolling frac 0.176/0.115/0.066, all < 0.6).

---

# BOTTLENECK REMOVAL PRIORITY

1. Environment/deps - ensure imports work (verified OK).
2. Zero-trades gate blocker - DIAGNOSED: `rolling_stable_ok` sole blocker (frac 0.066-0.176 < 0.6 on all three
   pairs; `insufficient_data` auto-fail on short windows). Remove by calibrating the gate so it genuinely
   evaluates on real windows (fail-closed, no coercion) OR documenting the honest blocked outcome with a
   per-bar gate breakdown + provenance.
3. End-to-end execution - run `examples/run_pairs.py` to completion; capture full output; produce nonzero
   trades/metrics via sanctioned calibration, or honest documented blocked result.
4. Stat-arb hardening - verify causal behavior and gate enforcement without fabrication.
5. Proof artifact - generate fresh `reports/handoff_proof_<UTC_TIMESTAMP>.json` with concrete metrics +
   per-bar gate breakdown report `reports/pairs_gate_breakdown_<UTC>.json`.

---

# IMMEDIATE ACTIONS FOR NEXT AGENT

- [ ] Verify deps: `python -c "import numpy,pandas,statsmodels,scipy,yaml; print('ok')"`
- [ ] Run targeted tests: `python -m pytest -v tests/test_cointegration_campaign31_mt.py tests/test_cointegration_diagnostics_schema.py tests/test_pairs_real_market.py tests/test_cointegration_threshold_invariance.py -q` (expect 40 passed)
- [ ] Run pairs example: `timeout 1800 python examples/run_pairs.py 2>&1 | tail -200` (confirm zero-trades blocker)
- [ ] Emit per-bar gate breakdown -> `reports/pairs_gate_breakdown_<UTC>.json`; confirm rolling_stable_ok is sole blocker and on what share of bars.
- [ ] Fix per fix direction: calibrate gate so it genuinely evaluates on real windows (fail-closed, no coercion) so pipeline emits real trades, OR document honest blocked result with gate breakdown + provenance.
- [ ] Re-run `examples/run_pairs.py` until pairs_real_market.json reflects the outcome with full metrics; write fresh proof artifact `reports/handoff_proof_<UTC>.json`.
- [ ] Re-run targeted tests after changes; leave repo runnable.
