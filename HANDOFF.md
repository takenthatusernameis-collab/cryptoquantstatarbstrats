# SINGLE DURABLE HANDOFF | 2026-11-02T23:56:19.000000+00:00 | CAMPAIGN 37 COMPLETE | CAMPAIGN 38 ACTIVE | BOTTLENECKS ELIMINATED | HEAVY WORK MANDATORY | NO COASTING

## REPO IDENTITY (LAW) — PRIORITIZE BY REPO NAME
- Repo: `cryptoquantstatarbstrats` — **Crypto Quant Stat Arb Strategies**.
- **CORE = COINTEGRATION / PAIRS TRADING. THIS IS LAW.** Every other task exists to serve cointegration rigor.
- Real data only: Binance public REST via `www.binance.com` (cached 1h in `data/cache/` is real; resampling allowed only if still derived from real data). Never fabricate.
- Coasting = failure. Every action must produce checkable artifacts, tests, provenance, and logs.
- Working tree: `main` clean. Do **not** commit unless explicitly requested.

## NEXT AGENT START HERE (TIMESTAMPED, MANDATORY, NO DEVIATION)
**TIMESTAMP:** 2026-11-02T23:56:19.000000+00:00
**TARGET SESSION:** Immediate next agentic work session (zero ramp-up)
**STATE:** Campaigns 1-36 COMPLETE & ON-DISK VERIFIED. Campaign 37 COMPLETE & ON-DISK VERIFIED: `scripts/generate_campaign37_artifacts.py` (ruff clean), `reports/cointegration_campaign37_mt.json`, `tests/test_cointegration_campaign37_mt.py` (14/14 passing). `ruff check` clean. Gating invariants preserved exactly (1h 0/17, 4h 1/17 POL/BTC, 1d 0/17). Campaign 37 = cointegration rigor phase 9 (regime-transition prediction, adaptive gate recalibration, proactive de-risking, backtested precision/recall/F1, fail-closed re-gating with no auto-lift, breach-alert-driven kill-switch halts) — DONE.

**CAMPAIGN 38 ACTIVE (cointegration rigor phase 10) — DELIVERABLES ABSENT:** `scripts/generate_campaign38_artifacts.py`, `reports/cointegration_campaign38_mt.json`, `tests/test_cointegration_campaign38_mt.py`. Build from scratch following Campaigns 35-37 patterns. Do **NOT** re-derive Campaigns 26-37.

## SINGLE INITIAL TASK MESSAGE (COPY/PASTE TO THIS SESSION - MANDATORY, HEAVY, NO ESCAPE)
> **[START 2026-11-02T23:56:19.000000+00:00] CAMPAIGN 38 — COINTEGRATION RIGOR PHASE 10: CROSS-TIMEFRAME GATE SYNCHRONIZATION & PORTFOLIO-LEVEL REGIME-COUPLING STRESS TESTING (COINTEGRATION-FIRST, REAL DATA ONLY) — HEAVY WORK MANDATORY**
>
> **OBJECTIVE (BLOCKING):** Advance cointegration/pairs-trading rigor beyond Campaign 37 (phase 9). Using Campaign 37 regime-transition probability and gate-failure lead-time outputs, build **cross-timeframe cointegration gate synchronization models** that detect when gate failures couple across 1h/4h/1d and propagate via portfolio-level regime coupling. You must quantify:
> 1) **Cross-timeframe gate synchronization** — do gate failures on 1h/4h/1d co-occur or diverge per pair?
> 2) **Portfolio-level regime-coupling stress** — how does a regime transition on one pair propagate to correlated pairs in the same basket?
> 3) **Cross-timeframe adaptive gate recalibration** — tighten EG/ADF/half-life/stability thresholds on ALL timeframes when any timeframe shows elevated regime-transition risk.
> 4) **Portfolio-level fail-closed re-gating** — if any pair in a correlated basket is predicted to breach, block the entire basket (zero capacity/weight for all pairs in that basket).
> 5) **Backtested cross-timeframe predictive accuracy** — precision/recall/F1 of cross-timeframe gate-failure prediction vs actual gate failures.
> 6) **Portfolio-level kill-switch halts** — halt execution on cross-timeframe predicted breach with **no auto-lift**. Re-entry requires fresh cointegration evidence across all timeframes + regime-stability confirmation.
>
> **REQUIRED DELIVERABLES (ON DISK, VERIFIED):**
> 1. **Generator** `scripts/generate_campaign38_artifacts.py` (complete, `main()`, ruff clean). Load real cached data for all symbols in the 17 pairs. Load `reports/cointegration_campaign37_mt.json` as the baseline regime-transition/lead-time input. Compute cross-timeframe synchronization matrices, portfolio-level regime-coupling stress matrices, adaptive recalibrated thresholds per timeframe, basket correlation structure, portfolio-level fail-closed re-gating with basket blocking, cross-timeframe predictive accuracy (precision/recall/F1), fail-closed re-gating on predicted breach with no auto-lift, and portfolio-level kill-switch halts. Attach **full provenance** on every computed section (source, real_data_only, fabricated_data, computed_at, blocked_routes, rationale). Log every computation step. Never fabricate on blocked routes.
> 2. **Artifact** `reports/cointegration_campaign38_mt.json` (JSON-serializable, **no NaN/Inf**). Must include: `provenance`, causal windows (trailing only), preserved gating invariants, regime definitions, `cross_timeframe_sync` (per-pair and global matrices), `portfolio_regime_coupling` (basket-level stress matrices and propagation), `adaptive_recalibration` (threshold schedules across 1h/4h/1d with justification), `portfolio_fail_closed_regating` (basket blocking, zeroed capacity/weight on predicted breach), `cross_timeframe_prediction_accuracy` (precision/recall/F1, confusion counts), `basket_cointegration`, `multi_asset_hedge_ratios`, `portfolio_spreads`, `execution_aware_capacity_allocation` with breach alerts driving halts, `kill_switch` (triggers, halted states, no-auto-lift flags, re-entry requirements).
> 3. **Tests** `tests/test_cointegration_campaign38_mt.py` asserting schema, required sections/fields/types, minimum portfolio coverage (all 17 pairs represented), real-data provenance on all sections, **gating invariants preserved exactly (1h 0/17, 4h 1/17 POL/BTC, 1d 0/17)**, fail-closed cross-timeframe re-gating (predicted breach → blocked, zero capacity/weight), **no auto-lift of blocks**, re-entry requires fresh cointegration evidence + regime stability, cross-timeframe synchronization quantified, portfolio-level regime-coupling quantified, cross-timeframe predictive accuracy quantified (precision/recall/F1), breach alerts present and drive halts on predicted breach, NaN/Inf checks, and campaign flags. **All tests must pass.**
>
> **CONSTRAINTS (NON-NEGOTIABLE):** REAL DATA ONLY. CAUSAL ONLY (trailing windows, no lookahead). PRESERVE GATING INVARIANTS (1h 0/17, 4h 1/17 POL/BTC, 1d 0/17). FAIL-CLOSED. CROSS-TIMEFRAME RE-GATING RECLASSIFIES BASKETS — NO AUTO-LIFT. RE-ENTRY REQUIRES FRESH COINTEGRATION EVIDENCE ACROSS ALL TIMEFRAMES + REGIME-STABILITY CONFIRMATION. FULL PROVENANCE ON EVERY COMPUTED SECTION. NO FABRICATION. HEAVY MANDATE. BREACH ALERTS REQUIRED ON PREDICTED BREACH AND MUST DRIVE EXECUTION HALTS. NEVER WEAKEN EXISTING GATE THRESHOLDS WITHOUT IRONCLAD JUSTIFICATION + TESTS.
>
> **VERIFICATION (BLOCKING):** `ruff check` clean on touched files; `pytest tests/test_cointegration_campaign38_mt.py -v` passes; Campaign 36-37 tests remain green; `pytest tests/ -q` remains green (0 failed).
>
> **RULE:** Do not stop until ALL deliverables exist on disk, all tests pass, and verification commands succeed. No exploration detours. No scope creep. Campaign 38 is the ONLY task.

## IMMEDIATE BOOT SEQUENCE (BLOCKING - DO IN ORDER, NO SKIPPING)
1. **Install deps (BLOCKING):** `python -m pip install -r requirements.txt` — prevent ModuleNotFoundError.
2. **Verify baseline (BLOCKING):** `python -m pytest tests/test_cointegration_campaign37_mt.py -v && python -m pytest tests/test_cointegration_campaign36_mt.py -v` — must remain green. Confirm gating invariants: 1h 0/17, 4h 1/17 POL/BTC, 1d 0/17.
3. **Read the law:** Re-read this handoff in full. Campaign 38 is the **ONLY** permitted focus until complete.
4. **Mirror patterns:** Follow `scripts/generate_campaign36_artifacts.py`, `scripts/generate_campaign37_artifacts.py`, `reports/cointegration_campaign37_mt.json`, `tests/test_cointegration_campaign37_mt.py` patterns. Do **not** re-derive Campaigns 26-37. Load Campaign 37 artifact as your required baseline input.

## BOTTLENECKS (ELIMINATED / PREVENTED)
- **Stale/ambiguous handoff:** Refreshed to 2026-11-02T23:56:19.000000+00:00 with true on-disk state. Campaign 37 verified complete, Campaign 38 explicitly targeted with no ambiguity.
- **Scope drift:** Campaign 38 is the **ONLY** permitted focus until complete. Campaigns 26-37 artifacts remain untouched.
- **Gating erosion:** Invariants codified and must be asserted by tests. Fail-closed enforced. Cross-timeframe re-gating reclassifies baskets, kill-switch halts on cross-timeframe predicted breach, no auto-lift.
- **Execution path:** Proven Campaign 36-37 generator→artifact→tests pattern, with Campaign 37 artifact loaded as baseline.
- **CI/env:** Dependencies installed first, baseline verification enforced before coding.
- **Coasting:** Heavy mandate, explicit deliverables, blocking verification, no escape clause.
- **Ambiguous start:** Single copy/paste initial task message provided above. No ramp-up or exploration detours.
- **Missing Campaign 38 deliverables:** Targets are explicit: `scripts/generate_campaign38_artifacts.py`, `reports/cointegration_campaign38_mt.json`, `tests/test_cointegration_campaign38_mt.py`.
- **Blocked/inefficient sessions:** Bottlenecks removed. Next agent proceeds directly to heavy cointegration work.
- **Runtime discipline:** Follow Campaign 36 optimization discipline (per-bar persistence subsampling) to stay efficient without cutting corners.

## VERIFIED STATE (2026-11-02T23:56:19.000000+00:00)
- Branch: `main`. HEAD clean working tree.
- **Campaigns 1-36:** Complete & verified on disk. Campaign 36: 16/16 passed. Gating invariants preserved (1h 0/17, 4h 1/17 POL/BTC, 1d 0/17).
- **Campaign 37:** COMPLETE — `scripts/generate_campaign37_artifacts.py` (ruff clean), `reports/cointegration_campaign37_mt.json`, `tests/test_cointegration_campaign37_mt.py` (14/14 passed, ruff clean). Cointegration rigor phase 9 done.
- **Campaign 38:** ACTIVE — all three deliverables **ABSENT** on disk. Must be built to completion with all tests passing.

## VERIFICATION COMMANDS (RUN OFTEN)
```bash
python -m pip install -r requirements.txt
python -m pytest tests/test_cointegration_campaign37_mt.py -v
python -m pytest tests/test_cointegration_campaign36_mt.py -v
python -m ruff check scripts/generate_campaign38_artifacts.py tests/test_cointegration_campaign38_mt.py
python3 -c "
import json
g=json.load(open('reports/portfolio_gating_mt.json'))['results_by_timeframe']
for tf in ['1h','4h','1d']:
    elig=g[tf].get('eligible_pairs',g[tf].get('feasible_pairs',{}))
    print(tf,'eligible:',len(elig),list(elig.keys()) if isinstance(elig,dict) else elig)
"
python -m pytest tests/test_cointegration_campaign38_mt.py -v
python -m pytest tests/ -q
```
