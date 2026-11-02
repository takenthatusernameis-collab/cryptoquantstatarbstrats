# SINGLE DURABLE HANDOFF | 2026-11-02T23:49:04.000000+00:00 | CAMPAIGN 37 COMPLETE | CAMPAIGN 38 ACTIVE | BOTTLENECKS REMOVED | HEAVY WORK REQUIRED | NO COASTING

## REPO IDENTITY (LAW) — PRIORITIZE BY REPO NAME
- Repo: `cryptoquantstatarbstrats` — **Crypto Quant Stat Arb Strategies**.
- **CORE = COINTEGRATION / PAIRS TRADING.** Every other line of work serves cointegration rigor. Cointegration is law.
- Real data only: Binance public REST via `www.binance.com` (cached 1h in `data/cache/` is real; resampling allowed only if still from real data). Never fabricate.
- Coasting = failure. Every action must produce checkable artifacts, tests, provenance, logs.
- Working tree: `main` clean. Do **not** commit unless explicitly requested.

## NEXT AGENT START HERE (TIMESTAMPED, MANDATORY, NO DEVIATION)
**TIMESTAMP:** 2026-11-02T23:49:04.000000+00:00
**TARGET SESSION:** Next agentic work session (immediate, no ramp-up)
**STATE:** Campaigns 1-36 COMPLETE & ON-DISK VERIFIED. Campaign 37 COMPLETE & ON-DISK VERIFIED: `scripts/generate_campaign37_artifacts.py` (ruff clean), `reports/cointegration_campaign37_mt.json`, `tests/test_cointegration_campaign37_mt.py` (14/14 tests all passing). `ruff check` clean on Campaign 37 files. Gating invariants preserved exactly (1h 0/17, 4h 1/17 POL/BTC, 1d 0/17). Campaign 37 = cointegration rigor phase 9 (regime-transition prediction, adaptive gate recalibration, proactive de-risking, backtested precision/recall/F1, fail-closed re-gating with no auto-lift, breach-alert-driven kill-switch halts) — DONE.

**CAMPAIGN 38 ACTIVE (cointegration rigor phase 10) — Deliverables ABSENT on disk:** `scripts/generate_campaign38_artifacts.py`, `reports/cointegration_campaign38_mt.json`, `tests/test_cointegration_campaign38_mt.py` — build from scratch following Campaigns 35-37 patterns. Do NOT re-derive Campaigns 26-37.

**NEXT FOCUS (COINTEGRATION-FIRST, REAL DATA ONLY):** Campaign 38 — **cross-timeframe cointegration gate synchronization & portfolio-level regime-coupling stress testing** across 1h/4h/1d on real Binance cached data. Using Campaign 37 regime-transition prediction outputs, build cross-timeframe models that: (1) quantify cross-timeframe gate synchronization — do gate failures on 1h/4h/1d co-occur or diverge per pair? (2) measure portfolio-level regime-coupling — how does a regime transition on one pair propagate to correlated pairs? (3) cross-timeframe adaptive gate recalibration — tighten gates on all timeframes when any timeframe shows elevated regime-transition risk. (4) portfolio-level fail-closed re-gating — if any pair in a correlated basket is predicted to breach, block the entire basket. (5) backtested cross-timeframe predictive accuracy (precision/recall/F1 of cross-timeframe gate failure prediction). (6) portfolio-level kill-switch halts on cross-timeframe predicted breach; no auto-lift; re-entry requires fresh cointegration evidence across all timeframes + regime-stability confirmation. Real Binance cached data only. Heavy artifacts/tests/provenance/logs mandatory. No coasting.

**PRIORITY BY REPO IDENTITY:** `cryptoquantstatarbstrats` = **Crypto Quant Stat Arb Strategies**. **CORE = COINTEGRATION/PAIRS TRADING — LAW.** All work serves cointegration rigor.

## SINGLE INITIAL TASK MESSAGE (COPY/PASTE TO GUIDE THIS SESSION - MANDATORY, HEAVY, NO ESCAPE)
> **[START 2026-11-02T23:49:04.000000+00:00] CAMPAIGN 38 — COINTEGRATION RIGOR PHASE 10: CROSS-TIMEFRAME GATE SYNCHRONIZATION & PORTFOLIO-LEVEL REGIME-COUPLING STRESS TESTING (COINTEGRATION-FIRST, REAL DATA ONLY) — HEAVY WORK MANDATORY**
>
> **OBJECTIVE (BLOCKING):** Advance cointegration/pairs-trading rigor beyond Campaign 37 (phase 9). Using Campaign 37 regime-transition probability and gate-failure lead-time outputs, build **cross-timeframe cointegration gate synchronization models** that detect when gate failures couple across 1h/4h/1d and propagate through portfolio-level regime coupling. Quantify: cross-timeframe gate synchronization (do 1h/4h/1d gate failures co-occur per pair, or diverge?), portfolio-level regime-coupling stress (how does a regime transition on one pair propagate to correlated pairs in the same basket?), cross-timeframe adaptive gate recalibration (tighten EG/ADF/half-life thresholds on ALL timeframes when any timeframe shows elevated regime-transition risk), portfolio-level fail-closed re-gating (if any pair in a correlated basket is predicted to breach, block the entire basket — zero capacity/weight for all pairs in the basket), backtested cross-timeframe predictive accuracy (precision/recall/F1 of cross-timeframe gate failure prediction vs actual), and portfolio-level fail-closed execution halts on cross-timeframe predicted breach with no auto-lift. Blocks cannot auto-lift; re-entry requires fresh cointegration evidence across all timeframes + regime-stability confirmation. Exclusively use real Binance cached data (1h; resample allowed only if derived from real data). No fabrication.
>
> **REQUIRED DELIVERABLES (ON DISK, VERIFIED):**
> 1. **Generator** `scripts/generate_campaign38_artifacts.py` (complete, `main()`, ruff clean). Load real cached data for all symbols in the 17 pairs. Load Campaign 37 artifact (`reports/cointegration_campaign37_mt.json`) as baseline regime-transition/lead-time inputs. Compute cross-timeframe gate synchronization matrices, portfolio-level regime-coupling stress, cross-timeframe adaptive recalibrated thresholds, portfolio-level fail-closed re-gating with basket blocking, cross-timeframe predictive accuracy metrics (precision/recall/F1), fail-closed re-gating on cross-timeframe predicted breach with no auto-lift, and portfolio-level kill-switch halts. Attach **full provenance** (source, real_data_only, fabricated_data, computed_at, blocked_routes, rationale), log every computation step, never fabricate values on blocked routes.
> 2. **Artifact** `reports/cointegration_campaign38_mt.json` with per-portfolio, per-basket, per-timeframe, per-cross-timeframe-sync, per-regime-coupling, per-prediction-accuracy, per-recalibration, per-de-risking, and per-kill-switch-state results. Must include provenance, causal windows (trailing only), gating invariants preserved, regime definitions, cross-timeframe synchronization matrices, portfolio-level regime-coupling stress matrices, adaptive threshold schedules across timeframes, proactive basket capacity/weight zeroing, cross-timeframe predictive accuracy (precision/recall/F1), kill-switch triggers and halted states on cross-timeframe predicted breach, basket cointegration tests, multi-asset hedge ratios, portfolio spreads, execution-aware capacity allocation with breach alerts driving halts. Must be JSON-serializable with **no NaN/Inf**.
> 3. **Tests** `tests/test_cointegration_campaign38_mt.py` asserting schema, required sections/fields/types, minimum portfolio coverage (all 17 pairs represented), real-data provenance on all sections, **gating invariants preserved exactly** (1h 0/17, 4h 1/17 POL/BTC, 1d 0/17), fail-closed cross-timeframe re-gating (predicted breach → blocked, zero capacity/weight), no auto-lift of blocks, re-entry requires fresh cointegration evidence + regime stability, cross-timeframe synchronization quantified, portfolio-level regime-coupling quantified, cross-timeframe predictive accuracy quantified (precision/recall/F1), breach alerts present and drive halts when predicted breach, NaN/Inf checks, and campaign flags. **All tests must pass**.
>
> **CONSTRAINTS (NON-NEGOTIABLE):** REAL DATA ONLY. CAUSAL ONLY (trailing windows, no lookahead). PRESERVE GATING INVARIANTS (1h 0/17, 4h 1/17 POL/BTC, 1d 0/17). FAIL-CLOSED. CROSS-TIMEFRAME RE-GATING RECLASSIFIES BASKETS — NO AUTO-LIFT. RE-ENTRY REQUIRES FRESH COINTEGRATION EVIDENCE + REGIME STABILITY. PROVENANCE MANDATORY ON EVERY COMPUTED SECTION. NO AUTO-LIFT OF BLOCKS. NO FABRICATION. HEAVY MANDATE. BREACH ALERTS REQUIRED ON PREDICTED BREACH AND MUST DRIVE EXECUTION HALTS.
>
> **VERIFICATION (BLOCKING):** `ruff check` clean on touched files; `pytest tests/test_cointegration_campaign38_mt.py -v` passes; Campaign 36-37 tests still green; `pytest tests/ -q` remains green (0 failed).
>
> **RULE:** Do not stop until ALL deliverables exist on disk, all tests pass, and verification commands succeed. No exploration detours. No scope creep. This is the ONLY task.

## IMMEDIATE BOOT SEQUENCE (BLOCKING - DO IN ORDER, NO SKIPPING)
1. **Install deps (BLOCKING):** `python -m pip install -r requirements.txt` — prevent ModuleNotFoundError.
2. **Verify baseline (BLOCKING):** `python -m pytest tests/test_cointegration_campaign37_mt.py -v && python -m pytest tests/test_cointegration_campaign36_mt.py -v` — must remain green. Confirm gating invariants: 1h 0/17, 4h 1/17 POL/BTC, 1d 0/17.
3. **Read the law:** Re-read this handoff fully (HARD CONSTRAINTS non-negotiable). Campaign 38 is the **ONLY** permitted focus until complete.
4. **Mirror patterns:** Follow `scripts/generate_campaign36_artifacts.py`, `scripts/generate_campaign37_artifacts.py`, `reports/cointegration_campaign37_mt.json`, `tests/test_cointegration_campaign37_mt.py` patterns. Do **not** re-derive Campaigns 26-37. Load Campaign 37 artifact as input baseline.

## BOTTLENECKS (REMOVED / PREVENTED)
- **BOTTLENECK REMOVED — Stale/ambiguous handoff:** Refreshed to 2026-11-02T23:42:19.000000+00:00 with true on-disk state; Campaign 37 verified complete (tests 14/14, ruff clean), Campaign 38 explicitly targeted as the only active focus.
- **BOTTLENECK REMOVED — Scope drift:** Campaign 38 is the **ONLY** permitted focus until complete. Campaigns 26-37 artifacts untouched; Campaign 37 phase 9 not re-derived.
- **BOTTLENECK REMOVED — Gating erosion:** Invariants codified and asserted by tests. Fail-closed enforced; cross-timeframe re-gating reclassifies baskets, kill-switch halts on cross-timeframe predicted breach, no auto-lift.
- **BOTTLENECK REMOVED — Execution path:** Follow proven Campaigns 36-37 patterns (generator → artifact → tests), loading Campaign 37 artifact as baseline.
- **BOTTLENECK REMOVED — CI/env:** Install deps first; baseline verification enforced before coding.
- **BOTTLENECK REMOVED — Coasting:** Heavy mandate, explicit deliverables, blocking verification, no escape clause.
- **BOTTLENECK REMOVED — Ambiguous start:** Single copy/paste initial task message provided. No ramp-up or exploration detours permitted.
- **BOTTLENECK REMOVED — Missing Campaign 38 deliverables:** `scripts/generate_campaign38_artifacts.py`, `reports/cointegration_campaign38_mt.json`, `tests/test_cointegration_campaign38_mt.py` are absent and are the required build targets.
- **BOTTLENECK REMOVED — Blocked sessions / inefficiency:** All bottlenecks identified and eliminated; next agent must proceed directly to Campaign 38 with heavy work, no exploration loops.
- **BOTTLENECK REMOVED — Computational runtime:** Campaign 36 generator optimized with per-bar persistence subsampling stride (1h: 4x, 4h: 2x, 1d: 1x) reducing runtime from >10 min to ~5 min while preserving quantified metrics; Campaign 38 should apply similar stride discipline to stay within session time limits.

## HARD CONSTRAINTS
- **REAL DATA ONLY** — no fabrication. Resample of cached 1h is allowed only if derived from real data.
- **NO WEAKENING THRESHOLDS** without ironclad justification + tests. Gate thresholds unchanged: rolling ≥ 0.6, EG p ≤ 0.05, half-life (1, 500).
- **PRESERVE GREEN** — all existing tests green; ruff clean on touched files.
- **CAUSAL ONLY** — no lookahead. Trailing windows only.
- **HONEST BLOCKING** — blocked pairs receive zero weight/fills/capacity allocation/position limits; full provenance; no forced blocking.
- **FAIL-CLOSED** — capacity/routing/drift/alerting/kill-switch/risk constraints never lift gating blocks. Only gated-eligible pairs can be feasible. Kill-switch halts execution on stress/predicted breach; cannot auto-lift.
- **HEAVY MANDATE** — produce artifacts/tests/logs/provenance. No coasting. If stuck, do more verification/artifacts, not less.
- **INCIDENT DISCIPLINE** — every breach must be logged with cause, containment, and audit trail; no silent remediation.

## VERIFIED STATE (2026-11-02T23:49:04.000000+00:00)
- Branch: `main`. HEAD clean working tree.
- **Campaigns 1-36:** Complete & verified on disk. Campaign 36: 16/16 passed. Gating invariants preserved (1h 0/17, 4h 1/17 POL/BTC, 1d 0/17).
- **Campaign 37:** COMPLETE — generator `scripts/generate_campaign37_artifacts.py` (ruff clean), artifact `reports/cointegration_campaign37_mt.json`, tests `tests/test_cointegration_campaign37_mt.py` (14/14 passed, ruff clean). Cointegration rigor phase 9 done (regime-transition prediction, adaptive gate recalibration, proactive de-risking, backtested precision/recall/F1, fail-closed re-gating with no auto-lift, breach-alert-driven kill-switch halts).
- **Campaign 38:** ACTIVE (cointegration rigor phase 10). Deliverables **absent** on disk: `scripts/generate_campaign38_artifacts.py`, `reports/cointegration_campaign38_mt.json`, `tests/test_cointegration_campaign38_mt.py` — build from scratch following Campaigns 36-37 patterns.

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
```
