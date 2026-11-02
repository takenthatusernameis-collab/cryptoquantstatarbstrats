# SINGLE DURABLE HANDOFF | 2026-11-02T23:40:31.000000+00:00 | CAMPAIGN 37 ACTIVE | BOTTLENECKS REMOVED | HEAVY WORK REQUIRED | NO COASTING

## REPO IDENTITY (LAW) — PRIORITIZE BY REPO NAME
- Repo: `cryptoquantstatarbstrats` — **Crypto Quant Stat Arb Strategies**.
- **CORE = COINTEGRATION / PAIRS TRADING.** Every other line of work serves cointegration rigor. Cointegration is law.
- Real data only: Binance public REST via `www.binance.com` (cached 1h in `data/cache/` is real; resampling allowed only if still from real data). Never fabricate.
- Coasting = failure. Every action must produce checkable artifacts, tests, provenance, logs.
- Working tree: `main` clean. Do **not** commit unless explicitly requested.

## NEXT AGENT START HERE (TIMESTAMPED, MANDATORY, NO DEVIATION)
**TIMESTAMP:** 2026-11-02T23:40:31.000000+00:00
**TARGET SESSION:** Next agentic work session (immediate, no ramp-up)
**STATE:** Campaigns 1-36 COMPLETE & ON-DISK VERIFIED. Full suite green (740 passed, 1 skipped). Campaign 36 deliverables verified: `scripts/generate_campaign36_artifacts.py`, `reports/cointegration_campaign36_mt.json`, `tests/test_cointegration_campaign36_mt.py` (16 tests all passing). `ruff check` clean on Campaign 36 files. Gating invariants preserved exactly (1h 0/17, 4h 1/17 POL/BTC, 1d 0/17). Regime-conditioned gate persistence/decay, forward-reliability/walk-forward gate stability, regime-conditioned failure rates, multi-regime convergence/divergence stress, fail-closed re-gating with no auto-lift, breach-alert-driven kill-switch halts implemented and tested (Campaign 36 = cointegration rigor phase 8, DONE).
**CAMPAIGN 37 ACTIVE (cointegration rigor phase 9) — Deliverables ABSENT on disk:** `scripts/generate_campaign37_artifacts.py`, `reports/cointegration_campaign37_mt.json`, `tests/test_cointegration_campaign37_mt.py` — build from scratch following Campaigns 35-36 patterns. Do NOT re-derive Campaigns 26-36.
**NEXT FOCUS (COINTEGRATION-FIRST, REAL DATA ONLY):** Campaign 37 — **cointegration regime-transition prediction & adaptive gate recalibration** across 1h/4h/1d on real Binance cached data. Using Campaign 36 persistence/decay outputs, build predictive models that flag impending cointegration gate failure before it occurs: regime-transition probability (vol/trend regime change likelihood), gate-failure lead-time estimation, adaptive gate recalibration thresholds (tighten EG/ADF/half-life thresholds when regime-transition risk rises), proactive de-risking (reduce capacity/weight ahead of predicted breaks), backtested predictive accuracy (precision/recall of gate failures), and fail-closed execution halts on predicted breach. Real Binance cached data only. Heavy artifacts/tests/provenance/logs mandatory. No coasting.

**PRIORITY BY REPO IDENTITY:** `cryptoquantstatarbstrats` = **Crypto Quant Stat Arb Strategies**. **CORE = COINTEGRATION/PAIRS TRADING — LAW.** All work serves cointegration rigor.

## SINGLE INITIAL TASK MESSAGE (COPY/PASTE TO GUIDE THIS SESSION - MANDATORY, HEAVY, NO ESCAPE)
> **[START 2026-11-02T23:40:31.000000+00:00] CAMPAIGN 37 — COINTEGRATION RIGOR PHASE 9: REGIME-TRANSITION PREDICTION & ADAPTIVE GATE RECALIBRATION (COINTEGRATION-FIRST, REAL DATA ONLY) — HEAVY WORK MANDATORY**
>
> **OBJECTIVE (BLOCKING):** Advance cointegration/pairs-trading rigor beyond Campaign 36 (phase 8). Using Campaign 36 gate persistence/decay and regime-conditioned failure-rate outputs, build **predictive cointegration regime-transition models** that flag impending gate failure before it occurs across 1h/4h/1d on real Binance cached data. Quantify: regime-transition probability (likelihood of vol/trend regime change), gate-failure lead-time estimation (bars until predicted gate breach), adaptive gate recalibration (tighten EG/ADF/half-life thresholds when regime-transition risk rises), proactive de-risking (zero capacity/weight ahead of predicted breaks), backtested predictive accuracy (precision/recall/F1 of predicted gate failures vs actual), and fail-closed execution halts on predicted breach. Blocks cannot auto-lift; re-entry requires fresh cointegration evidence + regime-stability confirmation. Exclusively use real Binance cached data (1h; resample allowed only if derived from real data). No fabrication.
>
> **REQUIRED DELIVERABLES (ON DISK, VERIFIED):**
> 1. **Generator** `scripts/generate_campaign37_artifacts.py` (complete, `main()`, ruff clean). Load real cached data for all symbols in the 17 pairs. Load Campaign 36 artifact (`reports/cointegration_campaign36_mt.json`) as baseline persistence/decay/failure-rate inputs. Compute regime-transition probabilities, gate-failure lead times, adaptive recalibrated thresholds, proactive de-risking allocations, predictive accuracy metrics (precision/recall/F1), fail-closed re-gating on predicted breach with no auto-lift, and breach-alert-driven kill-switch halts. Attach **full provenance** (source, real_data_only, fabricated_data, computed_at, blocked_routes, rationale), log every computation step, never fabricate values on blocked routes.
> 2. **Artifact** `reports/cointegration_campaign37_mt.json` with per-portfolio, per-regime, per-transition, per-lead-time, per-prediction-accuracy, per-recalibration, per-de-risking, and per-kill-switch-state results. Must include provenance, causal windows (trailing only), gating invariants preserved, regime definitions, transition probability matrices, gate-failure lead-time distributions, adaptive threshold schedules, proactive capacity/weight zeroing, predictive accuracy (precision/recall/F1), kill-switch triggers and halted states on predicted breach, basket cointegration tests, multi-asset hedge ratios, portfolio spreads, execution-aware capacity allocation with breach alerts driving halts. Must be JSON-serializable with **no NaN/Inf**.
> 3. **Tests** `tests/test_cointegration_campaign37_mt.py` asserting schema, required sections/fields/types, minimum portfolio coverage (all 17 pairs represented), real-data provenance on all sections, **gating invariants preserved exactly** (1h 0/17, 4h 1/17 POL/BTC, 1d 0/17), fail-closed regime-transition re-gating (predicted breach → blocked, zero capacity/weight), no auto-lift of blocks, re-entry requires fresh cointegration evidence + regime stability, regime-transition probability quantified, gate-failure lead-time quantified, predictive accuracy quantified (precision/recall/F1), breach alerts present and drive halts when predicted breach, NaN/Inf checks, and campaign flags. **All tests must pass**.
>
> **CONSTRAINTS (NON-NEGOTIABLE):** REAL DATA ONLY. CAUSAL ONLY (trailing windows, no lookahead). PRESERVE GATING INVARIANTS (1h 0/17, 4h 1/17 POL/BTC, 1d 0/17). FAIL-CLOSED. REGIME-TRANSITION RE-GATING RECLASSIFIES PAIRS — NO AUTO-LIFT. RE-ENTRY REQUIRES FRESH COINTEGRATION EVIDENCE + REGIME STABILITY. PROVENANCE MANDATORY ON EVERY COMPUTED SECTION. NO AUTO-LIFT OF BLOCKS. NO FABRICATION. HEAVY MANDATE. BREACH ALERTS REQUIRED ON PREDICTED BREACH AND MUST DRIVE EXECUTION HALTS.
>
> **VERIFICATION (BLOCKING):** `ruff check` clean on touched files; `pytest tests/test_cointegration_campaign37_mt.py -v` passes; Campaign 35-36 tests still green; `pytest tests/ -q` remains green (0 failed).
>
> **RULE:** Do not stop until ALL deliverables exist on disk, all tests pass, and verification commands succeed. No exploration detours. No scope creep. This is the ONLY task.

## IMMEDIATE BOOT SEQUENCE (BLOCKING - DO IN ORDER, NO SKIPPING)
1. **Install deps (BLOCKING):** `python -m pip install -r requirements.txt` — prevent ModuleNotFoundError.
2. **Verify baseline (BLOCKING):** `python -m pytest tests/test_cointegration_campaign36_mt.py -v && python -m pytest tests/ -q` — must remain green (0 failed). Confirm gating invariants: 1h 0/17, 4h 1/17 POL/BTC, 1d 0/17.
3. **Read the law:** Re-read this handoff fully (HARD CONSTRAINTS non-negotiable). Campaign 37 is the **ONLY** permitted focus until complete.
4. **Mirror patterns:** Follow `scripts/generate_campaign35_artifacts.py`, `scripts/generate_campaign36_artifacts.py`, `reports/cointegration_campaign36_mt.json`, `tests/test_cointegration_campaign37_mt.py` patterns. Do **not** re-derive Campaigns 26-36. Load Campaign 36 artifact as input baseline.

## BOTTLENECKS (REMOVED / PREVENTED)
- **BOTTLENECK REMOVED — Stale/ambiguous handoff:** Refreshed to 2026-11-02T23:40:31.000000+00:00 with true on-disk state; Campaign 36 verified complete, Campaign 37 explicitly targeted as the only active focus.
- **BOTTLENECK REMOVED — Scope drift:** Campaign 37 is the **ONLY** permitted focus until complete. Campaigns 26-36 artifacts untouched; Campaign 36 phase 8 not re-derived.
- **BOTTLENECK REMOVED — Gating erosion:** Invariants codified and asserted by tests. Fail-closed enforced; regime-transition re-gating reclassifies pairs, kill-switch halts on predicted breach, no auto-lift.
- **BOTTLENECK REMOVED — Execution path:** Follow proven Campaigns 35-36 patterns (generator → artifact → tests), loading Campaign 36 artifact as baseline.
- **BOTTLENECK REMOVED — CI/env:** Install deps first; baseline verification enforced before coding.
- **BOTTLENECK REMOVED — Coasting:** Heavy mandate, explicit deliverables, blocking verification, no escape clause.
- **BOTTLENECK REMOVED — Ambiguous start:** Single copy/paste initial task message provided. No ramp-up or exploration detours permitted.
- **BOTTLENECK REMOVED — Missing Campaign 37 deliverables:** `scripts/generate_campaign37_artifacts.py`, `reports/cointegration_campaign37_mt.json`, `tests/test_cointegration_campaign37_mt.py` are absent and are the required build targets.
- **BOTTLENECK REMOVED — Blocked sessions / inefficiency:** All bottlenecks identified and eliminated; next agent must proceed directly to Campaign 37 with heavy work, no exploration loops.
- **BOTTLENECK REMOVED — Computational runtime:** Campaign 36 generator optimized with per-bar persistence subsampling stride (1h: 4x, 4h: 2x, 1d: 1x) reducing runtime from >10 min to ~5 min while preserving quantified metrics; Campaign 37 should apply similar stride discipline to stay within session time limits.

## HARD CONSTRAINTS
- **REAL DATA ONLY** — no fabrication. Resample of cached 1h is allowed only if derived from real data.
- **NO WEAKENING THRESHOLDS** without ironclad justification + tests. Gate thresholds unchanged: rolling ≥ 0.6, EG p ≤ 0.05, half-life (1, 500).
- **PRESERVE GREEN** — all existing tests green; ruff clean on touched files.
- **CAUSAL ONLY** — no lookahead. Trailing windows only.
- **HONEST BLOCKING** — blocked pairs receive zero weight/fills/capacity allocation/position limits; full provenance; no forced blocking.
- **FAIL-CLOSED** — capacity/routing/drift/alerting/kill-switch/risk constraints never lift gating blocks. Only gated-eligible pairs can be feasible. Kill-switch halts execution on stress/predicted breach; cannot auto-lift.
- **HEAVY MANDATE** — produce artifacts/tests/logs/provenance. No coasting. If stuck, do more verification/artifacts, not less.
- **INCIDENT DISCIPLINE** — every breach must be logged with cause, containment, and audit trail; no silent remediation.

## VERIFIED STATE (2026-11-02T23:40:31.000000+00:00)
- Branch: `main`. HEAD clean working tree.
- **Campaigns 1-36:** Complete & verified on disk. Full suite green (Campaign 36: 16/16 passed; full suite: 740 passed, 1 skipped). Gating invariants preserved (1h 0/17, 4h 1/17 POL/BTC, 1d 0/17).
- **Campaign 36:** COMPLETE — generator `scripts/generate_campaign36_artifacts.py` (optimized with persistence stride), artifact `reports/cointegration_campaign36_mt.json`, tests `tests/test_cointegration_campaign36_mt.py` all verified green, ruff clean. Cointegration rigor phase 8 done (regime-conditioned gate persistence/decay, forward-reliability/walk-forward gate stability, regime-conditioned failure rates, multi-regime convergence/divergence stress, fail-closed re-gating with no auto-lift, breach-alert-driven kill-switch halts).
- **Campaign 37:** ACTIVE (cointegration rigor phase 9). Deliverables **absent** on disk: `scripts/generate_campaign37_artifacts.py`, `reports/cointegration_campaign37_mt.json`, `tests/test_cointegration_campaign37_mt.py` — build from scratch following Campaigns 35-36 patterns.

## VERIFICATION COMMANDS (RUN OFTEN)
```bash
python -m pip install -r requirements.txt
python -m pytest tests/test_cointegration_campaign36_mt.py -v
python -m pytest tests/ -q
python -m ruff check scripts/generate_campaign37_artifacts.py tests/test_cointegration_campaign37_mt.py
python3 -c "
import json
g=json.load(open('reports/portfolio_gating_mt.json'))['results_by_timeframe']
for tf in ['1h','4h','1d']:
    elig=g[tf].get('eligible_pairs',g[tf].get('feasible_pairs',{}))
    print(tf,'eligible:',len(elig),list(elig.keys()) if isinstance(elig,dict) else elig)
"
```
