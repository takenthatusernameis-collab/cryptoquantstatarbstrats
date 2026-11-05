# NEXT AGENT INITIAL TASK MESSAGE (PASTE THIS FIRST)

TIMESTAMP: 2026-11-05T01:56:44Z
REPO: cryptoquantstatarbstrats
FOCUS: Crypto Quantitative Statistical Arbitrage Strategies (Cointegration/Pairs First)

```
YOU ARE PICKING UP cryptoquantstatarbstrats. NO "investigate only". DO HEAVY WORKING IMMEDIATELY.

REPO-NAME PRIORITY (NON-NEGOTIABLE): cryptoquantstatarbstrats = Crypto Quant Stat Arb Strategies.
Cointegration/pairs trading IS the core edge. Everything else is secondary.
Every session MUST treat pairs/spreads/cointegration as the primary deliverable.

OBJECTIVE: Remove the universal gate bottleneck and produce a verifiably working, REAL-DATA-ONLY
end-to-end crypto pairs statistical arbitrage pipeline (pair selection -> cointegration/spread construction
-> z-score signals -> realistic backtest with costs) that produces concrete, reproducible metrics from
real code paths. Never fabricate candles/IV/funding/basis. Follow existing provenance patterns.

CURRENT VERIFIED STATE (2026-11-05T01:56:44Z):
- Deps OK (numpy,pandas,statsmodels,scipy,yaml). Targeted tests: 40 passed.
- examples/run_pairs.py completes end-to-end (exit 0) on cached Binance data (BTC/ETH/SOL 1h
  2026-04-01->2026-10-28) but produces trades_count=0, total_return=0, sharpe=0, max_dd=0.
- Full universe scan done: reports/pairs_candidate_scan_20261105T011346Z.json scanned all 165 combos
  (11 symbols x 1h/4h/1d), n_pass_all_gates=0. leg_stationarity_ok=False for ALL 165 (universal blocker).
  rolling_stable_ok=False for ALL 165.
- Honest proof exists: reports/handoff_proof_20261105T011439Z.json documents blocked outcome.
- Engine preserves opposing legs via explicit per-asset weights; enriched gates fail-closed by design.

UNIVERSAL BOTTLENECK (MUST REMOVE):
The gate leg_stationarity_ok requires BOTH legs to be ADF-stationary (p <= 0.05). For genuine
cointegrated pairs, legs are I(1) (non-stationary) and the SPREAD is I(0) (stationary) -- this is
exactly what spread_mr_pass tests. Requiring legs stationary contradicts cointegration theory and blocks
every real pair in the cached universe. This is a GATE DESIGN ERROR, not a data issue.

FIX DIRECTION (CORRECT DESIGN, DO NOT COERCE):
- DO NOT weaken thresholds (spread_mr_pass p<0.05 stays). DO NOT coerce failing gates to True.
- CORRECT the gate logic to match cointegration theory: legs need not both be stationary for
  cointegration. The spread stationarity (spread_mr_pass) is the correct test. Review and fix
  leg_stationarity_ok in utils/cointegration.py (both comprehensive_cointegration_diagnostics and
  target_schema_diagnostics) and ensure strategy gates behave consistently.
- Update tests that assert the old (incorrect) behavior: tests/test_cointegration_diagnostics_schema.py
  expects leg_stationarity_ok False for non-stationary legs in specific cases - these assertions need
  to change to reflect correct theory. Update them.
- After fixing, re-scan or directly test a plausible cointegrated pair (e.g. POL/BTC at 4h) with
  walk-forward backtest to produce NONZERO trades_count/total_return/sharpe/max_drawdown.
- Write fresh reports/handoff_proof_<UTC>.json with concrete metrics from real code paths.

EXECUTE IN THIS EXACT ORDER (REMOVE BOTTLENECKS FIRST):

1. HEALTH CHECK (FAST)
   - python -c "import numpy,pandas,statsmodels,scipy,yaml; print('ok')"
   - python -m pytest -v tests/test_cointegration_campaign31_mt.py tests/test_cointegration_diagnostics_schema.py tests/test_pairs_real_market.py tests/test_cointegration_threshold_invariance.py -q
   (40 passed baseline - fix any breakage immediately)

2. CONFIRM BLOCKED BASELINE
   - timeout 1800 python examples/run_pairs.py 2>&1 | tail -30
   - cat reports/pairs_real_market.json | grep -E '"trades_count|total_return|sharpe|max_drawdown"'
   - Confirm scan shows leg_stationarity_ok False for all 165

3. FIX THE GATE DESIGN (CORE HEAVY WORK - BOTTLENECK REMOVAL)
   - Read utils/cointegration.py: leg_stationarity logic in comprehensive_cointegration_diagnostics (line ~448)
     and target_schema_diagnostics (line ~811). Understand current implementation.
   - Read strategies/pairs_trading.py gate evaluation - ensure consistency.
   - Fix leg_stationarity_ok to be correct per cointegration theory. Options:
     a) Remove leg_stationarity_ok from required gates (spread_mr_pass is sufficient)
     b) Change to require at most one leg stationary OR require legs non-stationary in a specific pattern
     c) Make it not block when spread is clearly stationary (spread_mr_pass True)
   Choose the fix that matches theory and allows genuine cointegrated pairs to pass. Do NOT weaken
   spread_mr_pass threshold.
   - Update tests/test_cointegration_diagnostics_schema.py assertions that encode the old incorrect
     behavior (around lines 416, 551 etc.) to match corrected theory.
   - Ensure both diagnostic paths (comprehensive and target_schema) are consistent.

4. FIND A PASSING PAIR & RUN REAL BACKTEST (CORE HEAVY WORK)
   - Re-run universe scan to find pairs that now pass all gates:
     timeout 3600 python examples/run_pair_universe_scan.py 2>&1 | tail -40
   - Or test specific candidates like POL/BTC at 4h directly via quick script.
   - Once a pair passes all gates with full provenance, run walk-forward backtest producing
     NONZERO trades_count, total_return, sharpe, max_drawdown.
   - Use existing infrastructure (strategies/pairs_trading.py, backtest/engine.py).

5. PRODUCE VERIFIABLE PROOF (REQUIRED)
   - Write reports/handoff_proof_<UTC_TIMESTAMP>.json with:
     config, data_provenance (real_data_only/fabricated_data/hosts/blocked_routes/cache_used),
     gates_summary, trades_count, equity_curve_summary, key_metrics, files_modified,
     reproduction_command, artifacts, verification
   - Re-run targeted tests (must still pass or be updated correctly)
   - Run examples/run_pairs.py to completion and confirm metrics are from real code paths

RULES:
- Prioritize unblocking execution over docs. Write code to fix failures.
- Full suite large/slow - use targeted runs.
- Real data only. Never fabricate candles/IV/funding/basis.
- Stay laser-focused on pairs/spreads/cointegration per repo name.
- Commit nothing unless explicitly asked.
- Success = modified code + working end-to-end pairs stat-arb run producing NONZERO concrete metrics
  from real code paths + fresh verifiable proof artifact.
- Do NOT switch to use_enriched_gates=False to manufacture metrics.
- Correct gate design to match theory; do not coerce gates or weaken thresholds.

FOCUS CAMPAIGN (FUTURE AGENTS MUST DO HEAVY WORK):
- Every session re-runs targeted pairs/cointegration tests and examples/run_pairs.py before declaring progress.
- The pair universe scan is mandatory heavy work when no passing candidate exists.
- Any new pair must pass full enriched cointegration gates with full provenance before trading.
- leg_stationarity_ok design flaw is THE blocker - fix it correctly or prove it's not fixable with
  full evidence. "Investigation only" is not allowed.
- Not complete until fresh reports/handoff_proof_*.json exists with concrete nonzero metrics from
  real code paths.
```

---

# HANDOFF (SINGLE DURABLE HANDOFF)

TIMESTAMP: 2026-11-05T01:56:44Z
REPO: cryptoquantstatarbstrats
FOCUS: Crypto Quantitative Statistical Arbitrage Strategies (Cointegration/Pairs First)

## PRIORITY (REPO-NAME DRIVEN - NON-NEGOTIABLE)
`cryptoquantstatarbstrats` = Crypto Quant Stat Arb Strategies. Cointegration/pairs trading IS the core edge.
Mean reversion/momentum/term structure/vol surface are SECONDARY.

## THIS SESSION VERIFIED
- Deps OK: numpy,pandas,statsmodels,scipy,yaml
- Targeted pairs/cointegration tests: 40 passed
- examples/run_pairs.py completes (exit 0), 5064 hourly bars BTC/ETH/SOL 2026-04-01->2026-10-28 (cached Binance) -> trades_count=0, total_return=0, sharpe=0, max_dd=0, final_equity=100000
- strategies/pairs_trading.py: causal rolling hedge ratio (guarded, clipped), opposing legs via explicit weights, enriched gates fail-closed
- backtest/engine.py: explicit per-asset weights precedence, costs/slippage, walk-forward
- data/cache.py: 11 symbols 1h cached 2026-04-01->2026-10-30; api.binance.com HTTP 451 in env
- reports/pairs_candidate_scan_20261105T011346Z.json: 165 combos scanned, n_pass_all_gates=0, leg_stationarity_ok False for ALL 165, rolling_stable_ok False for ALL 165
- reports/handoff_proof_20261105T011439Z.json: honest blocked outcome documented
- New scan script: examples/run_pair_universe_scan.py

## ROOT CAUSE (CONFIRMED)
Universal blocker: `leg_stationarity_ok` requires BOTH legs ADF-stationary (p<=0.05). Crypto price levels are non-stationary random walks. Cointegration theory requires legs I(1), spread I(0) - spread stationarity is tested by `spread_mr_pass` (correct). This gate design contradicts theory and blocks all real pairs.

## IMMEDIATE ACTION REQUIRED
1. Fix gate design in utils/cointegration.py (comprehensive_cointegration_diagnostics and target_schema_diagnostics) - make leg_stationarity_ok consistent with cointegration theory without weakening spread_mr_pass threshold
2. Update tests/test_cointegration_diagnostics_schema.py to match corrected behavior
3. Re-scan universe, find passing pair, run walk-forward backtest with NONZERO metrics
4. Write fresh reports/handoff_proof_<UTC>.json with concrete metrics from real code paths
5. Re-run targeted tests

## FILES TO FOCUS ON
- utils/cointegration.py (leg_stationarity_ok logic)
- strategies/pairs_trading.py (gate evaluation)
- tests/test_cointegration_diagnostics_schema.py (update assertions)
- examples/run_pair_universe_scan.py (re-run after fix)
- examples/run_pairs.py (validate end-to-end)

## SUCCESS CRITERIA
- Targeted tests pass (after necessary updates)
- examples/run_pairs.py completes with REAL trades_count > 0, nonzero total_return/sharpe/max_dd from real code paths
- Fresh reports/handoff_proof_<UTC>.json with full provenance and concrete metrics
- No fabrication, fail-closed behavior preserved where appropriate, theory-correct gates
