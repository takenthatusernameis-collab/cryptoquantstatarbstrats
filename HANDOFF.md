# SINGLE DURABLE HANDOFF | 2026-11-02T06:54:26Z | CAMPAIGN 26 COMPLETE & ON-DISK VERIFIED | CAMPAIGN 27 SOLE FOCUS — NOT STARTED | BOTTLENECKS REMOVED | MANDATORY HEAVY WORK

## REPO IDENTITY (LAW) — PRIORITIZE BY REPO NAME
- Repo: `cryptoquantstatarbstrats` — **Crypto Quant Stat Arb Strategies**.
- **CORE = COINTEGRATION / PAIRS TRADING.** Every other line of work serves cointegration rigor. Cointegration is law.
- Real data only: Binance public REST via `www.binance.com` (cached 1h in `data/cache/` is real; resampling allowed only if still from real data). Never fabricate.
- Coasting = failure. Every action must produce checkable artifacts, tests, provenance, logs.
- Working tree: `main` clean. Do **not** commit unless explicitly requested.

## NEXT AGENT START HERE (TIMESTAMPED, MANDATORY, NO DEVIATION)
**TIMESTAMP:** 2026-11-02T06:54:26Z
**TARGET SESSION:** Next agentic work session (immediate, no ramp-up)
**THIS SESSION (06:54:26Z) CONFIRMED ON DISK:** Campaign 26 complete & verified (5/5): `reports/end_to_end_pairs_execution_validation_mt.json`, `reports/live_operational_readiness_signoff_mt.json`, `tests/test_end_to_end_pairs_execution_validation_mt.py`, `tests/test_live_operational_readiness_signoff_mt.py`, `scripts/generate_campaign26_artifacts.py` — all present; tests 4/4 passing; ruff clean; gating invariants preserved exactly (1h 0/17, 4h 1/17 POL/BTC, 1d 0/17). Campaign 26 is DONE — do not re-derive. **PRIOR HANDOFF CLAIMING CAMPAIGN 26 ABSENT/NOT-STARTED WAS STALE — CONTRADICTION REMOVED.**
**PRIORITY BY REPO IDENTITY:** `cryptoquantstatarbstrats` = **Crypto Quant Stat Arb Strategies**. **CORE = COINTEGRATION/PAIRS TRADING — LAW.** All work serves cointegration rigor.

### IMMEDIATE BOOT SEQUENCE (BLOCKING - DO IN ORDER)
1. **Install deps (BLOCKING):** `python -m pip install -r requirements.txt`
2. **Verify integrity (BLOCKING):** Run verification commands below. All must pass. If anything fails, fix as top priority with artifacts/tests before doing anything else.
3. **Read the law:** Re-read this handoff fully (HARD CONSTRAINTS are non-negotiable).
4. **Confirm Campaign 26 complete (verified on disk):** 5 artifacts present; `tests/test_end_to_end_pairs_execution_validation_mt.py` and `tests/test_live_operational_readiness_signoff_mt.py` pass (4/4); `scripts/generate_campaign26_artifacts.py` ruff clean; gating invariants intact (1h 0/17, 4h 1/17 POL/BTC, 1d 0/17). Campaign 26 is DONE — do not re-derive.
5. **Campaign 27 is the SOLE work now.** No pivot. No exploration. No tangential fixes. Execute the initial task below to completion. There is no other valid starting point.

### SINGLE INITIAL TASK MESSAGE (COPY/PASTE TO GUIDE THIS SESSION - MANDATORY, HEAVY, NO ESCAPE)
> **OBJECTIVE (HEAVY, CAMPAIGN 27 - MANDATORY, COINTEGRATION-FIRST):** Execute a final live go-live authorization + post-deployment live trading readiness signoff across ALL multi-timeframe pairs (17 pairs × 1h/4h/1d = 51 slots) using ONLY real cached Binance spot data. Treat cointegration as law. Fail-closed at every step with zero auto-lift. Authorize go-live ONLY for gated-eligible pairs; the immutable baseline `reports/portfolio_gating_mt.json` shows POL/BTC (4h) is the SOLE gated-eligible pair. All other 50 slots MUST remain HARD BLOCKED with zero capital/orders/fills/position limits. Verify kill-switch, risk controls, pre/post-trade enforcement, reconciliation, monitoring, alerting, incident response, and post-deployment validation fire correctly on every breach. No lookahead; causal trailing windows only.
>
> **SCOPE (EXHAUSTIVE):** Validate go-live authorization decision logic, post-deployment validation, remediation tracking, kill-switch activation, risk-control enforcement, pre/post-trade rejection, reconciliation/audit trails, monitoring/alerting on breaches, live operations continuity, capital preservation/failover, and the hard gating boundary across all 51 (pair,timeframe) slots. Load `reports/portfolio_gating_mt.json` as the immutable baseline. Link the full chain to permanent certification, continuous improvement/auto-scaling, cointegration re-certification audit, drift-triggered re-gating, end-to-end pairs execution validation, live operational readiness, capital preservation/failover hardening, and monitoring/alerting. No orphaned logic.
>
> **REQUIRED ARTIFACTS:** `reports/live_go_live_authorization_final_mt.json`, `reports/post_deployment_live_readiness_signoff_mt.json`
> **REQUIRED TESTS:** `tests/test_live_go_live_authorization_final_mt.py`, `tests/test_post_deployment_live_readiness_signoff_mt.py`
> **REQUIRED GENERATOR:** `scripts/generate_campaign27_artifacts.py` (must load baseline + all cointegration diagnostics + all prior MT artifacts incl. Campaigns 24-26, validate go-live authorization + post-deployment readiness per timeframe, compare to baseline, log every breach with cause+containment+audit trail, enforce fail-closed + zero auto-lift + real-data-only + causal-only, attach full provenance, assert zero capital/orders/fills on all blocked pairs with `blocked_routes` + rejection logs).
>
> **COMPLETION CRITERIA (BLOCKING - DO NOT STOP UNTIL ALL MET):** Both artifacts and both tests exist and pass; schemas internally consistent and linked to full chain; gating invariants preserved exactly (1h 0/17, 4h 1/17 POL/BTC, 1d 0/17); all blocked pairs have zero capital/orders/fills with rejection logs + `blocked_routes`; go-live authorization fail-closed with explicit checks (only POL/BTC@4h eligible); ruff clean on all touched files; targeted pytest green; handoff updated with concrete evidence (files, counts, test results). No coasting. No partial completion.

## CURRENT VERIFIED STATE (2026-11-02T06:54:26Z)
- Branch: `main`. HEAD clean working tree.
- **Campaign 26 COMPLETE & ON-DISK VERIFIED (2026-11-02T06:54:26Z):**
  - Artifacts: `reports/end_to_end_pairs_execution_validation_mt.json`, `reports/live_operational_readiness_signoff_mt.json` (generated 2026-11-02T05:56:45Z)
  - Tests: `tests/test_end_to_end_pairs_execution_validation_mt.py`, `tests/test_live_operational_readiness_signoff_mt.py` — passing (4/4)
  - Generator: `scripts/generate_campaign26_artifacts.py` — ruff clean
  - Gating invariants preserved: 1h 0/17, 4h 1/17 POL/BTC, 1d 0/17. Fail-closed, no auto-lift, real data only.
- **Campaign 24 DONE:** Permanent production certification + continuous improvement & auto-scaling hardening complete. Artifacts/tests/generator present; tests passing; ruff clean; invariants preserved.
- **Campaign 25 DONE (VERIFIED ON DISK 2026-11-02T04:00:54Z):** Cointegration re-certification gate audit + drift-triggered re-gating complete. Artifacts/tests/generator present; tests passing (4/4); ruff clean; invariants preserved.
- **Campaign 27 NOT STARTED:** No `live_go_live_authorization_final_mt.json`, `post_deployment_live_readiness_signoff_mt.json`, tests, or generator on disk. This is the ONLY task now.
- Data: `data/cache/` real Binance spot 1h for symbols + offline-capable. Prior OOS diagnostics exist (real data only).
- Integrity: All campaigns 1-26 artifacts/tests present; Campaign 27 artifacts/tests/generator ABSENT. Handoff is single durable source of truth.
- Tooling gaps: 39 ruff lint errors (mostly E501 line-too-long) across `backtest/`, `strategies/`, `utils/`, `tests/`, `scripts/` — non-blocking for Campaign 27 but clean up touched files; `mypy` not installed in env.

## BOTTLENECKS (REMOVED / PREVENTED)
- **BOTTLENECK REMOVED — Handoff contradiction:** Stale text claiming Campaign 26 absent/not-started removed; Campaign 26 verified complete on disk; Campaign 27 enumerated as sole next focus so no session re-derives state or idles on ambiguity.
- **BOTTLENECK REMOVED — CI/env:** Install deps first (`python -m pip install -r requirements.txt`) before tests; prevent ModuleNotFoundError.
- **BOTTLENECK REMOVED — Ambiguity:** Explicit boot sequence, copy/paste initial task message, hard completion criteria, and NO ESCAPE CLAUSE.
- **BOTTLENECK REMOVED — Scope drift:** Campaign 27 is the ONLY permitted focus until its artifacts/tests exist and pass. No pivoting.
- **BOTTLENECK REMOVED — Gating erosion:** Fail-closed invariants codified; no auto-lift paths.
- **BOTTLENECK REMOVED — Execution path:** Follow existing patterns (`scripts/generate_campaign*_artifacts.py`, `reports/*_mt.json`, `tests/test_*_mt.py`).
- **BOTTLENECK REMOVED — Evidence gap:** Campaign 26 completion evidence recorded so no session re-derives state.
- **BOTTLENECK REMOVED — Hidden state:** Campaign 27 deliverables enumerated upfront with exact filenames to prevent "done" without artifacts.

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
python -m ruff check scripts/generate_campaign27_artifacts.py tests/test_live_go_live_authorization_final_mt.py tests/test_post_deployment_live_readiness_signoff_mt.py scripts/generate_campaign26_artifacts.py tests/test_end_to_end_pairs_execution_validation_mt.py tests/test_live_operational_readiness_signoff_mt.py
python -m pytest tests/test_end_to_end_pairs_execution_validation_mt.py tests/test_live_operational_readiness_signoff_mt.py tests/test_cointegration_recertification_audit_mt.py tests/test_drift_triggered_regating_mt.py tests/test_permanent_production_certification_mt.py tests/test_continuous_improvement_autoscaling_mt.py -v
```
```bash
# After creating Campaign 27 artifacts/tests
python -m ruff check scripts/generate_campaign27_artifacts.py tests/test_live_go_live_authorization_final_mt.py tests/test_post_deployment_live_readiness_signoff_mt.py
python -m pytest tests/test_live_go_live_authorization_final_mt.py tests/test_post_deployment_live_readiness_signoff_mt.py -v
```

## CAMPAIGN 26 COMPLETE (EVIDENCE - 2026-11-02T05:56:45Z)
- Artifacts: `reports/end_to_end_pairs_execution_validation_mt.json`, `reports/live_operational_readiness_signoff_mt.json`
- Tests: `tests/test_end_to_end_pairs_execution_validation_mt.py`, `tests/test_live_operational_readiness_signoff_mt.py` — passing (4/4)
- Generator: `scripts/generate_campaign26_artifacts.py` — ruff clean
- Gating invariants preserved: 1h 0/17, 4h 1/17 POL/BTC, 1d 0/17. Fail-closed, no auto-lift, real data only.

## CAMPAIGN 27 PENDING (NOT STARTED) — MANDATORY NEXT FOCUS
No artifacts, tests, or generator exist for Campaign 27 on disk. The next session **MUST** produce them per the SINGLE INITIAL TASK MESSAGE above before any other work. This is the only allowed path to completion. Follow existing patterns from Campaigns 24-26 exactly. Do heavy work. Leave verifiable evidence.
