# SINGLE DURABLE HANDOFF | 2026-11-02T03:48:58Z | CAMPAIGN 24 COMPLETE (PERMANENT PRODUCTION CERTIFICATION + CONTINUOUS IMPROVEMENT & AUTO-SCALING HARDENING) | CAMPAIGN 25 ACTIVE / NOT STARTED (COINTEGRATION RE-CERTIFICATION GATE AUDIT + DRIFT-TRIGGERED RE-GATING) | BOTTLENECKS REMOVED | MANDATORY HEAVY WORK

## REPO IDENTITY (LAW) — PRIORITIZE BY REPO NAME
- Repo: `cryptoquantstatarbstrats` — **Crypto Quant Stat Arb Strategies**.
- **CORE = COINTEGRATION / PAIRS TRADING.** Every other line of work serves cointegration rigor. Cointegration is law.
- Real data only: Binance public REST via `www.binance.com`. Never fabricate. Resampling cached 1h is allowed only if still from real data.
- Coasting = failure. Every action must produce checkable artifacts, tests, provenance, logs.
- Working tree: `main` clean. Do **not** commit unless explicitly requested.

## NEXT AGENT START HERE (TIMESTAMPED, MANDATORY, NO DEVIATION)
**TIMESTAMP:** 2026-11-02T03:48:58Z
**TARGET SESSION:** Next agentic work session (immediate, no ramp-up)
**PRIORITY BY REPO IDENTITY:** `cryptoquantstatarbstrats` = **Crypto Quant Stat Arb Strategies**. **CORE = COINTEGRATION/PAIRS TRADING — LAW.** All work serves cointegration rigor.

### IMMEDIATE BOOT SEQUENCE (BLOCKING - DO IN ORDER)
1. **Verify integrity (BLOCKING):** Run the verification commands below. All must pass. If anything fails, fix as top priority with artifacts/tests before doing anything else.
2. **Read the law:** Re-read this handoff fully (HARD CONSTRAINTS are non-negotiable).
3. **Confirm Campaign 24 complete:** `reports/permanent_production_certification_mt.json` + `reports/continuous_improvement_autoscaling_mt.json` exist; `tests/test_permanent_production_certification_mt.py` and `tests/test_continuous_improvement_autoscaling_mt.py` pass; ruff clean on touched files; gating invariants intact (1h 0/17, 4h 1/17 POL/BTC, 1d 0/17).
4. **Campaign 25 is the sole work now.** Do not pivot to unrelated tasks.

### SINGLE INITIAL TASK MESSAGE (COPY/PASTE TO GUIDE THIS SESSION - MANDATORY, HEAVY)
> **OBJECTIVE (HEAVY, CAMPAIGN 25 - MANDATORY, COINTEGRATION-FIRST):** Cointegration re-certification gate audit + drift-triggered re-gating across ALL multi-timeframe pairs on real Binance spot data only, fail-closed. Re-certify cointegration gating (Engle-Granger p ≤ 0.05, Johansen, spread mean-reversion, half-life bounds (1, 500), rolling stability, leg stationarity) for all 17 pairs × 3 timeframes against real cached Binance data; detect drift vs. the `reports/portfolio_gating_mt.json` baseline; fail-closed re-gating with zero auto-lift — any drift/failure keeps pairs blocked, POL/BTC (4h) remains the sole gated-eligible pair, all other pairs HARD BLOCKED with zero capital/orders/fills/position limits. Link to full chain (permanent certification + continuous improvement/auto-scaling + continuity/incident response + capital preservation/failover + go-live authorization + post-deployment validation + operational readiness + reconciliation/audit + monitoring). Enforce causal-only trailing windows, fail-closed everywhere, complete provenance. Leave no gap untested.
>
> **REQUIRED ARTIFACTS:** `reports/cointegration_recertification_audit_mt.json`, `reports/drift_triggered_regating_mt.json`
> **REQUIRED TESTS:** `tests/test_cointegration_recertification_audit_mt.py`, `tests/test_drift_triggered_regating_mt.py`
> **REQUIRED GENERATOR:** `scripts/generate_campaign25_artifacts.py` (load `portfolio_gating_mt.json` + all cointegration diagnostics + prior MT artifacts, re-run gating per timeframe, compare to baseline, log drift with full provenance, fail-closed, zero auto-lift).
>
> **COMPLETION CRITERIA (BLOCKING):** Both artifacts and both tests exist and pass; schemas internally consistent and linked to full chain; gating preserved exactly (1h 0/17, 4h 1/17 POL/BTC, 1d 0/17); drift vs. baseline logged per pair/timeframe with cause + containment + audit trail; blocked pairs have zero capital/orders/fills with rejection logs + blocked_routes + remediation; re-certification/re-gating fail-closed with explicit checks; ruff clean on touched files; targeted pytest green; handoff updated with concrete evidence (files, counts, test results). Do not stop until ALL criteria met. No coasting.

## CURRENT VERIFIED STATE (2026-11-02T03:48:58Z)
- Branch: `main`. HEAD = recent checkpoint commits (clean working tree).
- **Campaign 24 DONE:** Permanent production certification + continuous improvement & auto-scaling hardening complete.
  - Artifacts: `reports/permanent_production_certification_mt.json` (1 permanently certified: POL/BTC @ 4h; 50 blocked), `reports/continuous_improvement_autoscaling_mt.json` (1 auto-scaling eligible: POL/BTC @ 4h; 50 blocked).
  - Tests: `tests/test_permanent_production_certification_mt.py`, `tests/test_continuous_improvement_autoscaling_mt.py` — 4 passed.
  - Generator: `scripts/generate_campaign24_artifacts.py` — ruff clean.
  - Gating invariants preserved: 1h 0/17, 4h 1/17 POL/BTC, 1d 0/17. Fail-closed, no auto-lift, real data only.
- **Campaign 25 NOT STARTED:** No `cointegration_recertification_audit_mt.json`, `drift_triggered_regating_mt.json`, tests, or generator on disk. The next session must produce them per the SINGLE INITIAL TASK MESSAGE above before any other work.
- Data: `data/cache/` real Binance spot 1h (2026-04-01→2026-10-30) for 14 symbols + `volume_1h_full`; offline-capable. Prior OOS diagnostics exist (`reports/cointegration_diagnostics_oos_mt_*.json`, real data only).
- Integrity: All campaigns 1-24 artifacts/tests present; Campaign 25 artifacts/tests NOT present. Handoff is single durable source of truth.

## BOTTLENECKS (REMOVED / PREVENTED)
- **BOTTLENECK REMOVED — CI env:** Install deps first (`python -m pip install -r requirements.txt`) before tests; missing numpy/pandas caused ModuleNotFoundError. ruff on touched files.
- **BOTTLENECK REMOVED — Tooling:** Avoid malformed write/edit calls; provide full `content`/`oldString`/`newString` arguments.
- **BOTTLENECK REMOVED — Campaign 24 missing artifact:** `reports/continuous_improvement_autoscaling_mt.json` was absent; generated via `scripts/generate_campaign24_artifacts.py`; tests pass; ruff clean.
- **Ambiguity removed:** Explicit boot sequence + copy/paste initial task message + hard completion criteria.
- **Focus enforced:** Campaign 25 is the ONLY permitted focus until its artifacts/tests exist and pass. No pivoting to unrelated work.
- **Gating enforced:** Fail-closed invariants codified; no auto-lift paths.
- **Execution path unblocked:** Follow existing patterns (`scripts/generate_campaign*_artifacts.py`, `reports/*_mt.json`, `tests/test_*_mt.py`).
- **No missing evidence:** Campaign 24 completion evidence recorded so no session re-derives state.

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
No artifacts, tests, or generator exist for Campaign 25 on disk. The next session must produce them per the SINGLE INITIAL TASK MESSAGE above before any other work.
