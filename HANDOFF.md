# NEXT AGENT INITIAL TASK MESSAGE (PASTE THIS FIRST)

TIMESTAMP: 2026-11-05T01:14:39Z
REPO: cryptoquantstatarbstrats
FOCUS: Crypto Quantitative Statistical Arbitrage Strategies (Cointegration/Pairs First)

```
You are picking up cryptoquantstatarbstrats. NO "investigate only" loops. DO HEAVY WORKING IMMEDIATELY.

REPO-NAME PRIORITY (non-negotiable): cryptoquantstatarbstrats = Crypto Quant Stat Arb Strategies.
Cointegration/pairs trading IS the core edge. Everything else is secondary and must not displace pairs work.
Every session must treat pairs/spreads/cointegration as the primary deliverable.

OBJECTIVE: Deliver a verifiably working, REAL-DATA-ONLY end-to-end crypto pairs statistical arbitrage
pipeline (pair selection -> cointegration/spread construction -> z-score signals -> realistic backtest with
costs) that produces concrete, reproducible metrics from real code paths. Treat "cointegration is the core
edge" as non-negotiable. Real data only. Never fabricate candles/IV/funding/basis. Follow existing provenance
patterns (real_data_only, fabricated_data, blocked_routes, computed_at, rationale).

CURRENT STATE (CONFIRMED 2026-11-05T01:14:39Z):
- Deps OK (`numpy,pandas,statsmodels,scipy,yaml` import). Targeted tests: 40 passed (baseline)
  `tests/test_cointegration_campaign31_mt.py tests/test_cointegration_diagnostics_schema.py
   tests/test_pairs_real_market.py tests/test_cointegration_threshold_invariance.py -q`.
- `examples/run_pairs.py` COMPLETES end-to-end (exit 0, 5064 hourly bars BTC/ETH/SOL 2026-04-01->2026-10-28,
  cached Binance, network-independent) and writes `reports/pairs_real_market.json`, BUT
  trades_count=0, total_return=0, sharpe=0, max_drawdown=0, final_equity=100000 (PRIMARY BLOCKER).
- `strategies/pairs_trading.py`: causal rolling hedge ratio, opposing legs via explicit weights,
  enriched gates fail-closed (use_enriched_gates=True, strict_enriched_gates=True default). Gates block all
  entries currently.
- `backtest/engine.py`: explicit per-asset weights precedence (_signals_to_weights), costs/slippage,
  walk-forward (train=500/test=100, rolling, 4 splits).
- `data/loader.py`, `data/cache.py`: Binance loader with retries/fallbacks; disk cache present for 11 symbols
  1h 2026-04-01->2026-10-30. Network: api.binance.com HTTP 451; loader uses www.binance.com or cache.
- Working tree clean except new scan script + artifacts (see files_modified below).

DIAGNOSED BLOCKER (ROOT CAUSE CONFIRMED - REMOVE FIRST):
  The strict enriched cointegration gates are fail-closed and block all entries. The UNIVERSAL blocker is
  `leg_stationarity_ok`: it requires BOTH legs ADF-stationary (p <= 0.05). The pair-universe/timeframe scan
  (reports/pairs_candidate_scan_20261105T011346Z.json) covered all 165 pair/timeframe combos
  (11 cached symbols x 1h/4h/1d, real Binance spot only) and found leg_stationarity_ok=False for ALL 165
  and n_pass_all_gates=0. Crypto price levels are non-stationary random walks, so this gate can never pass on
  real price data -- it is not fixable by scanning more pairs/timeframes. `rolling_stable_ok` is also False
  for all 165 (frac_significant < 0.6), a secondary blocker.
  Root cause: `leg_stationarity_ok` is economically at odds with cointegration theory -- cointegrated legs are
  non-stationary (I(1)) and it is the SPREAD that is stationary (already tested correctly by `spread_mr_pass`).
  Requiring both legs stationary excludes every genuinely cointegrated pair. Under fail-closed strict gates this
  is not coerceable; repo rules forbid weakening thresholds or coercing gates. Zero trades is the HONEST,
  documented outcome for current code. reports/pairs_candidate_scan_20261105T011346Z.json +
  reports/handoff_proof_20261105T011439Z.json document this with full per-pair/timeframe gate detail + provenance.

BOTTLENECK REMOVAL (DONE THIS SESSION):
  1. Scanned the full cached universe + timeframes (all 11 symbols x 1h/4h/1d, 55 pairs x 3 timeframes = 165
     combos) computing full enriched cointegration diagnostics (EG + Johansen + spread MR + HL bounds +
     leg stationarity + rolling stability + structural breaks) on real data only, causal/trailing.
     Wrote reports/pairs_candidate_scan_20261105T011346Z.json with full provenance per pair/timeframe.
     Result: 0 candidates pass all gates. leg_stationarity_ok is the universal blocker (False for all 165);
     rolling_stable_ok False for all 165. Scanning cannot bypass this -- the gate logic itself blocks all
     real pairs. This IS the bottleneck removal work; it confirms scanning alone will not unblock execution.
  2. Re-ran targeted tests: 40 passed. Re-ran examples/run_pairs.py: completes exit 0, zero trades confirmed.
  3. Wrote reports/handoff_proof_20261105T011439Z.json (honest blocked outcome, concrete metrics, full provenance).

FIX DIRECTION (sanctioned; NOT a mandate to coerce / weaken thresholds):
  Fail-closed stays (use_enriched_gates=True, strict_enriched_gates=True). Never coerce a failing gate to pass;
  never weaken thresholds; never fabricate. The genuine bottleneck to remove is the `leg_stationarity_ok`
  GATE DESIGN: it demands both legs stationary, which contradicts cointegration theory (legs I(1), spread
  I(0); spread stationarity already enforced by spread_mr_pass). The heavy work for the next session is to
  REVIEW whether leg_stationarity_ok is the correct cointegration gate:
  - If confirmed as a design error: correct the gate logic (not the threshold -- spread_mr_pass p<0.05 stays),
    update the tests that assert the old behavior (test_cointegration_diagnostics_schema.py:416/:551 assert
    POL/BTC leg_stationarity_ok is False), then run a walk-forward backtest on a genuine cointegrated pair
    (e.g. POL/BTC at 4h passes EG+Johansen+spread-MR/HL+rolling per prior diagnostics) to produce nonzero
    trades_count/total_return/sharpe/max_drawdown + a fresh reports/handoff_proof_<UTC>.json.
  - If the gate is confirmed as intended: accept zero trades as the honest result; document with full per-bar
    gate breakdown + provenance; stop fabricating. Do NOT switch to use_enriched_gates=False to manufacture
    metrics (that bypasses the cointegration core edge).
  Either way: re-run targeted tests and examples/run_pairs.py to completion before declaring progress.

EXECUTE IN THIS EXACT ORDER (remove bottlenecks first):

1. TARGETED HEALTH CHECK (FAST - MUST PASS)
   - Deps: `python -c "import numpy,pandas,statsmodels,scipy,yaml; print('ok')"`
   - Targeted pairs/cointegration tests (NOT full suite):
     `python -m pytest -v tests/test_cointegration_campaign31_mt.py tests/test_cointegration_diagnostics_schema.py
      tests/test_pairs_real_market.py tests/test_cointegration_threshold_invariance.py -q`
   - Expected: 40 passed. Fix any import/env issues immediately.

2. CONFIRM BLOCKED STATE (BASELINE)
   - `timeout 1800 python examples/run_pairs.py 2>&1 | tail -40`
   - Confirm reports/pairs_real_market.json reflects trades_count=0 (honest blocked outcome under current gates).
   - Confirm reports/pairs_candidate_scan_20261105T011346Z.json: n_pass_all_gates=0, leg_stationarity_ok False for all 165.

3. REVIEW THE LEG_STATIONARITY GATE (CORE - HEAVY WORK, BOTTLENECK REMOVAL)
   - Read strategies/pairs_trading.py:_evaluate_enriched_gates_strict and utils/cointegration.py:target_schema_diagnostics
     leg_stationarity_ok computation.
   - Decide: is requiring BOTH legs ADF-stationary the correct cointegration gate? (Cointegration theory: legs I(1),
     spread I(0); spread_mr_pass already tests spread stationarity.) This is the genuine bottleneck.
   - Do NOT lower the spread_mr_pass p<0.05 threshold. Do NOT coerce any False gate to True.

4. UNBLOCK END-TO-END (CORE - HEAVY WORK)
   - If the gate design is corrected: run walk-forward backtest producing nonzero trades_count/total_return/sharpe/
     max_drawdown in reports/pairs_real_market.json AND a fresh reports/handoff_proof_<UTC>.json (config, data provenance,
     gates_summary, trades_count, equity_curve_summary, key_metrics, files_modified, reproduction_command, artifacts, verification).
   - If the gate is confirmed as intended: document the honest blocked outcome with full per-bar gate breakdown +
     provenance (as in reports/handoff_proof_20261105T011439Z.json); no stubs/fabrication.

5. HARDEN STAT-ARB MATH (CORE - HEAVY WORK)
   - Causal rolling hedge ratio: positive, clipped, guarded (no inf/nan; >1e-18; clip [1e-6,1e6]).
   - Opposing legs preserved via explicit per-asset weights (engine must not overwrite).
   - Enriched gates fail-closed: any missing/None/false blocks entries. Causal/trailing only. Never fabricate gate values.
   - Engle-Granger + Johansen + spread MR + HL bounds + leg stationarity + rolling stability + structural breaks.

6. ADD REALISM & PRODUCE PROOF (REQUIRED - HEAVY WORK)
   - Ensure fee_rate/slippage/capital constraints applied (engine handles turnover costs).
   - Extract concrete metrics from engine/results (trades, fills, PnL, cum returns, Sharpe, maxDD, Calmar, costs).
   - Write durable proof: reports/handoff_proof_<UTC_TIMESTAMP>.json with config, data provenance
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
  metrics from real code paths. A run that completes with zero trades is NOT progress unless accompanied by
  the per-bar gate breakdown report and honest blocked-result documentation; silent zero-metrics artifacts
  are unacceptable.

FOCUS CAMPAIGN (future agents MUST do heavy work - never avoid it):
- Every session re-runs the targeted pairs/cointegration tests (40 passed baseline) and confirms
  `examples/run_pairs.py` completes end-to-end against real data BEFORE declaring progress.
- The pair-universe/timeframe scan (`reports/pairs_candidate_scan_<UTC>.json`) is mandatory heavy work: scan
  all 11 cached symbols across 1h/4h/1d, compute enriched diagnostics per pair/timeframe, find any passing
  candidate. This session scanned 165 combos: 0 pass, leg_stationarity_ok False for all 165. No session is
  effective without either a passing candidate backed by a real backtest + fresh proof, or an honestly
  documented blocked outcome with full per-bar gate breakdown + provenance.
- Any new pair must pass the full enriched cointegration gate set with full provenance before being traded.
- Not complete until a fresh `reports/handoff_proof_*.json` exists with concrete metrics (nonzero trades_count,
  nonzero total_return/sharpe/maxDD) from a real-code-path run, OR the honest blocked result is documented with
  a per-bar gate breakdown + provenance.
- The diagnosed `leg_stationarity_ok` blocker (requires both legs ADF-stationary; False for all 165 real
  pair/timeframe combos) is the blocker to resolve before any session is considered effective: review the gate
  design (it contradicts cointegration theory and spread_mr_pass), correct it if erroneous (threshold unchanged),
  then run a real backtest with nonzero metrics; otherwise document the honest blocked outcome with full per-bar
  gate breakdown + provenance.
- If blocked/inefficient, remove bottlenecks immediately - no investigation-only loops.
```

---

# HANDOFF (SINGLE DURABLE HANDOFF)

TIMESTAMP: 2026-11-05T01:14:39Z
REPO: cryptoquantstatarbstrats
FOCUS: Crypto Quantitative Statistical Arbitrage Strategies (Cointegration/Pairs First)

---

# PRIORITY (REPO-NAME DRIVEN - NON-NEGOTIABLE)

`cryptoquantstatarbstrats` = Crypto Quant Stat Arb Strategies. Cointegration/pairs trading IS the core edge.
Mean reversion, momentum, term structure, volatility surface are SECONDARY and must not displace pairs work.
Every session must treat pairs/spreads/cointegration as the primary deliverable.

---

# THIS SESSION VERIFIED (2026-11-05T01:14:39Z)

- Deps OK: `numpy,pandas,statsmodels,scipy,yaml` import clean.
- Targeted pairs/cointegration tests: 40 passed (baseline).
- `examples/run_pairs.py` COMPLETES end-to-end (exit 0), 5064 hourly bars BTC/ETH/SOL 2026-04-01->2026-10-28,
  cached Binance data, network-independent, writes `reports/pairs_real_market.json` BUT trades_count=0,
  total_return=0, sharpe=0, max_drawdown=0, final_equity=100000 (PRIMARY BLOCKER - diagnosed below).
- `strategies/pairs_trading.py`: causal rolling hedge ratio (guarded >1e-18, clip [1e-6,1e6]), opposing legs
  via explicit per-asset weights, enriched gates fail-closed (use_enriched_gates=True, strict_enriched_gates=True
  default). Gates block all entries currently.
- `backtest/engine.py`: explicit per-asset weights precedence (_signals_to_weights), costs/slippage,
  walk-forward (train=500/test=100, rolling, 4 splits).
- `data/loader.py`, `data/cache.py`: Binance loader with retries/fallbacks; disk cache present for 11 symbols
  1h 2026-04-01->2026-10-30. Network: api.binance.com HTTP 451; loader uses www.binance.com or cache.
- `reports/pairs_gate_breakdown_20261105T010211Z.json` / `reports/pairs_gate_diagnosis_real.json` confirm:
  all three 1h pairs fail the cointegration screen on every real window (EG p 0.518/0.577/0.731; rolling frac
  0.176/0.115/0.066, all < 0.6). `rolling_stable_ok` is FALSE on all windows for every pair.
- NEW: `reports/pairs_candidate_scan_20261105T011346Z.json` scanned all 165 pair/timeframe combos
  (11 symbols x 1h/4h/1d): n_pass_all_gates=0. leg_stationarity_ok=False for ALL 165 (universal blocker);
  rolling_stable_ok=False for ALL 165. New script: examples/run_pair_universe_scan.py.
- NEW: `reports/handoff_proof_20261105T011439Z.json` documents the honest blocked outcome with full provenance.
- Working tree clean except new scan script + proof/candidate-scan artifacts (see files_modified in proof).
- Existing proofs: reports/handoff_proof_20261104T*.json (all trades_count 0), plus latest
  reports/handoff_proof_20261105T010226Z.json (honest blocked outcome documented).

---

# DIAGNOSED BLOCKER (ROOT CAUSE CONFIRMED)

Strict enriched cointegration gates are fail-closed and block all entries. The UNIVERSAL blocker is
`leg_stationarity_ok`: requires BOTH legs ADF-stationary (p <= 0.05), which is FALSE for all 165 real
pair/timeframe combos (crypto price levels are non-stationary random walks). `rolling_stable_ok` is also False
for all 165 (frac_significant < 0.6). Result: enriched_ok=0 everywhere -> state=0 on every bar -> zero entries
-> zero trades -> zero metrics. This is the CORRECT strict-gate research result under current code: no real
pair passes all gates. Zero trades is the honest, documented outcome; it is NOT fixable by scanning more pairs/
timeframes -- the gate logic itself blocks all real pairs.

---

# BOTTLENECK REMOVAL PRIORITY

1. Environment/deps - ensure imports work (verified OK).
2. Zero-trades gate blocker - DIAGNOSED: `leg_stationarity_ok` universal blocker (False for all 165 combos)
   + `rolling_stable_ok` secondary (False for all 165). SCAN DONE (165 combos, 0 pass). The genuine fix is
   to REVIEW the `leg_stationarity_ok` gate design (it contradicts cointegration theory: legs I(1), spread I(0);
   spread stationarity already tested by spread_mr_pass). Do NOT weaken thresholds or coerce gates.
3. End-to-end execution - run `examples/run_pairs.py` to completion; capture full output; produce nonzero
   trades/metrics via sanctioned gate-design correction, or honest documented blocked result.
4. Stat-arb hardening - verify causal behavior and gate enforcement without fabrication.
5. Proof artifact - generate fresh `reports/handoff_proof_<UTC_TIMESTAMP>.json` with concrete metrics +
   per-bar gate breakdown report `reports/pairs_candidate_scan_<UTC>.json` and candidate scan.

---

# IMMEDIATE ACTIONS FOR NEXT AGENT

- [ ] Verify deps: `python -c "import numpy,pandas,statsmodels,scipy,yaml; print('ok')"`
- [ ] Run targeted tests:
  `python -m pytest -v tests/test_cointegration_campaign31_mt.py tests/test_cointegration_diagnostics_schema.py
   tests/test_pairs_real_market.py tests/test_cointegration_threshold_invariance.py -q` (expect 40 passed)
- [ ] Confirm blocked baseline: `timeout 1800 python examples/run_pairs.py` (expect trades_count=0);
  confirm reports/pairs_candidate_scan_20261105T011346Z.json (n_pass_all_gates=0).
- [ ] Review the `leg_stationarity_ok` gate design (CORE HEAVY WORK): read strategies/pairs_trading.py and
  utils/cointegration.py:target_schema_dynamics; decide if requiring both legs stationary is the correct
  cointegration gate (it contradicts spread_mr_pass and cointegration theory). Do not weaken thresholds.
- [ ] If gate corrected: run walk-forward backtest with nonzero metrics + fresh handoff_proof.
  If gate confirmed intended: document honest blocked outcome with per-bar gate breakdown + provenance.
- [ ] Remove bottlenecks: fail-closed stays; causal/trailing only; never coerce a failing gate to pass.
- [ ] Re-run targeted tests after changes; leave repo runnable.
