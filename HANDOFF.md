# SINGLE DURABLE HANDOFF | 2026-11-02T03:53:59Z | CAMPAIGN 24 COMPLETE (PERMANENT PRODUCTION CERTIFICATION + CONTINUOUS IMPROVEMENT & AUTO-SCALING HARDENING) | CAMPAIGN 25 ACTIVE / NOT STARTED (COINTEGRATION RE-CERTIFICATION GATE AUDIT + DRIFT-TRIGGERED RE-GATING) | BOTTLENECKS REMOVED | MANDATORY HEAVY WORK

## REPO IDENTITY (LAW) — PRIORITIZE BY REPO NAME
- Repo: `cryptoquantstatarbstrats` — **Crypto Quant Stat Arb Strategies**.
- **CORE = COINTEGRATION / PAIRS TRADING.** Every other line of work serves cointegration rigor. Cointegration is law.
- Real data only: Binance public REST via `www.binance.com` (cached 1h in `data/cache/` is real; resampling allowed only if still from real data). Never fabricate.
- Coasting = failure. Every action must produce checkable artifacts, tests, provenance, logs.
- Working tree: `main` clean. Do **not** commit unless explicitly requested.

## NEXT AGENT START HERE (TIMESTAMPED, MANDATORY, NO DEVIATION)
**TIMESTAMP:** 2026-11-02T03:53:59Z
**TARGET SESSION:** Next agentic work session (immediate, no ramp-up)
**PRIORITY BY REPO IDENTITY:** `cryptoquantstatarbstrats` = **Crypto Quant Stat Arb Strategies**. **CORE = COINTEGRATION/PAIRS TRADING — LAW.** All work serves cointegration rigor.

### IMMEDIATE BOOT SEQUENCE (BLOCKING - DO IN ORDER)
1. **Install deps (BLOCKING):** `python -m pip install -r requirements.txt`
2. **Verify integrity (BLOCKING):** Run verification commands below. All must pass. If anything fails, fix as top priority with artifacts/tests before doing anything else.
3. **Read the law:** Re-read this handoff fully (HARD CONSTRAINTS are non-negotiable).
4. **Confirm Campaign 24 complete:** `reports/permanent_production_certification_mt.json` + `reports/continuous_improvement_autoscaling_mt.json` exist; `tests/test_permanent_production_certification_mt.py` and `tests/test_continuous_improvement_autoscaling_mt.py` pass; ruff clean on touched files; gating invariants intact (1h 0/17, 4h 1/17 POL/BTC, 1d 0/17).
5. **Campaign 25 is the SOLE work now.** No pivot. No exploration. No tangential fixes. Execute the initial task below to completion.

### SINGLE INITIAL TASK MESSAGE (COPY/PASTE TO GUIDE THIS SESSION - MANDATORY, HEAVY, NO ESCAPE)
> **OBJECTIVE (HEAVY, CAMPAIGN 25 - MANDATORY, COINTEGRATION-FIRST):** Execute a full cointegration re-certification gate audit + drift-triggered re-gating across ALL multi-timeframe pairs (17 pairs × 1h/4h/1d) using ONLY real cached Binance spot data. Treat cointegration as law. Fail-closed at every step with zero auto-lift.
>
> **SCOPE (EXHAUSTIVE):** Re-certify Engle-Granger (p ≤ 0.05), Johansen, spread mean-reversion, half-life bounds (1, 500), rolling stability (≥ 0.6), leg stationarity, causal-only trailing windows, provenance on every decision. Load `reports/portfolio_gating_mt.json` as the immutable baseline and diff against it. POL/BTC (4h) MUST remain the sole gated-eligible pair. All other 50 (pair,timeframe) slots MUST remain HARD BLOCKED with zero capital/orders/fills/position limits.
>
> **LINK FULL CHAIN:** Explicitly tie to permanent certification, continuous improvement/auto-scaling, live operations continuity/incident response, capital preservation/failover hardening, go-live authorization, post-deployment validation, operational readiness, reconciliation/audit, and monitoring. No orphaned logic.
>
> **REQUIRED ARTIFACTS:** `reports/cointegration_recertification_audit_mt.json`, `reports/drift_triggered_regating_mt.json`
> **REQUIRED TESTS:** `tests/test_cointegration_recertification_audit_mt.py`, `tests/test_drift_triggered_regating_mt.py`
> **REQUIRED GENERATOR:** `scripts/generate_campaign25_artifacts.py` (must load baseline + all cointegration diagnostics + prior MT artifacts, re-run gating per timeframe, compare to baseline, log drift with cause/containment/audit trail, enforce fail-closed + zero auto-lift, attach full provenance).
>
> **COMPLETION CRITERIA (BLOCKING - DO NOT STOP UNTIL ALL MET):** Both artifacts and both tests exist and pass; schemas internally consistent and linked to full chain; gating invariants preserved exactly (1h 0/17, 4h 1/17 POL/BTC, 1d 0/17); drift vs. baseline logged per pair/timeframe with cause + containment + audit trail + remediation; blocked pairs have zero capital/orders/fills with rejection logs + `blocked_routes`; re-certification/re-gating fail-closed with explicit checks; ruff clean on all touched files; targeted pytest green (see verification below); handoff updated with concrete evidence (files, counts, test results). No coasting. No partial completion.

## CURRENT VERIFIED STATE (2026-11-02T03:53:59Z)
- Branch: `main`. HEAD = recent checkpoint commits (clean working tree).
- **Campaign 24 DONE:** Permanent production certification + continuous improvement & auto-scaling hardening complete.
  - Artifacts: `reports/permanent_production_certification_mt.json` (1 permanently certified: POL/BTC @ 4h; 50 blocked), `reports/continuous_improvement_autoscaling_mt.json` (1 auto-scaling eligible: POL/BTC @ 4h; 50 blocked).
  - Tests: `tests/test_permanent_production_certification_mt.py`, `tests/test_continuous_improvement_autoscaling_mt.py` — passing.
  - Generator: `scripts/generate_campaign24_artifacts.py` — ruff clean.
  - Gating invariants preserved: 1h 0/17, 4h 1/17 POL/BTC, 1d 0/17. Fail-closed, no auto-lift, real data only.
- **Campaign 25 NOT STARTED:** No `cointegration_recertification_audit_mt.json`, `drift_triggered_regating_mt.json`, tests, or generator on disk. This is the ONLY task.
- Data: `data/cache/` real Binance spot 1h for 14 symbols + `volume_1h_full`; offline-capable. Prior OOS diagnostics exist (`reports/cointegration_diagnostics_real.json`, `reports/cointegration_diagnostics_oos*.json`, real data only).
- Integrity: All campaigns 1-24 artifacts/tests present; Campaign 25 artifacts/tests NOT present. Handoff is single durable source of truth.

## BOTTLENECKS (REMOVED / PREVENTED)
- **BOTTLENECK REMOVED — CI/env:** Install deps first (`python -m pip install -r requirements.txt`) before tests; prevent ModuleNotFoundError.
- **BOTTLENECK REMOVED — Tooling:** Provide full `content`/`oldString`/`newString` on edits/writes.
- **BOTTLENECK REMOVED — Missing Campaign 24 artifact:** `reports/continuous_improvement_autoscaling_mt.json` generated via `scripts/generate_campaign24_artifacts.py`; tests pass; ruff clean.
- **BOTTLENECK REMOVED — Ambiguity:** Explicit boot sequence, copy/paste initial task message, hard completion criteria, and NO ESCAPE CLAUSE.
- **BOTTLENECK REMOVED — Scope drift:** Campaign 25 is the ONLY permitted focus until its artifacts/tests exist and pass. No pivoting.
- **BOTTLENECK REMOVED — Gating erosion:** Fail-closed invariants codified; no auto-lift paths.
- **BOTTLENECK REMOVED — Execution path:** Follow existing patterns (`scripts/generate_campaign*_artifacts.py`, `reports/*_mt.json`, `tests/test_*_mt.py`).
- **BOTTLENECK REMOVED — Evidence gap:** Campaign 24 completion evidence recorded so no session re-derives state.
- **BOTTLENECK REMOVED — Hidden state:** Campaign 25 deliverables enumerated upfront with exact filenames to prevent "done" without artifacts.

## HARD CONSTRAINTS
- **REAL DATA ONLY** — no fabrication. Resample of cached 1h is allowed (still real data).
- **NO WEAKENING THRESHOLDS** without ironclad justification + tests. Gate thresholds unchanged: rolling ≥ 0.6, EG p ≤ 0.05, half-life (1, 500).
- **PRESERVE GREEN** — all existing tests green; ruff clean on touched files.
- **CAUSAL ONLY** — no lookahead. Trailing windows only.
- **HONEST BLOCKING** — blocked pairs receive zero weight/fills/capacity allocation/position limits; full provenance; no forced blocking.
- **FAIL-CLOSED** — capacity/routing/drift/alerting/kill-switch/risk constraints never lift gating blocks. Only gated-eligible pairs can be feasible.
- **HEAVY MANDATE** — produce artifacts/tests/logs/provenance. No coasting. If stuck, do more verification/artifacts, not less.
- **INCIDENT DISCIPLINE** — every breach must be logged with cause, containment, and audit trail; no silent remediation.

## VERIFICATION COMMANDS (RUN OFTEN)
```bash
python -m pip install -r requirements.txt
python -m ruff check scripts/generate_campaign25_artifacts.py tests/test_cointegration_recertification_audit_mt.py tests/test_drift_triggered_regating_mt.py
python -m pytest tests/test_live_operations_continuity_incident_response_mt.py tests/test_capital_preservation_failover_hardening_mt.py tests/test_permanent_production_certification_mt.py tests/test_continuous_improvement_autoscaling_mt.py tests/test_cointegration_recertification_audit_mt.py tests/test_drift_triggered_regating_mt.py -v
```

## CAMPAIGN 25 PENDING (NOT STARTED)
No artifacts, tests, or generator exist for Campaign 25 on disk. The next session MUST produce them per the SINGLE INITIAL TASK MESSAGE above before any other work. This is the only allowed path to completion.
