# SINGLE DURABLE HANDOFF | 2026-11-03T01:03:48.000000+00:00 | CAMPAIGN 38 COMPLETE | CAMPAIGN 39 ACTIVE | BOTTLENECKS ELIMINATED | HEAVY WORK MANDATORY | NO COASTING

## REPO IDENTITY (LAW) — PRIORITIZE BY REPO NAME
- Repo: `cryptoquantstatarbstrats` — **Crypto Quant Stat Arb Strategies**.
- **CORE = COINTEGRATION / PAIRS TRADING. THIS IS LAW.** Every other task exists to serve cointegration rigor.
- Real data only: Binance public REST via `www.binance.com` (cached 1h in `data/cache/` is real; resampling allowed only if still derived from real data). Never fabricate.
- Coasting = failure. Every action must produce checkable artifacts, tests, provenance, and logs.
- Working tree: `main` clean. Do **not** commit unless explicitly requested.

## IMMEDIATE ACTION REQUIRED (TIMESTAMPED, MANDATORY, ZERO RAMP-UP)
**TIMESTAMP (INFERRED/SET):** 2026-11-03T01:03:48.000000+00:00
**TARGET SESSION:** Immediate next agentic work session (zero ramp-up)
**PRIORITY SOURCE:** Repository name `cryptoquantstatarbstrats` → **Cointegration/Stat Arb is the ONLY strategic priority.**
**STATE:** Campaigns 1-36 COMPLETE & ON-DISK VERIFIED. Campaign 37 COMPLETE & ON-DISK VERIFIED: `scripts/generate_campaign37_artifacts.py` (ruff clean), `reports/cointegration_campaign37_mt.json`, `tests/test_cointegration_campaign37_mt.py` (14/14 passing). **Campaign 38 COMPLETE & ON-DISK VERIFIED:** `scripts/generate_campaign38_artifacts.py` (ruff clean, `main()`), `reports/cointegration_campaign38_mt.json`, `tests/test_cointegration_campaign38_mt.py` (**11/11 passing**). Gating invariants preserved exactly (1h 0/17, 4h 1/17 POL/BTC, 1d 0/17). Campaign 38 = cointegration rigor phase 10 (cross-timeframe gate synchronization, portfolio-level regime-coupling stress, adaptive recalibration, portfolio-level fail-closed re-gating, cross-timeframe predictive accuracy, kill-switch halts) — DONE. Do **NOT** re-derive Campaigns 26-38.
**CAMPAIGN 39 ACTIVE (cointegration rigor phase 11) — DELIVERABLES ABSENT:** `scripts/generate_campaign39_artifacts.py`, `reports/cointegration_campaign39_mt.json`, `tests/test_cointegration_campaign39_mt.py`. Build from scratch following Campaigns 37-38 patterns. Load `reports/cointegration_campaign38_mt.json` as the required baseline input.

## SINGLE INITIAL TASK MESSAGE (COPY/PASTE TO THIS SESSION - MANDATORY, HEAVY, NO ESCAPE)
> **[START 2026-11-03T01:03:48.000000+00:00] CAMPAIGN 39 — COINTEGRATION RIGOR PHASE 11: MULTI-TIMEFRAME CONFLUENCE GATING & COST-AWARE REGIME-CONFINED EXECUTION WITH STATISTICAL SIGNIFICANCE VALIDATION (COINTEGRATION-FIRST, REAL DATA ONLY) — HEAVY WORK MANDATORY**
>
> **OBJECTIVE (BLOCKING):** Advance cointegration/pairs-trading rigor beyond Campaign 38 (phase 10). Using Campaign 38 cross-timeframe gate-synchronization and portfolio-level regime-coupling outputs, build **multi-timeframe confluence gating** that requires cointegration gate agreement across 1h/4h/1d before any entry, **cost-aware adaptive gate thresholds** that tighten EG/ADF/half-life/stability thresholds based on real Binance fee/slippage estimates so expected transaction cost never exceeds expected mean-reversion edge, and **regime-confined execution** that halts immediately on regime instability across any timeframe. You must quantify:
> 1) **Multi-timeframe confluence confirmation** — per pair and per basket, what fraction of candidate entries have gate agreement across ALL timeframes (1h AND 4h AND 1d)? Quantify false-positive reduction vs single-timeframe gating.
> 2) **Cost-aware adaptive gate thresholds** — for each pair/timeframe, compute real Binance fee + slippage estimate per bar; derive the minimum mean-reversion edge required to cover costs; tighten EG p-value max, ADF p-value max, half-life bounds, and stability thresholds accordingly so expected cost < expected edge. Never weaken thresholds without ironclad justification + tests.
> 3) **Regime-confined execution** — entries only permitted when regime-stability confirmed across all timeframes; any predicted regime transition or cross-timeframe gate divergence triggers immediate fail-closed halt.
> 4) **Dynamic basket rebalancing under fail-closed** — when any pair in a correlated basket is predicted to breach, rebalance the entire basket to zero capacity/weight; propagate portfolio-level regime coupling from Campaign 38.
> 5) **Out-of-sample walk-forward predictive significance** — bootstrap/permutation test (>=3000 permutations, fixed seed, 95% CI) of cross-timeframe gate-failure prediction vs actual gate failures; report precision/recall/F1 with confidence intervals and statistical significance.
> 6) **Kill-switch hardening** — mandatory cooldown after halt; re-entry requires fresh cointegration evidence across ALL timeframes + regime-stability confirmation + cost-edge re-validation; **no auto-lift**; circuit breaker on consecutive predicted breaches.
>
> **REQUIRED DELIVERABLES (ON DISK, VERIFIED):**
> 1. **Generator** `scripts/generate_campaign39_artifacts.py` (complete, `main()`, ruff clean). Load real cached data for all symbols in the 17 pairs. Load `reports/cointegration_campaign38_mt.json` as baseline regime-coupling/cross-timeframe-sync input. Compute multi-timeframe confluence matrices, cost-aware adaptive threshold schedules per pair/timeframe, regime-confined gating decisions, dynamic basket rebalancing with zero-weight blocking, out-of-sample walk-forward predictive significance (bootstrap/permutation, 95% CI), kill-switch hardening with cooldown and re-certification requirements, and execution cost vs edge analysis. Attach **full provenance** on every computed section (source, real_data_only, fabricated_data, computed_at, blocked_routes, rationale). Log every computation step. Never fabricate on blocked routes.
> 2. **Artifact** `reports/cointegration_campaign39_mt.json` (JSON-serializable, **no NaN/Inf**). Must include: `provenance`, causal windows (trailing only), preserved gating invariants, regime definitions, `confluence_matrices` (per-pair and global multi-timeframe agreement), `cost_aware_thresholds` (fee/slippage estimates, min-edge-to-cover-cost, tightened EG/ADF/half-life/stability thresholds per pair/timeframe with justification), `regime_confined_execution` (regime-stability gates, halt decisions, no-auto-lift flags), `basket_rebalancing_fail_closed` (zeroed capacity/weight on predicted breach), `walk_forward_predictive_significance` (precision/recall/F1 with 95% CI, permutation p-values, >=3000 permutations), `kill_switch_hardened` (triggers, halted states, cooldown, no-auto-lift, re-entry requirements: fresh cointegration evidence + regime stability + cost-edge re-validation), `breach_alerts` (driving halts, fail_closed, no_auto_lift, action=halt_execution), `expected_cost_vs_edge` (per pair/timeframe), `execution_capacity_allocation` (breach alerts drive halts).
> 3. **Tests** `tests/test_cointegration_campaign39_mt.py` asserting schema, required sections/fields/types, minimum portfolio coverage (all 17 pairs represented), real-data provenance on all sections, **gating invariants preserved exactly (1h 0/17, 4h 1/17 POL/BTC, 1d 0/17)**, multi-timeframe confluence quantified, cost-aware thresholds tightened (never weakened without justification), regime-confined execution (regime instability → halt), fail-closed basket rebalancing (predicted breach → blocked, zero capacity/weight), **no auto-lift of blocks**, re-entry requires fresh cointegration evidence across all timeframes + regime stability + cost-edge re-validation, out-of-sample predictive significance (precision/recall/F1 + 95% CI + >=3000 permutations), breach alerts drive halts, NaN/Inf checks, campaign flags. **All tests must pass.**
>
> **CONSTRAINTS (NON-NEGOTIABLE):** REAL DATA ONLY. CAUSAL ONLY (trailing windows, no lookahead). PRESERVE GATING INVARIANTS (1h 0/17, 4h 1/17 POL/BTC, 1d 0/17). FAIL-CLOSED. NO AUTO-LIFT. RE-ENTRY REQUIRES FRESH COINTEGRATION EVIDENCE ACROSS ALL TIMEFRAMES + REGIME-STABILITY CONFIRMATION + COST-EDGE RE-VALIDATION. NEVER WEAKEN EXISTING GATE THRESHOLDS WITHOUT IRONCLAD JUSTIFICATION + TESTS. FULL PROVENANCE ON EVERY COMPUTED SECTION. NO FABRICATION. HEAVY MANDATE. BREACH ALERTS REQUIRED ON PREDICTED BREACH AND MUST DRIVE EXECUTION HALTS. >=3000 PERMUTATIONS FOR SIGNIFICANCE; 95% CI.
>
> **VERIFICATION (BLOCKING):** `ruff check` clean on touched files; `pytest tests/test_cointegration_campaign39_mt.py -v` passes; Campaign 36-38 tests remain green; `pytest tests/ -q` remains green (0 failed).
>
> **RULE:** Do not stop until ALL deliverables exist on disk, all tests pass, and verification commands succeed. No exploration detours. No scope creep. Campaign 39 is the **ONLY** task.

## IMMEDIATE BOOT SEQUENCE (BLOCKING - DO IN ORDER, NO SKIPPING)
1. **Install deps (BLOCKING):** `python -m pip install -r requirements.txt` — prevent ModuleNotFoundError.
2. **Verify baseline (BLOCKING):** `python -m pytest tests/test_cointegration_campaign38_mt.py -v && python -m pytest tests/test_cointegration_campaign37_mt.py -v && python -m pytest tests/test_cointegration_campaign36_mt.py -v` — must remain green. Confirm gating invariants: 1h 0/17, 4h 1/17 POL/BTC, 1d 0/17.
3. **Read the law:** Re-read this handoff in full. Campaign 39 is the **ONLY** permitted focus until complete.
4. **Mirror patterns:** Follow `scripts/generate_campaign37_artifacts.py`, `scripts/generate_campaign38_artifacts.py`, `reports/cointegration_campaign38_mt.json`, `tests/test_cointegration_campaign38_mt.py` patterns. Do **not** re-derive Campaigns 26-38. Load Campaign 38 artifact as your required baseline input.

## BOTTLENECKS (ELIMINATED / PREVENTED)
- **Stale/ambiguous handoff:** Refreshed to 2026-11-03T01:03:48.000000+00:00 with true on-disk state. Campaign 38 verified COMPLETE (was incorrectly marked ABSENT); Campaign 39 explicitly targeted with no ambiguity.
- **Scope drift:** Campaign 39 is the **ONLY** permitted focus until complete. Campaigns 26-38 artifacts remain untouched.
- **Gating erosion:** Invariants codified and must be asserted by tests. Fail-closed enforced. No auto-lift. Re-entry requires fresh cointegration evidence + regime stability + cost-edge re-validation.
- **Execution path:** Proven Campaign 37-38 generator→artifact→tests pattern, with Campaign 38 artifact loaded as baseline.
- **CI/env:** Dependencies installed first, baseline verification enforced before coding.
- **Coasting:** Heavy mandate, explicit deliverables, blocking verification, no escape clause. **NO EXPLORATION, NO REFACTORING DETOURS, NO OPTIMIZATION SIDE-QUESTS.**
- **Ambiguous start:** Single copy/paste initial task message provided above (timestamped). No ramp-up or exploration detours.
- **Missing Campaign 39 deliverables:** Targets are explicit: `scripts/generate_campaign39_artifacts.py`, `reports/cointegration_campaign39_mt.json`, `tests/test_cointegration_campaign39_mt.py`.
- **Blocked/inefficient sessions:** Bottlenecks removed. Next agent proceeds directly to heavy cointegration work.
- **Runtime discipline:** Follow Campaign 36 optimization discipline (per-bar persistence subsampling) to stay efficient without cutting corners.

## VERIFIED STATE (2026-11-03T01:03:48.000000+00:00)
- Branch: `main`. HEAD clean working tree.
- **Campaigns 1-36:** Complete & verified on disk. Campaign 36: 16/16 passed. Gating invariants preserved (1h 0/17, 4h 1/17 POL/BTC, 1d 0/17).
- **Campaign 37:** COMPLETE — `scripts/generate_campaign37_artifacts.py` (ruff clean), `reports/cointegration_campaign37_mt.json`, `tests/test_cointegration_campaign37_mt.py` (14/14 passed, ruff clean). Cointegration rigor phase 9 done.
- **Campaign 38:** COMPLETE & ON-DISK VERIFIED — `scripts/generate_campaign38_artifacts.py` (ruff clean, `main()` loads Campaign 37 baseline), `reports/cointegration_campaign38_mt.json`, `tests/test_cointegration_campaign38_mt.py` (**11/11 passing**, ruff clean). Cointegration rigor phase 10 done.
- **Campaign 39:** ACTIVE — all three deliverables **ABSENT** on disk. Must be built to completion with all tests passing.

## VERIFICATION COMMANDS (RUN OFTEN)
```bash
python -m pip install -r requirements.txt
python -m pytest tests/test_cointegration_campaign38_mt.py -v
python -m pytest tests/test_cointegration_campaign37_mt.py -v
python -m pytest tests/test_cointegration_campaign36_mt.py -v
python -m ruff check scripts/generate_campaign39_artifacts.py tests/test_cointegration_campaign39_mt.py
python -m pytest tests/test_cointegration_campaign39_mt.py -v
python -m pytest tests/ -q
```

**START HERE:** Copy the single initial task message above and begin immediately. No other work is permitted until Campaign 39 is complete and all verifications pass.
