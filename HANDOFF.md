# NEXT AGENT INITIAL TASK MESSAGE (PASTE THIS FIRST)

TIMESTAMP: 2026-11-05T01:03:13Z
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

CURRENT STATE (CONFIRMED 2026-11-05T01:03:13Z):
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
  1h 2026-04-01->2026-10-30 (BTC, ETH, SOL, ADA, AVAX, BNB, DOT, LINK, LTC, POL, XRP).
  Network: api.binance.com HTTP 451; loader uses www.binance.com or cache.
- Root cause CONFIRMED: `rolling_stable_ok` is the SOLE gate blocker - no pair passes the cointegration screen
  on any real 1h window (EG p 0.518/0.577/0.731; rolling frac 0.176/0.115/0.066, all < 0.6). Honest blocked
  outcome documented: reports/pairs_gate_breakdown_20261105T010211Z.json +
  reports/handoff_proof_20261105T010226Z.json (zero trades is the honest outcome, gate breakdown provided).

DIAGNOSED BLOCKER (ROOT CAUSE CONFIRMED - REMOVE FIRST):
  Strict enriched cointegration gates are fail-closed and block all entries. `rolling_stable_ok` never passes
  because frac_significant >= 0.6 is not met on any real 1h window for BTC/ETH, ETH/SOL, BTC/SOL ->
  enriched_ok=0 everywhere -> state=0 on every bar -> zero entries -> zero trades -> zero metrics. This is the
  CORRECT strict-gate research result for these three pairs at 1h: none is stably cointegrated, so the enriched
  screen correctly keeps the strategy in cash. Zero trades is NOT acceptable as silent progress unless accompanied
  by the per-bar gate breakdown + honest blocked-result documentation (done). NEXT: break the bottleneck by
  scanning the broader cached universe + timeframes to find ANY pair/timeframe that genuinely passes all gates,
  then run a real backtest with nonzero metrics; if none pass anywhere, document the honest blocked outcome with
  full provenance and stop fabricating.

FIX DIRECTION (sanctioned; NOT a mandate to coerce):
  1. Expand pair universe + timeframes: scan all cached symbols (11) across 1h/4h/1d; compute cointegration
     diagnostics for every pair; find any pair/timeframe that passes all enriched gates. Write
     reports/pairs_candidate_scan_<UTC>.json with full provenance per pair/timeframe.
  2. If a passing window exists, run walk-forward backtest producing nonzero trades_count/total_return/sharpe/
     max_drawdown in pairs_real_market.json AND a fresh reports/handoff_proof_<UTC>.json (config, data provenance,
     gates_summary, trades_count, equity_curve_summary, key_metrics, files_modified, reproduction_command,
     artifacts, verification).
  3. If none pass on any real window/timeframe, document the honest blocked outcome with full per-bar gate
     breakdown + provenance; never fabricate candles/IV/funding/basis; never weaken thresholds to hide failure.
  4. Remove bottlenecks: ensure rolling_cointegration_stability is assessable on trailing samples
     (min_windows>=2, overlapping windows) while fail-closed; propagate honest gates; causal/trailing only.
     Never coerce a failing gate to pass; fail-closed stays.

EXECUTE IN THIS EXACT ORDER (remove bottlenecks first):

1. TARGETED HEALTH CHECK (FAST - MUST PASS)
   - Deps: `python -c "import numpy,pandas,statsmodels,scipy,yaml; print('ok')"`
   - Targeted pairs/cointegration tests (NOT full suite):
     `python -m pytest -v tests/test_cointegration_campaign31_mt.py tests/test_cointegration_diagnostics_schema.py
      tests/test_pairs_real_market.py tests/test_cointegration_threshold_invariance.py -q`
   - Expected: 40 passed. Fix any import/env issues in pyproject/requirements immediately.

2. MAP REAL DATA & PROVENANCE (BLOCKER REMOVAL)
   - Inspect `data/loader.py`, `data/cache.py`. Cached Binance data exists for 11 symbols at 1h
     (2026-04-01 -> 2026-10-30). Confirm 4h/1d availability or compute from cached 1h by resampling if supported.
   - `api.binance.com` returns HTTP 451 in this env; loader must try `www.binance.com` first or use cache.
   - Record hosts_tried/blocked_routes/cache_used honestly in all proof artifacts.

3. EXPAND PAIR UNIVERSE + TIMEFRAMES SCAN (CORE - HEAVY WORK, BOTTLENECK REMOVAL)
   - Scan all cached symbols (11) across 1h/4h/1d; all pairs per timeframe.
   - Compute full enriched cointegration diagnostics (Engle-Granger + Johansen + spread MR + HL bounds +
     leg stationarity + rolling stability + structural breaks) on real data only, causal/trailing.
   - Write `reports/pairs_candidate_scan_<UTC>.json`: per pair/timeframe gate pass/fail, frac_significant,
     n_windows, full provenance, which (if any) pair/timeframe passes ALL gates.
   - Confirm rolling_stable_ok share of bars / frac_significant per candidate.

4. UNBLOCK END-TO-END (CORE - HEAVY WORK)
   - If a passing pair/timeframe exists: focus `strategies/pairs_trading.py` + `backtest/engine.py`
     (_signals_to_weights gives explicit per-asset weights precedence), costs/slippage/regime gating.
     Run `timeout 1800 python examples/run_pairs.py 2>&1 | tail -150` until `reports/pairs_real_market.json`
     reflects nonzero trades/metrics via sanctioned calibration (fail-closed, no coercion).
   - If no pair/timeframe passes all gates on real data: wire the honest blocked path (fail-closed stays),
     produce per-bar gate breakdown + documented blocked result; no stubs/fabrication.

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
  metrics from real code paths. A run that completes with zero trades is NOT progress unless accompanied by
  the per-bar gate breakdown report and honest blocked-result documentation; silent zero-metrics artifacts
  are unacceptable.

FOCUS CAMPAIGN (future agents MUST do heavy work - never avoid it):
- Every session re-runs the targeted pairs/cointegration tests (40 passed baseline) and confirms
  `examples/run_pairs.py` completes end-to-end against real data BEFORE declaring progress.
- The pair-universe/timeframe scan (`reports/pairs_candidate_scan_<UTC>.json`) is mandatory heavy work: scan
  all 11 cached symbols across 1h/4h/1d, compute enriched diagnostics per pair/timeframe, find any passing
  candidate. No session is effective without either a passing candidate backed by a real backtest + fresh proof,
  or an honestly documented blocked outcome with full per-bar gate breakdown + provenance.
- Any new pair must pass the full enriched cointegration gate set with full provenance before being traded.
- Not complete until a fresh `reports/handoff_proof_*.json` exists with concrete metrics (nonzero trades_count,
  nonzero total_return/sharpe/maxDD) from a real-code-path run, OR the honest blocked result is documented with
  a per-bar gate breakdown + provenance.
- If blocked/inefficient, remove bottlenecks immediately - no investigation-only loops. The diagnosed
  `rolling_stable_ok` blocker (strategies/pairs_trading.py:366-371; rolling 720-bar stability vs short
  walk-forward windows; frac 0.066-0.176 < 0.6 on all three real pairs) is the blocker to resolve before any
  session is considered effective: scan broader universe/timeframes to find a genuinely passing candidate, or
  document the honest blocked outcome with full per-bar gate breakdown.
```

---

# HANDOFF (SINGLE DURABLE HANDOFF)

TIMESTAMP: 2026-11-05T01:03:13Z
REPO: cryptoquantstatarbstrats
FOCUS: Crypto Quantitative Statistical Arbitrage Strategies (Cointegration/Pairs First)

---

# PRIORITY (REPO-NAME DRIVEN - NON-NEGOTIABLE)

`cryptoquantstatarbstrats` = Crypto Quant Stat Arb Strategies. Cointegration/pairs trading IS the core edge.
Mean reversion, momentum, term structure, volatility surface are SECONDARY and must not displace pairs work.
Every session must treat pairs/spreads/cointegration as the primary deliverable.

---

# THIS SESSION VERIFIED (2026-11-05T01:03:13Z)

- Deps OK: `numpy,pandas,statsmodels,scipy,yaml` import clean.
- Targeted pairs/cointegration tests: 40 passed (baseline).
- `examples/run_pairs.py` COMPLETES end-to-end (exit 0), 5064 hourly bars BTC/ETH/SOL 2026-04-01->2026-10-28,
  cached Binance data, network-independent, writes `reports/pairs_real_market.json` BUT trades_count=0,
  total_return=0, sharpe=0, max_drawdown=0, final_equity=100000 (PRIMARY BLOCKER - diagnosed below).
- `strategies/pairs_trading.py`: causal rolling hedge ratio (guarded >1e-18, clip [1e-6,1e6]), opposing legs
  via explicit per-asset weights, enriched gates fail-closed (use_enriched_gates=True,
  strict_enriched_gates=True default). Gates block all entries currently.
- `backtest/engine.py`: explicit per-asset weights precedence (_signals_to_weights), costs/slippage,
  walk-forward (train=500/test=100, rolling, 4 splits).
- `data/loader.py`, `data/cache.py`: Binance loader with retries/fallbacks; disk cache present for 11 symbols
  1h 2026-04-01->2026-10-30. Network: api.binance.com HTTP 451; loader uses www.binance.com or cache.
- `reports/pairs_gate_diagnosis_real.json` / `reports/pairs_gate_breakdown_20261105T010211Z.json` confirm:
  all three pairs fail the cointegration screen on every real 1h window (EG p 0.518/0.577/0.731; rolling frac
  0.176/0.115/0.066, all < 0.6). `rolling_stable_ok` is FALSE on all windows for every pair.
- Root cause CONFIRMED: `rolling_stable_ok` is the SOLE gate blocker -> enriched_ok=0 everywhere -> state=0
  every bar -> zero entries -> zero trades -> zero metrics.
- Working tree clean; all prior sessions were checkpoints (no uncommitted changes).
- Existing proofs: reports/handoff_proof_20261104T*.json (all trades_count 0), plus latest
  reports/handoff_proof_20261105T010226Z.json (honest blocked outcome documented).

---

# DIAGNOSED BLOCKER (ROOT CAUSE CONFIRMED)

Strict enriched cointegration gates are fail-closed and block all entries. `rolling_stable_ok` is the SOLE gate
blocker:
- BTC/ETH: EG p=0.6109, rolling frac=0.176 over full 5064-bar history (stable=False)
- ETH/SOL: EG p=0.577, rolling frac=0.115 (stable=False)
- BTC/SOL: EG p=0.731, rolling frac=0.066 (stable=False)
None of the three pairs passes the cointegration screen on any real 1h window -> enriched_ok=0 everywhere ->
state=0 on every bar -> zero entries -> zero trades -> zero metrics. This is the CORRECT strict-gate research
result: no pair here is stably cointegrated at 1h, so the enriched screen correctly keeps the strategy in cash.
`examples/run_pairs.py` no longer compounds this with a static all-or-nothing cached gate (fixed: cached
aggregate diagnostic is NOT used as a per-bar gate). Zero trades is the honest, documented outcome for these
three pairs at 1h.

---

# BOTTLENECK REMOVAL PRIORITY

1. Environment/deps - ensure imports work (verified OK).
2. Zero-trades gate blocker - DIAGNOSED: `rolling_stable_ok` sole blocker (frac 0.066-0.176 < 0.6 on all three
   1h pairs). Remove by SCANNING the broader cached universe + timeframes (all 11 symbols x 1h/4h/1d) to find
   ANY pair/timeframe that genuinely passes all enriched gates (fail-closed, no coercion), then run a real
   backtest with nonzero metrics; if none pass, document the honest blocked outcome with full per-bar gate
   breakdown + provenance.
3. End-to-end execution - run `examples/run_pairs.py` to completion; capture full output; produce nonzero
   trades/metrics via sanctioned calibration, or honest documented blocked result.
4. Stat-arb hardening - verify causal behavior and gate enforcement without fabrication.
5. Proof artifact - generate fresh `reports/handoff_proof_<UTC_TIMESTAMP>.json` with concrete metrics +
   per-bar gate breakdown report `reports/pairs_gate_breakdown_<UTC>.json` and candidate scan
   `reports/pairs_candidate_scan_<UTC>.json`.

---

# IMMEDIATE ACTIONS FOR NEXT AGENT

- [ ] Verify deps: `python -c "import numpy,pandas,statsmodels,scipy,yaml; print('ok')"`
- [ ] Run targeted tests:
  `python -m pytest -v tests/test_cointegration_campaign31_mt.py tests/test_cointegration_diagnostics_schema.py
   tests/test_pairs_real_market.py tests/test_cointegration_threshold_invariance.py -q` (expect 40 passed)
- [ ] Map real data/provenance: inspect data/loader.py, data/cache.py; confirm 11 cached symbols 1h; record
  hosts_tried/blocked_routes/cache_used.
- [ ] Run pair-universe/timeframe scan (all 11 symbols x 1h/4h/1d, all pairs) computing enriched cointegration
  diagnostics; write reports/pairs_candidate_scan_<UTC>.json; find any passing candidate.
- [ ] If passing candidate exists: run walk-forward backtest with nonzero metrics + fresh handoff_proof.
  If none pass: document honest blocked outcome with per-bar gate breakdown + provenance.
- [ ] Remove bottlenecks: rolling_cointegration_stability assessable on trailing samples (min_windows>=2,
  overlapping) while fail-closed; causal/trailing only.
- [ ] Re-run targeted tests after changes; leave repo runnable.
