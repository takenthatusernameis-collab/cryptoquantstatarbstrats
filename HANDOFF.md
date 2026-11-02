# SINGLE DURABLE HANDOFF | 2026-11-02T03:00:01Z | CAMPAIGN 23 COMPLETE (LIVE OPERATIONS CONTINUITY + INCIDENT RESPONSE + CAPITAL PRESERVATION HARDENING) | CAMPAIGN 24 ACTIVE / NOT STARTED (PERMANENT PRODUCTION CERTIFICATION + CONTINUOUS IMPROVEMENT & AUTO-SCALING HARDENING) | BOTTLENECKS REMOVED | MANDATORY HEAVY WORK

## REPO IDENTITY (LAW) — PRIORITIZE BY REPO NAME
- Repo: `cryptoquantstatarbstrats` — **Crypto Quant Stat Arb Strategies**.
- **CORE = COINTEGRATION / PAIRS TRADING.** Every other line of work serves cointegration rigor. Cointegration is law.
- Real data only: Binance public REST via `www.binance.com`. Never fabricate. Resampling cached 1h is allowed only if still from real data.
- Coasting = failure. Every action must produce checkable artifacts, tests, provenance, logs.
- Working tree: `main` clean. Do **not** commit unless explicitly requested.

## NEXT AGENT START HERE (TIMESTAMPED, MANDATORY, NO DEVIATION)
**TIMESTAMP:** 2026-11-02T03:00:01Z
**TARGET SESSION:** Next agentic work session (immediate, no ramp-up)
**PRIORITY BY REPO IDENTITY:** `cryptoquantstatarbstrats` = **Crypto Quant Stat Arb Strategies**. **CORE = COINTEGRATION/PAIRS TRADING — LAW.** All work serves cointegration rigor.

### IMMEDIATE BOOT SEQUENCE (BLOCKING - DO IN ORDER)
1. **Verify integrity (BLOCKING):** Run the verification commands below. All must pass. If anything fails, fix as top priority with artifacts/tests before doing anything else.
2. **Read the law:** Re-read this handoff fully (HARD CONSTRAINTS are non-negotiable).
3. **Confirm Campaign 23 complete:** `reports/live_operations_continuity_incident_response_mt.json`, `reports/capital_preservation_failover_hardening_mt.json` exist; `tests/test_live_operations_continuity_incident_response_mt.py` and `tests/test_capital_preservation_failover_hardening_mt.py` pass; gating invariants intact (1h 0/17, 4h 1/17 POL/BTC, 1d 0/17).
4. **Campaign 24 is the sole work now.** Do not pivot to unrelated tasks.

### SINGLE INITIAL TASK MESSAGE (COPY/PASTE TO GUIDE THIS SESSION - MANDATORY, HEAVY)
> **OBJECTIVE (HEAVY, CAMPAIGN 24 - MANDATORY, COINTEGRATION-FIRST):** Permanent production certification + continuous improvement & auto-scaling hardening across ALL multi-timeframe artifacts on real Binance spot data only, cointegration-gated (fail-closed). Certify ONLY POL/BTC (4h) as permanently production-certified; ALL blocked pairs remain HARD BLOCKED with zero capital/orders/fills/position limits, no auto-lift paths. Harden permanent certification (rolling re-certification, drift-triggered re-cert), continuous improvement loops (model refresh gates, parameter stability, regression guards), auto-scaling gates (scale only on sustained gated eligibility + stability + capacity), linked to full chain (continuity/incident response + capital preservation/failover + go-live authorization + post-deployment validation + drift/permanent readiness + reconciliation/audit + go/no-go + operational readiness + execution validation + monitoring). Enforce causal-only trailing windows, fail-closed everywhere, complete provenance. Leave no gap untested.
>
> **REQUIRED ARTIFACTS:** `reports/permanent_production_certification_mt.json`, `reports/continuous_improvement_autoscaling_mt.json`
> **REQUIRED TESTS:** `tests/test_permanent_production_certification_mt.py`, `tests/test_continuous_improvement_autoscaling_mt.py`
> **REQUIRED GENERATOR:** `scripts/generate_campaign24_artifacts.py` (mirror Campaign 23 patterns: load `portfolio_gating_mt.json` + `live_operations_continuity_incident_response_mt.json` + `capital_preservation_failover_hardening_mt.json` + all prior MT artifacts, enforce invariants, zero blocked pairs, full provenance).
>
> **COMPLETION CRITERIA (BLOCKING):** Both artifacts and both tests exist and pass; schemas internally consistent and linked to full chain; gating preserved exactly (1h 0/17, 4h 1/17 POL/BTC, 1d 0/17); blocked pairs have zero capital/orders/fills with rejection logs + blocked_routes + remediation; permanent certification/continuous improvement/auto-scaling all fail-closed with explicit checks; ruff clean on touched files; targeted pytest green; handoff updated with concrete evidence (files, counts, test results). Do not stop until ALL criteria met. No coasting.

## CURRENT VERIFIED STATE (2026-11-02T03:00:01Z)
- Branch: `main`. HEAD = recent checkpoint commits (clean working tree).
- **Campaign 23 DONE:** Live operations continuity + incident response + capital preservation hardening complete with artifacts/tests/generator.
- Data: `data/cache/` real Binance spot 1h (2026-04-01→2026-10-30) for 14 symbols + `volume_1h_full`; offline-capable. Prior OOS diagnostics exist (`reports/cointegration_diagnostics_oos_mt_*.json`, real data only).
- Integrity: All campaigns 1-23 artifacts/tests present; Campaign 24 artifacts/tests NOT present (not started); gating invariants intact (1h 0/17, 4h 1/17 POL/BTC, 1d 0/17). Handoff is single durable source of truth.

## BOTTLENECKS (REMOVED / PREVENTED)
- **BOTTLENECK REMOVED — CI env:** Install deps first (`python -m pip install -r requirements.txt`) before tests; missing numpy/pandas caused ModuleNotFoundError. ruff on touched files.
- **BOTTLENECK REMOVED — Tooling:** Avoid malformed write/edit calls; provide full `content`/`oldString`/`newString` arguments.
- **Ambiguity removed:** Explicit boot sequence + copy/paste initial task message + hard completion criteria.
- **Focus enforced:** Campaign 24 is the ONLY permitted focus until its artifacts/tests exist and pass. No pivoting to unrelated work.
- **Gating enforced:** Fail-closed invariants codified; no auto-lift paths.
- **Execution path unblocked:** Follow existing patterns (`scripts/generate_campaign*_artifacts.py`, `reports/*_mt.json`, `tests/test_*_mt.py`).
- **No missing evidence:** Campaign 23 completion evidence recorded so no session re-derives state.

## HARD CONSTRAINTS
- **REAL DATA ONLY** — no fabrication. Resample of cached 1h is allowed (still real data).
- **NO WEAKENING THRESHOLDS** without ironclad justification + tests. Gate thresholds unchanged: rolling ≥ 0.6, EG p ≤ 0.05, half-life (1, 500).
- **PRESERVE GREEN** — all existing tests green; ruff clean.
- **CAUSAL ONLY** — no lookahead. Trailing windows only.
- **HONEST BLOCKING** — blocked pairs receive zero weight/fills/capacity allocation/position limits; full provenance; no forced blocking.
- **FAIL-CLOSED** — capacity/routing/drift/alerting/kill-switch/risk constraints never lift gating blocks. Only gated-eligible pairs can be feasible.
- **HEAVY MANDATE** — produce artifacts/tests/logs/provenance. No coasting. If stuck, do more verification/artifacts, not less.
- **INCIDENT DISCIPLINE** — every breach must be logged with cause, containment, and audit trail; no silent remediation.

## VERIFICATION COMMANDS (RUN OFTEN)
```bash
python -m pip install -r requirements.txt
python -m ruff check backtest/ strategies/ utils/ tests/ examples/ scripts/
python -m pytest tests/test_live_operations_continuity_incident_response_mt.py tests/test_capital_preservation_failover_hardening_mt.py -v
```

## CAMPAIGN 24 PENDING (NOT STARTED)
No artifacts, tests, or generator exist for Campaign 24 on disk. The next session must produce them per the SINGLE INITIAL TASK MESSAGE above before any other work.
