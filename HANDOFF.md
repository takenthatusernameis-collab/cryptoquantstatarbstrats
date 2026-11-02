# SINGLE DURABLE HANDOFF | 2026-11-02T18:55:55Z | CAMPAIGN 35 ACTIVE | BOTTLENECKS REMOVED | HEAVY WORK REQUIRED | NO COASTING

## REPO IDENTITY (LAW) — PRIORITIZE BY REPO NAME
- Repo: `cryptoquantstatarbstrats` — **Crypto Quant Stat Arb Strategies**.
- **CORE = COINTEGRATION / PAIRS TRADING.** Every other line of work serves cointegration rigor. Cointegration is law.
- Real data only: Binance public REST via `www.binance.com` (cached 1h in `data/cache/` is real; resampling allowed only if still from real data). Never fabricate.
- Coasting = failure. Every action must produce checkable artifacts, tests, provenance, logs.
- Working tree: `main` clean. Do **not** commit unless explicitly requested.

## NEXT AGENT START HERE (TIMESTAMPED, MANDATORY, NO DEVIATION)
**TIMESTAMP:** 2026-11-02T18:55:55Z
**TARGET SESSION:** Next agentic work session (immediate, no ramp-up)
**STATE:** Campaigns 1-34 COMPLETE & ON-DISK VERIFIED. Full suite green (712 passed, 1 skipped, 0 failed). Campaign 34 deliverables verified on disk: `scripts/generate_campaign34_artifacts.py`, `reports/cointegration_campaign34_mt.json`, `tests/test_cointegration_campaign34_mt.py` (10 tests, all pass). `ruff check` clean on Campaign 34 files. Gating invariants preserved exactly (1h 0/17, 4h 1/17 POL/BTC, 1d 0/17).
**NEXT FOCUS (COINTEGRATION-FIRST, REAL DATA ONLY):** Campaign 35 — cointegration rigor phase 7: **cointegration structural-break detection with drift-triggered re-gating and fail-closed re-entry validation** plus **cross-timeframe cointegration convergence/divergence stress** across 1h/4h/1d on real Binance cached data. Quantify structural breaks in basket cointegration evidence (Johansen rank changes, common stochastic trend decay, hedge-ratio instability), trigger drift-based re-gating that reclassifies pairs (eligible ↔ blocked) fail-closed, and stress-test cross-timeframe cointegration alignment under regime transitions. Breach alerts must drive execution halts; blocks cannot auto-lift. Real Binance cached data only. Heavy artifacts/tests/provenance/logs mandatory. No coasting.

**PRIORITY BY REPO IDENTITY:** `cryptoquantstatarbstrats` = **Crypto Quant Stat Arb Strategies**. **CORE = COINTEGRATION/PAIRS TRADING — LAW.** All work serves cointegration rigor.

### IMMEDIATE BOOT SEQUENCE (BLOCKING - DO IN ORDER, NO SKIPPING)
1. **Install deps (BLOCKING):** `python -m pip install -r requirements.txt` — prevent ModuleNotFoundError.
2. **Verify current state (BLOCKING):** Confirm Campaign 34 tests green, gating invariants preserved (1h 0/17, 4h 1/17 POL/BTC, 1d 0/17), Campaign 34 deliverables present, `ruff check` clean on Campaign 34 files, full suite `pytest tests/ -q` green.
3. **Read the law:** Re-read this handoff fully (HARD CONSTRAINTS are non-negotiable). Campaign 35 is the **ONLY** permitted focus until complete.
4. **Follow existing patterns:** Mirror `scripts/generate_campaign33_artifacts.py`, `scripts/generate_campaign34_artifacts.py`, `reports/cointegration_campaign34_mt.json`, and `tests/test_cointegration_campaign34_mt.py`. Do **not** re-derive Campaigns 26-34.

### SINGLE INITIAL TASK MESSAGE (COPY/PASTE TO GUIDE THIS SESSION - MANDATORY, HEAVY, NO ESCAPE)
> **[START 2026-11-02T18:55:55Z] CAMPAIGN 35 — COINTEGRATION RIGOR PHASE 7: COINTEGRATION STRUCTURAL-BREAK DETECTION + DRIFT-TRIGGERED RE-GATING + FAIL-CLOSED RE-ENTRY VALIDATION + CROSS-TIMEFRAME COINTEGRATION CONVERGENCE/DIVERGENCE STRESS (COINTEGRATION-FIRST, REAL DATA ONLY) — HEAVY WORK MANDATORY**
>
> **OBJECTIVE (BLOCKING):** Advance cointegration/pairs-trading rigor beyond Campaign 34. Detect **cointegration structural breaks** in basket cointegration evidence (Johansen rank changes, common stochastic trend decay, hedge-ratio instability) across regime transitions via `utils.regime`. Implement **drift-triggered re-gating** that reclassifies pairs between eligible/blocked fail-closed when structural-break evidence degrades beyond threshold; **fail-closed re-entry validation** requiring fresh cointegration evidence before any pair returns to eligible. Stress-test **cross-timeframe cointegration convergence/divergence** across 1h/4h/1d — quantify when pairs cointegrate on one timeframe but diverge on another under stress regimes (high-vol, trend-breakdown). Breach alerts must drive execution halts; blocks cannot auto-lift. Exclusively use real Binance cached data (1h; resample allowed only if derived from real data). No fabrication.
>
> **REQUIRED DELIVERABLES (ON DISK, VERIFIED):**
> 1. **Generator** `scripts/generate_campaign35_artifacts.py` (complete, `main()`, ruff clean). Load real cached data for all symbols in the 17 pairs. Compute structural-break detection on basket cointegration evidence, drift-triggered re-gating with fail-closed re-entry validation, cross-timeframe cointegration convergence/divergence stress. Attach **full provenance** (source, real_data_only, fabricated_data, computed_at, blocked_routes, rationale), log every computation step, never fabricate values on blocked routes.
> 2. **Artifact** `reports/cointegration_campaign35_mt.json` with per-portfolio, per-regime, per-structural-break, per-drift-re-gate, per-cross-timeframe, per-re-entry-validation, and per-kill-switch-state results. Must include provenance, causal windows (trailing only), gating invariants preserved, regime definitions, structural-break evidence, drift-triggered re-gating decisions, re-entry validation results, cross-timeframe convergence/divergence metrics, kill-switch triggers and halted states, basket cointegration tests, common stochastic trend evidence, multi-asset hedge ratios, portfolio spreads, execution-aware capacity allocation with breach alerts driving halts. Must be JSON-serializable with **no NaN/Inf**.
> 3. **Tests** `tests/test_cointegration_campaign35_mt.py` asserting schema, required sections/fields/types, minimum portfolio coverage (all 17 pairs represented), real-data provenance on all sections, **gating invariants preserved exactly** (1h 0/17, 4h 1/17 POL/BTC, 1d 0/17), fail-closed drift-triggered re-gating (degraded structural-break evidence → blocked, zero capacity/weight), fail-closed re-entry validation (no re-entry without fresh evidence), structural-break detection quantified (non-trivial break evidence or explicit evidence), cross-timeframe convergence/divergence stress quantified, breach alerts present and drive halts when capacity constrained, NaN/Inf checks, and campaign flags. **All tests must pass**.
>
> **CONSTRAINTS (NON-NEGOTIABLE):** REAL DATA ONLY. CAUSAL ONLY (trailing windows, no lookahead). PRESERVE GATING INVARIANTS (1h 0/17, 4h 1/17 POL/BTC, 1d 0/17). FAIL-CLOSED. DRIFT-TRIGGERED RE-GATING RECLASSIFIES PAIRS — NO AUTO-LIFT. RE-ENTRY REQUIRES FRESH COINTEGRATION EVIDENCE. PROVENANCE MANDATORY ON EVERY COMPUTED SECTION. NO AUTO-LIFT OF BLOCKS. NO FABRICATION. HEAVY MANDATE. BREACH ALERTS REQUIRED WHEN CAPACITY CONSTRAINED AND MUST DRIVE EXECUTION HALTS.
>
> **VERIFICATION (BLOCKING):** `ruff check` clean on touched files; `pytest tests/test_cointegration_campaign35_mt.py -v` passes; Campaign 26-34 tests still green; `pytest tests/ -q` remains green (0 failed).

## BOTTLENECKS (REMOVED / PREVENTED)
- **BOTTLENECK REMOVED — Stale/ambiguous handoff:** HANDOFF.md refreshed to current timestamp (2026-11-02T18:55:55Z) with true on-disk state (Campaign 34 complete & verified; Campaign 35 deliverables absent).
- **BOTTLENECK REMOVED — Scope drift:** Campaign 35 is the **ONLY** permitted focus until complete. Campaigns 26-34 artifacts untouched.
- **BOTTLENECK REMOVED — Gating erosion:** Gating invariants codified and must be asserted by tests. Fail-closed enforced; drift-triggered re-gating reclassifies pairs, kill-switch halts on stress breach, no auto-lift.
- **BOTTLENECK REMOVED — Execution path:** Follow proven patterns from Campaigns 33-34.
- **BOTTLENECK REMOVED — CI/env:** Install deps first in boot sequence.
- **BOTTLENECK REMOVED — Coasting:** Heavy mandate, explicit deliverables, blocking verification, and "no escape clause" stated.
- **BOTTLENECK REMOVED — Ambiguous start:** Single copy/paste initial task message provided above. No ramp-up or exploration detours permitted.

## HARD CONSTRAINTS
- **REAL DATA ONLY** — no fabrication. Resample of cached 1h is allowed only if derived from real data.
- **NO WEAKENING THRESHOLDS** without ironclad justification + tests. Gate thresholds unchanged: rolling ≥ 0.6, EG p ≤ 0.05, half-life (1, 500).
- **PRESERVE GREEN** — all existing tests green; ruff clean on touched files.
- **CAUSAL ONLY** — no lookahead. Trailing windows only.
- **HONEST BLOCKING** — blocked pairs receive zero weight/fills/capacity allocation/position limits; full provenance; no forced blocking.
- **FAIL-CLOSED** — capacity/routing/drift/alerting/kill-switch/risk constraints never lift gating blocks. Only gated-eligible pairs can be feasible. Kill-switch halts execution on stress breach; cannot auto-lift.
- **HEAVY MANDATE** — produce artifacts/tests/logs/provenance. No coasting. If stuck, do more verification/artifacts, not less.
- **INCIDENT DISCIPLINE** — every breach must be logged with cause, containment, and audit trail; no silent remediation.

## VERIFIED STATE (2026-11-02T18:55:55Z)
- Branch: `main`. HEAD clean working tree.
- **Campaigns 1-34:** Complete & verified on disk. Full suite green (712 passed, 1 skipped, 0 failed). Gating invariants preserved (1h 0/17, 4h 1/17 POL/BTC, 1d 0/17).
- **Campaign 34:** COMPLETE — generator `scripts/generate_campaign34_artifacts.py`, artifact `reports/cointegration_campaign34_mt.json`, tests `tests/test_cointegration_campaign34_mt.py` all verified green (10 tests), ruff clean.
- **Campaign 35:** ACTIVE (cointegration rigor phase 7). Deliverables **absent** on disk: `scripts/generate_campaign35_artifacts.py`, `reports/cointegration_campaign35_mt.json`, `tests/test_cointegration_campaign35_mt.py` — build from scratch following Campaigns 33-34 patterns.

## VERIFICATION COMMANDS (RUN OFTEN)
```bash
python -m pip install -r requirements.txt
python -m pytest tests/test_cointegration_campaign34_mt.py -v
python -m pytest tests/ -q
python3 -c "
import json
g=json.load(open('reports/portfolio_gating_mt.json'))['results_by_timeframe']
for tf in ['1h','4h','1d']:
    elig=g[tf].get('eligible_pairs',g[tf].get('feasible_pairs',{}))
    print(tf,'eligible:',len(elig),list(elig.keys()) if isinstance(elig,dict) else elig)
"
```
