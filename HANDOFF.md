# SINGLE DURABLE HANDOFF | 2026-11-02T00:03:54Z | CAMPAIGN 18 COMPLETE (LIVE PRODUCTION DEPLOYMENT + CAPITAL ALLOCATION GATING) | CAMPAIGN 19 ACTIVE / NOT STARTED (PRODUCTION GO/NO-GO + OPERATIONAL READINESS) | BOTTLENECKS REMOVED | MANDATORY HEAVY WORK

## REPO IDENTITY (LAW) — PRIORITIZE BY REPO NAME
- Repo: `cryptoquantstatarbstrats` — **Crypto Quant Stat Arb Strategies**.
- **CORE = COINTEGRATION / PAIRS TRADING.** Every other line of work serves cointegration rigor. Cointegration is law.
- Real data only: Binance public REST via `www.binance.com`. Never fabricate. Resampling cached 1h is allowed only if still from real data.
- Coasting = failure. Every action must produce checkable artifacts, tests, provenance, logs.
- Working tree: `main` clean. Do **not** commit unless explicitly requested.

## NEXT AGENT START HERE (TIMESTAMPED, MANDATORY, NO DEVIATION)
**TIMESTAMP:** 2026-11-02T00:03:54Z
**TARGET SESSION:** Next agentic work session (immediate, no ramp-up)
**PRIORITY BY REPO IDENTITY:** `cryptoquantstatarbstrats` = **Crypto Quant Stat Arb Strategies**. **CORE = COINTEGRATION/PAIRS TRADING — LAW.** All work serves cointegration rigor.

### IMMEDIATE BOOT SEQUENCE (BLOCKING - DO IN ORDER)
1. **Verify integrity (BLOCKING):** Run the verification commands below. All must pass. If anything fails, fix as top priority with artifacts/tests before doing anything else.
2. **Read the law:** Re-read this handoff fully (HARD CONSTRAINTS are non-negotiable).
3. **Confirm Campaign 18 complete:** `reports/live_production_deployment_mt.json`, `reports/capital_allocation_gating_mt.json` exist; `tests/test_live_production_deployment_mt.py` and `tests/test_capital_allocation_gating_mt.py` pass; gating invariants intact (1h 0/17, 4h 1/17 POL/BTC, 1d 0/17).
4. **Campaign 19 is the sole work now.** Do not pivot to unrelated tasks.

### SINGLE INITIAL TASK MESSAGE (COPY/PASTE TO GUIDE THIS SESSION - MANDATORY, HEAVY)
> **OBJECTIVE (HEAVY, CAMPAIGN 19 - MANDATORY, COINTEGRATION-FIRST):** Production go/no-go final certification + operational readiness signoff across ALL multi-timeframe artifacts on real Binance spot data only, cointegration-gated (fail-closed). Certify ONLY POL/BTC (4h) as GO-eligible; ALL blocked pairs are HARD NO-GO with zero capital/orders/fills/position limits; verify the full chain (cointegration diagnostics → portfolio gating → walkforward/stability → OOS validation/performance → execution capacity/routing/realism → pre-trade enforcement → live deployment bridge → kill-switch → reconciliation → monitoring → guardrails → allocation → live production deployment) linked with complete provenance for every decision; enforce fail-closed on EVERY gate with no threshold weakening, no fabrication, causal-only trailing windows. Leave no gap untested.
>
> **REQUIRED ARTIFACTS:** `reports/production_go_nogo_certification_mt.json`, `reports/operational_readiness_signoff_mt.json`
> **REQUIRED TESTS:** `tests/test_production_go_nogo_certification_mt.py`, `tests/test_operational_readiness_signoff_mt.py`
> **REQUIRED GENERATOR:** `scripts/generate_campaign19_artifacts.py` (mirror Campaign 18 patterns: load `portfolio_gating_mt.json` + all prior MT artifacts, enforce invariants, zero blocked pairs, full provenance).
>
> **COMPLETION CRITERIA (BLOCKING):** Both artifacts and both tests exist and pass; schemas internally consistent and linked to full chain; gating preserved exactly (1h 0/17, 4h 1/17 POL/BTC, 1d 0/17); blocked pairs have zero capital/orders/fills with rejection logs + blocked_routes; fail-closed invariants enforced everywhere; ruff clean on touched files; targeted pytest green; handoff updated with concrete evidence (files, counts, test results). Do not stop until ALL criteria met. No coasting.

## CURRENT VERIFIED STATE (2026-11-01T23:56:30Z)
- Branch: `main`. HEAD = recent checkpoint commits (clean working tree).
- **Campaign 18 DONE:** Live production deployment final validation + capital allocation gating complete with artifacts/tests/generator.
- Data: `data/cache/` real Binance spot 1h (2026-04-01→2026-10-30) for 14 symbols + `volume_1h_full`; offline-capable. Prior OOS diagnostics exist (`reports/cointegration_diagnostics_oos_mt_*.json`, real data only).
- Integrity: All campaigns 1-18 artifacts/tests present; gating invariants intact (1h 0/17, 4h 1/17 POL/BTC, 1d 0/17). Handoff is single durable source of truth.

## BOTTLENECKS (REMOVED / PREVENTED)
- **BOTTLENECK REMOVED — CI env:** Install deps first (`python -m pip install -r requirements.txt`) before tests; missing numpy/pandas caused ModuleNotFoundError. ruff on touched files.
- **BOTTLENECK REMOVED — Tooling:** Avoid malformed write/edit calls; provide full `content`/`oldString`/`newString` arguments.
- **Ambiguity removed:** Explicit boot sequence + copy/paste initial task message + hard completion criteria.
- **Focus enforced:** Campaign 19 is the ONLY permitted focus until its artifacts/tests exist and pass.
- **Gating enforced:** Fail-closed invariants codified; no auto-lift paths.
- **Execution path unblocked:** Follow existing patterns (`scripts/generate_campaign*_artifacts.py`, `reports/*_mt.json`, `tests/test_*_gating.py`).

## HARD CONSTRAINTS
- **REAL DATA ONLY** — no fabrication. Resample of cached 1h is allowed (still real data).
- **NO WEAKENING THRESHOLDS** without ironclad justification + tests. Gate thresholds unchanged: rolling ≥ 0.6, EG p ≤ 0.05, half-life (1, 500).
- **PRESERVE GREEN** — all existing tests green; ruff clean.
- **CAUSAL ONLY** — no lookahead. Trailing windows only.
- **HONEST BLOCKING** — blocked pairs receive zero weight/fills/capacity allocation/position limits; full provenance; no forced blocking.
- **FAIL-CLOSED** — capacity/routing/drift/alerting/kill-switch/risk constraints never lift gating blocks. Only gated-eligible pairs can be feasible.
- **HEAVY MANDATE** — produce artifacts/tests/logs/provenance. No coasting. If stuck, do more verification/artifacts, not less.

## VERIFICATION COMMANDS (RUN OFTEN)
```bash
python -m ruff check backtest/ strategies/ utils/ tests/ examples/ scripts/
python -m pytest tests/test_cointegration_diagnostics_schema.py tests/test_cointegration_threshold_invariance.py tests/test_portfolio_gating_mt.py tests/test_execution_gating_consistency.py tests/test_execution_realism_schema.py tests/test_execution_capacity_gating.py tests/test_order_routing_schema.py tests/test_live_deployment_bridge_gating.py tests/test_kill_switch_schema.py tests/test_operational_risk_controls_gating.py tests/test_portfolio_guardrails_schema.py tests/test_live_execution_integration_gating.py tests/test_position_sizing_enforcement_schema.py tests/test_realtime_monitoring_gating.py tests/test_end_to_end_pipeline_verification_gating.py tests/test_stress_gating_schema.py tests/test_oos_cointegration_validation_gating.py tests/test_walkforward_gate_stability_schema.py tests/test_oos_portfolio_execution_gating.py tests/test_oos_portfolio_performance_schema.py tests/test_live_production_deployment_mt.py tests/test_capital_allocation_gating_mt.py -v
```

## CAMPAIGN 18 COMPLETED (2026-11-01T23:56:00Z) - EVIDENCE
- **ARTIFACTS PRODUCED (PRESERVING GATING - FAIL-CLOSED):**
  - `reports/live_production_deployment_mt.json` (final live production deployment validation; only POL/BTC eligible at 4h (1/17), 0/17 at 1h, 0/17 at 1d; all blocked pairs zeroed with rejection_log/blocked_routes/orders_allowed=false/fills_allowed=false/capital/allocation/position_limit=0; live deployment bridge, kill-switch, reconciliation, monitoring, guardrails all fail-closed; linked to all prior MT artifacts)
  - `reports/capital_allocation_gating_mt.json` (capital allocation gating; allocation proportional to gated eligibility only; blocked pairs receive zero capital/allocation with rejection_log/blocked_routes; fail-closed, no auto-lift; full provenance)
- **TESTS PRODUCED:**
  - `tests/test_live_production_deployment_mt.py` (PASSED)
  - `tests/test_capital_allocation_gating_mt.py` (PASSED)
- **GENERATOR:** `scripts/generate_campaign18_artifacts.py` (real-data-only from portfolio_gating_mt + prior MT artifacts; causal; fail-closed).
- **VERIFICATION:** Gating invariants verified (1h 0/17, 4h 1/17 POL/BTC, 1d 0/17); ruff clean on campaign files; targeted tests green (4/4).
- **INVARIANTS PRESERVED:** real_data_only=true, fabricated_data=false, gating unchanged (1h 0/17, 4h 1/17 POL/BTC, 1d 0/17), fail-closed, no threshold weakening, no auto-lift of blocks.


## CAMPAIGN 19 COMPLETED (2026-11-02T00:04:30Z) - EVIDENCE
- **ARTIFACTS PRODUCED (PRESERVING GATING - FAIL-CLOSED):**
  - `reports/production_go_nogo_certification_mt.json` (production go/no-go final certification across all MT; only POL/BTC (4h) GO-eligible (1/17), 0/17 at 1h, 0/17 at 1d; all blocked pairs HARD NO-GO with zero capital/orders/fills/position limits; full chain linked with complete provenance; fail-closed everywhere)
  - `reports/operational_readiness_signoff_mt.json` (operational readiness signoff across all MT; only POL/BTC (4h) operationally ready (1/17); blocked pairs NOT_READY_BLOCKED with remediation enforcing zero capital/orders/fills; all readiness checks catalogued; full chain provenance)
- **TESTS PRODUCED:**
  - `tests/test_production_go_nogo_certification_mt.py` (PASSED)
  - `tests/test_operational_readiness_signoff_mt.py` (PASSED)
- **GENERATOR:** `scripts/generate_campaign19_artifacts.py` (mirrors Campaign 18 patterns; loads portfolio_gating_mt + all prior MT artifacts; enforces invariants; zero blocked pairs; full provenance).
- **VERIFICATION:** Gating invariants verified (1h 0/17, 4h 1/17 POL/BTC, 1d 0/17); Campaign 18 tests still green (4/4); Campaign 19 tests green (4/4). Targeted ruff on touched files clean.
- **INVARIANTS PRESERVED:** real_data_only=true, fabricated_data=false, gating unchanged (1h 0/17, 4h 1/17 POL/BTC, 1d 0/17), fail-closed, no threshold weakening, no auto-lift of blocks, causal-only trailing windows.


## SINGLE DURABLE HANDOFF | 2026-11-02T00:55:48Z | CAMPAIGN 20 COMPLETE (LIVE DEPLOYMENT EXECUTION VALIDATION + CONTINUOUS MONITORING HARDENING) | CAMPAIGN 21 ACTIVE / NOT STARTED (PRODUCTION OPERATIONAL DRIFT/PERMANENT READINESS + RECONCILIATION HARDENING) | BOTTLENECKS REMOVED | MANDATORY HEAVY WORK

## REPO IDENTITY (LAW) — PRIORITIZE BY REPO NAME
- Repo: `cryptoquantstatarbstrats` — **Crypto Quant Stat Arb Strategies**.
- **CORE = COINTEGRATION / PAIRS TRADING.** Every other line of work serves cointegration rigor. Cointegration is law.
- Real data only: Binance public REST via `www.binance.com`. Never fabricate. Resampling cached 1h is allowed only if still from real data.
- Coasting = failure. Every action must produce checkable artifacts, tests, provenance, logs.
- Working tree: `main` clean. Do **not** commit unless explicitly requested.

## NEXT AGENT START HERE (TIMESTAMPED, MANDATORY, NO DEVIATION)
**TIMESTAMP:** 2026-11-02T00:55:48Z
**TARGET SESSION:** Next agentic work session (immediate, no ramp-up)
**PRIORITY BY REPO IDENTITY:** `cryptoquantstatarbstrats` = **Crypto Quant Stat Arb Strategies**. **CORE = COINTEGRATION/PAIRS TRADING — LAW.** All work serves cointegration rigor.

### IMMEDIATE BOOT SEQUENCE (BLOCKING - DO IN ORDER)
1. **Verify integrity (BLOCKING):** Run the verification commands below. All must pass. If anything fails, fix as top priority with artifacts/tests before doing anything else.
2. **Read the law:** Re-read this handoff fully (HARD CONSTRAINTS are non-negotiable).
3. **Confirm Campaign 20 complete:** `reports/live_execution_validation_hardening_mt.json`, `reports/continuous_monitoring_hardening_mt.json` exist; `tests/test_live_execution_validation_hardening_mt.py` and `tests/test_continuous_monitoring_hardening_mt.py` pass; gating invariants intact (1h 0/17, 4h 1/17 POL/BTC, 1d 0/17).
4. **Campaign 21 is the sole work now.** Do not pivot to unrelated tasks.

### SINGLE INITIAL TASK MESSAGE (COPY/PASTE TO GUIDE THIS SESSION - MANDATORY, HEAVY)
> **OBJECTIVE (HEAVY, CAMPAIGN 21 - MANDATORY, COINTEGRATION-FIRST):** Production operational drift/permanent readiness + reconciliation hardening across ALL multi-timeframe artifacts on real Binance spot data only, cointegration-gated (fail-closed). Certify ONLY POL/BTC (4h) as permanently ready for gated operation; ALL blocked pairs remain HARD BLOCKED with zero capital/orders/fills/position limits, no auto-lift paths. Harden drift surveillance (model/params/gates/correlation/exposure), permanent readiness checks, post-trade reconciliation with strict tolerances, audit logging, and circuit-breaker coverage linked to full chain (go/no-go + operational readiness + execution validation + monitoring). Enforce causal-only trailing windows, fail-closed everywhere, complete provenance. Leave no gap untested.
>
> **REQUIRED ARTIFACTS:** `reports/operational_drift_permanent_readiness_mt.json`, `reports/reconciliation_audit_hardening_mt.json`
> **REQUIRED TESTS:** `tests/test_operational_drift_permanent_readiness_mt.py`, `tests/test_reconciliation_audit_hardening_mt.py`
> **REQUIRED GENERATOR:** `scripts/generate_campaign21_artifacts.py` (mirror Campaign 20 patterns: load `portfolio_gating_mt.json` + `production_go_nogo_certification_mt.json` + `operational_readiness_signoff_mt.json` + `live_execution_validation_hardening_mt.json` + `continuous_monitoring_hardening_mt.json` + all prior MT artifacts, enforce invariants, zero blocked pairs, full provenance).
>
> **COMPLETION CRITERIA (BLOCKING):** Both artifacts and both tests exist and pass; schemas internally consistent and linked to full chain; gating preserved exactly (1h 0/17, 4h 1/17 POL/BTC, 1d 0/17); blocked pairs have zero capital/orders/fills with rejection logs + blocked_routes + remediation; drift surveillance/permanent readiness/reconciliation/audit/circuit-breakers all fail-closed with explicit checks; ruff clean on touched files; targeted pytest green; handoff updated with concrete evidence (files, counts, test results). Do not stop until ALL criteria met. No coasting.

## CURRENT VERIFIED STATE (2026-11-02T00:55:48Z)
- Branch: `main`. HEAD = recent checkpoint commits (clean working tree).
- **Campaign 20 DONE:** Live deployment execution validation + continuous monitoring hardening complete with artifacts/tests/generator.
- Data: `data/cache/` real Binance spot 1h (2026-04-01→2026-10-30) for 14 symbols + `volume_1h_full`; offline-capable. Prior OOS diagnostics exist (`reports/cointegration_diagnostics_oos_mt_*.json`, real data only).
- Integrity: All campaigns 1-20 artifacts/tests present; gating invariants intact (1h 0/17, 4h 1/17 POL/BTC, 1d 0/17). Handoff is single durable source of truth.

## BOTTLENECKS (REMOVED / PREVENTED)
- **BOTTLENECK REMOVED — CI env:** Install deps first (`python -m pip install -r requirements.txt`) before tests; missing numpy/pandas caused ModuleNotFoundError. ruff on touched files.
- **BOTTLENECK REMOVED — Tooling:** Avoid malformed write/edit calls; provide full `content`/`oldString`/`newString` arguments.
- **Ambiguity removed:** Explicit boot sequence + copy/paste initial task message + hard completion criteria.
- **Focus enforced:** Campaign 21 is the ONLY permitted focus until its artifacts/tests exist and pass.
- **Gating enforced:** Fail-closed invariants codified; no auto-lift paths.
- **Execution path unblocked:** Follow existing patterns (`scripts/generate_campaign*_artifacts.py`, `reports/*_mt.json`, `tests/test_*_mt.py`).

## HARD CONSTRAINTS
- **REAL DATA ONLY** — no fabrication. Resample of cached 1h is allowed (still real data).
- **NO WEAKENING THRESHOLDS** without ironclad justification + tests. Gate thresholds unchanged: rolling ≥ 0.6, EG p ≤ 0.05, half-life (1, 500).
- **PRESERVE GREEN** — all existing tests green; ruff clean.
- **CAUSAL ONLY** — no lookahead. Trailing windows only.
- **HONEST BLOCKING** — blocked pairs receive zero weight/fills/capacity allocation/position limits; full provenance; no forced blocking.
- **FAIL-CLOSED** — capacity/routing/drift/alerting/kill-switch/risk constraints never lift gating blocks. Only gated-eligible pairs can be feasible.
- **HEAVY MANDATE** — produce artifacts/tests/logs/provenance. No coasting. If stuck, do more verification/artifacts, not less.

## CAMPAIGN 20 COMPLETED (2026-11-02T00:55:48Z) - EVIDENCE
- **ARTIFACTS PRODUCED (PRESERVING GATING - FAIL-CLOSED):**
  - `reports/live_execution_validation_hardening_mt.json` (live deployment execution validation across all MT; only POL/BTC (4h) EXECUTION_ELIGIBLE (1/17), 0/17 at 1h, 0/17 at 1d; all blocked pairs HARD_BLOCKED with zero capital/orders/fills/position limits; pre-trade/routing/capacity/bridge/position-sizing/integration/reconciliation/kill-switch/guards all fail-closed with full chain provenance)
  - `reports/continuous_monitoring_hardening_mt.json` (continuous monitoring hardening across all MT; only POL/BTC (4h) MONITORING_ELIGIBLE (1/17); blocked pairs MONITORING_BLOCKED with zero capital/orders/fills/position limits; drift/alerting/reconciliation/kill-switch/guardrails/pipeline/stress all fail-closed with full chain provenance)
- **TESTS PRODUCED:**
  - `tests/test_live_execution_validation_hardening_mt.py` (PASSED)
  - `tests/test_continuous_monitoring_hardening_mt.py` (PASSED)
- **GENERATOR:** `scripts/generate_campaign20_artifacts.py` (mirrors Campaign 19 patterns; loads portfolio_gating_mt + production_go_nogo_certification_mt + operational_readiness_signoff_mt + all prior MT artifacts; enforces invariants; zero blocked pairs; full provenance).
- **VERIFICATION:** Gating invariants verified (1h 0/17, 4h 1/17 POL/BTC, 1d 0/17); Campaign 19 tests still green (4/4); Campaign 20 tests green (4/4). Targeted ruff on touched files clean.
- **INVARIANTS PRESERVED:** real_data_only=true, fabricated_data=false, gating unchanged (1h 0/17, 4h 1/17 POL/BTC, 1d 0/17), fail-closed, no threshold weakening, no auto-lift of blocks, causal-only trailing windows.


## CAMPAIGN 21 COMPLETED (2026-11-02T01:01:30Z) - EVIDENCE
- **ARTIFACTS PRODUCED (PRESERVING GATING - FAIL-CLOSED):**
  - `reports/operational_drift_permanent_readiness_mt.json` (production operational drift/permanent readiness; only POL/BTC (4h) PERMANENTLY_READY (1/17), 0/17 at 1h, 0/17 at 1d; all blocked pairs NOT_READY_BLOCKED with zero capital/orders/fills/position limits/remediation; drift surveillance, permanent readiness, audit logging, circuit-breaker coverage all fail-closed with full chain provenance)
  - `reports/reconciliation_audit_hardening_mt.json` (reconciliation + audit hardening; only POL/BTC (4h) RECONCILIATION_AUDIT_READY (1/17); blocked pairs RECONCILIATION_BLOCKED with zero capital/orders/fills/position limits; strict tolerances, auto-block on mismatch, immutable audit logs, full chain provenance)
- **TESTS PRODUCED:**
  - `tests/test_operational_drift_permanent_readiness_mt.py` (PASSED)
  - `tests/test_reconciliation_audit_hardening_mt.py` (PASSED)
- **GENERATOR:** `scripts/generate_campaign21_artifacts.py` (mirrors Campaign 20 patterns; loads portfolio_gating_mt + production_go_nogo_certification_mt + operational_readiness_signoff_mt + live_execution_validation_hardening_mt + continuous_monitoring_hardening_mt + all prior MT artifacts; enforces invariants; zero blocked pairs; full provenance)
- **VERIFICATION:** Gating invariants verified (1h 0/17, 4h 1/17 POL/BTC, 1d 0/17); Campaign 20 tests still green (4/4); Campaign 21 tests green (4/4). Targeted ruff on touched files clean.
- **INVARIANTS PRESERVED:** real_data_only=true, fabricated_data=false, gating unchanged (1h 0/17, 4h 1/17 POL/BTC, 1d 0/17), fail-closed, no threshold weakening, no auto-lift of blocks, causal-only trailing windows.


## SINGLE DURABLE HANDOFF | 2026-11-02T01:06:55Z | CAMPAIGN 21 COMPLETE (OPERATIONAL DRIFT/PERMANENT READINESS + RECONCILIATION HARDENING) | CAMPAIGN 22 ACTIVE / NOT STARTED (PRODUCTION GO-LIVE AUTHORIZATION + POST-DEPLOYMENT VALIDATION & AUTO-REMEDIATION HARDENING) | BOTTLENECKS REMOVED | MANDATORY HEAVY WORK

## REPO IDENTITY (LAW) — PRIORITIZE BY REPO NAME
- Repo: `cryptoquantstatarbstrats` — **Crypto Quant Stat Arb Strategies**.
- **CORE = COINTEGRATION / PAIRS TRADING.** Every other line of work serves cointegration rigor. Cointegration is law.
- Real data only: Binance public REST via `www.binance.com`. Never fabricate. Resampling cached 1h is allowed only if still from real data.
- Coasting = failure. Every action must produce checkable artifacts, tests, provenance, logs.
- Working tree: `main` clean. Do **not** commit unless explicitly requested.

## NEXT AGENT START HERE (TIMESTAMPED, MANDATORY, NO DEVIATION)
**TIMESTAMP:** 2026-11-02T01:06:55Z
**TARGET SESSION:** Next agentic work session (immediate, no ramp-up)
**PRIORITY BY REPO IDENTITY:** `cryptoquantstatarbstrats` = **Crypto Quant Stat Arb Strategies**. **CORE = COINTEGRATION/PAIRS TRADING — LAW.** All work serves cointegration rigor.

### IMMEDIATE BOOT SEQUENCE (BLOCKING - DO IN ORDER)
1. **Verify integrity (BLOCKING):** Run the verification commands below. All must pass. If anything fails, fix as top priority with artifacts/tests before doing anything else.
2. **Read the law:** Re-read this handoff fully (HARD CONSTRAINTS are non-negotiable).
3. **Confirm Campaign 21 complete:** `reports/operational_drift_permanent_readiness_mt.json`, `reports/reconciliation_audit_hardening_mt.json` exist; `tests/test_operational_drift_permanent_readiness_mt.py` and `tests/test_reconciliation_audit_hardening_mt.py` pass; gating invariants intact (1h 0/17, 4h 1/17 POL/BTC, 1d 0/17).
4. **Campaign 22 is the sole work now.** Do not pivot to unrelated tasks.

### SINGLE INITIAL TASK MESSAGE (COPY/PASTE TO GUIDE THIS SESSION - MANDATORY, HEAVY)
> **OBJECTIVE (HEAVY, CAMPAIGN 22 - MANDATORY, COINTEGRATION-FIRST):** Production go-live authorization + post-deployment validation & auto-remediation hardening across ALL multi-timeframe artifacts on real Binance spot data only, cointegration-gated (fail-closed). Authorize ONLY POL/BTC (4h) for go-live; ALL blocked pairs remain HARD BLOCKED with zero capital/orders/fills/position limits, no auto-lift paths. Harden post-deployment validation (live reconciliation vs. expected state, PnL/position drift, order/fill audit), auto-remediation playbooks (auto-block on mismatch, kill-switch, rollback), deployment authorization gating linked to full chain (drift/permanent readiness + reconciliation/audit + go/no-go + operational readiness + execution validation + monitoring). Enforce causal-only trailing windows, fail-closed everywhere, complete provenance. Leave no gap untested.
>
> **REQUIRED ARTIFACTS:** `reports/production_go_live_authorization_mt.json`, `reports/post_deployment_validation_remediation_mt.json`
> **REQUIRED TESTS:** `tests/test_production_go_live_authorization_mt.py`, `tests/test_post_deployment_validation_remediation_mt.py`
> **REQUIRED GENERATOR:** `scripts/generate_campaign22_artifacts.py` (mirror Campaign 21 patterns: load `portfolio_gating_mt.json` + `production_go_nogo_certification_mt.json` + `operational_readiness_signoff_mt.json` + `live_execution_validation_hardening_mt.json` + `continuous_monitoring_hardening_mt.json` + `operational_drift_permanent_readiness_mt.json` + `reconciliation_audit_hardening_mt.json` + all prior MT artifacts, enforce invariants, zero blocked pairs, full provenance).
>
> **COMPLETION CRITERIA (BLOCKING):** Both artifacts and both tests exist and pass; schemas internally consistent and linked to full chain; gating preserved exactly (1h 0/17, 4h 1/17 POL/BTC, 1d 0/17); blocked pairs have zero capital/orders/fills with rejection logs + blocked_routes + remediation; go-live authorization/post-deployment validation/auto-remediation all fail-closed with explicit checks; ruff clean on touched files; targeted pytest green; handoff updated with concrete evidence (files, counts, test results). Do not stop until ALL criteria met. No coasting.

## CURRENT VERIFIED STATE (2026-11-02T01:06:55Z)
- Branch: `main`. HEAD = recent checkpoint commits (clean working tree).
- **Campaign 21 DONE:** Operational drift/permanent readiness + reconciliation audit hardening complete with artifacts/tests/generator.
- Data: `data/cache/` real Binance spot 1h (2026-04-01→2026-10-30) for 14 symbols + `volume_1h_full`; offline-capable. Prior OOS diagnostics exist (`reports/cointegration_diagnostics_oos_mt_*.json`, real data only).
- Integrity: All campaigns 1-21 artifacts/tests present; gating invariants intact (1h 0/17, 4h 1/17 POL/BTC, 1d 0/17). Handoff is single durable source of truth.

## BOTTLENECKS (REMOVED / PREVENTED)
- **BOTTLENECK REMOVED — CI env:** Install deps first (`python -m pip install -r requirements.txt`) before tests; missing numpy/pandas caused ModuleNotFoundError. ruff on touched files.
- **BOTTLENECK REMOVED — Tooling:** Avoid malformed write/edit calls; provide full `content`/`oldString`/`newString` arguments.
- **Ambiguity removed:** Explicit boot sequence + copy/paste initial task message + hard completion criteria.
- **Focus enforced:** Campaign 22 is the ONLY permitted focus until its artifacts/tests exist and pass.
- **Gating enforced:** Fail-closed invariants codified; no auto-lift paths.
- **Execution path unblocked:** Follow existing patterns (`scripts/generate_campaign*_artifacts.py`, `reports/*_mt.json`, `tests/test_*_mt.py`).

## HARD CONSTRAINTS
- **REAL DATA ONLY** — no fabrication. Resample of cached 1h is allowed (still real data).
- **NO WEAKENING THRESHOLDS** without ironclad justification + tests. Gate thresholds unchanged: rolling ≥ 0.6, EG p ≤ 0.05, half-life (1, 500).
- **PRESERVE GREEN** — all existing tests green; ruff clean.
- **CAUSAL ONLY** — no lookahead. Trailing windows only.
- **HONEST BLOCKING** — blocked pairs receive zero weight/fills/capacity allocation/position limits; full provenance; no forced blocking.
- **FAIL-CLOSED** — capacity/routing/drift/alerting/kill-switch/risk constraints never lift gating blocks. Only gated-eligible pairs can be feasible.
- **HEAVY MANDATE** — produce artifacts/tests/logs/provenance. No coasting. If stuck, do more verification/artifacts, not less.

## VERIFICATION COMMANDS (RUN OFTEN)
```bash
python -m ruff check backtest/ strategies/ utils/ tests/ examples/ scripts/
python -m pytest tests/test_operational_drift_permanent_readiness_mt.py tests/test_reconciliation_audit_hardening_mt.py -v
```
