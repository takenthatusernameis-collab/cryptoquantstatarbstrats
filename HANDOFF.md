# SINGLE DURABLE HANDOFF | 2026-11-01T18:12:29Z | CAMPAIGN 10 ACTIVE (LIVE PAPER-TRADING DEPLOYMENT BRIDGE + DRIFT MONITORING + COINTEGRATION-GATED ALERTING) | BOTTLENECKS CLEARED | MANDATORY HEAVY WORK

## REPO IDENTITY (LAW) — PRIORITIZE BY REPO NAME
- Repo: `cryptoquantstatarbstrats` — **Crypto Quant Stat Arb Strategies**.
- **CORE = COINTEGRATION / PAIRS TRADING.** Every other line of work serves cointegration rigor. Cointegration is law.
- Real data only: Binance public REST via `www.binance.com`. Never fabricate. Resampling cached 1h is allowed only if still from real data.
- Coasting = failure. Every action must produce checkable artifacts, tests, provenance, logs.
- Working tree: `main` clean. Do **not** commit unless explicitly requested.

## NEXT AGENT START HERE (TIMESTAMPED, MANDATORY, NO DEVIATION)
**TIMESTAMP:** 2026-11-01T18:12:29Z
**TARGET SESSION:** Next agentic work session (immediate, no ramp-up)
**PRIORITY BY REPO IDENTITY:** `cryptoquantstatarbstrats` = **Crypto Quant Stat Arb Strategies**. **CORE = COINTEGRATION/PAIRS TRADING — LAW.** All work serves cointegration rigor.

### IMMEDIATE BOOT SEQUENCE (BLOCKING - DO IN ORDER)
1. **Verify integrity (BLOCKING):** Run verification commands below. All must pass. If anything fails, fix as top priority with artifacts/tests before doing anything else.
2. **Read the law:** Re-read this handoff fully (HARD CONSTRAINTS are non-negotiable).
3. **Audit existing state:** Confirm gating artifacts exist: `reports/portfolio_gating_mt.json`, `reports/portfolio_walkforward_mt.json`, `reports/portfolio_cost_stress_mt.json`, `reports/mt_blocking_matrix.json`, `reports/mt_structural_breaks_summary.json`. Confirm Campaign 9 artifacts exist: `reports/execution_capacity_mt.json`, `reports/order_routing_realism_mt.json`, `reports/live_readiness_checklist_mt.json`. Confirm all cointegration-gating tests pass.
4. **Identify the gap (BLOCKING):** Campaign 10 artifacts/tests do **NOT** exist yet. This is the **ONLY** work to do now. Do not pivot to unrelated tasks.

### CONCRETE GATING STATE (DO NOT WEAKEN — from reports/portfolio_gating_mt.json)
- Universe: 17 pairs (BTC/ETH, ETH/SOL, BTC/SOL, ADA/ETH, XRP/BTC, BNB/ETH, BTC/BNB, SOL/BNB, ADA/BTC, XRP/ETH, BNB/BTC, DOT/BTC, DOT/ETH, POL/BTC, AVAX/BTC, LINK/BTC, LTC/BTC).
- 1h: 0 eligible / 17 blocked. 4h: 1 eligible (POL/BTC) / 16 blocked. 1d: 0 eligible / 17 blocked.
- Only gated-eligible pairs may receive weight/fills/capacity allocation. Blocked pairs = zero allocation, full provenance, honest blocking.
- Campaign 10 must **preserve** this exactly: drift/alerting/routing constraints never lift gating blocks.

### SINGLE INITIAL TASK MESSAGE (COPY/PASTE TO GUIDE THIS SESSION - MANDATORY, HEAVY)
> **OBJECTIVE (HEAVY, CAMPAIGN 10 - MANDATORY, COINTEGRATION-FIRST):** Build a live paper-trading deployment bridge + drift monitoring + cointegration-gated alerting while strictly preserving cointegration gating (fail-closed). Only real data/causal logic. No threshold weakening. No fabrication. Every gated block must remain blocked. Treat this as the sole deliverable until complete.
>
> **REQUIRED ARTIFACTS (MUST PRODUCE):** `reports/paper_trading_bridge_mt.json`, `reports/drift_monitor_mt.json`, `reports/alerting_rules_mt.json`
>
> **REQUIRED TESTS (MUST PRODUCE):** `tests/test_paper_trading_bridge_gating.py`, `tests/test_drift_monitor_schema.py`
>
> **REQUIREMENTS (HARD):**
> - **Paper trading bridge:** Bridge from MT-gated state to live/paper execution with deterministic mapping. Only gated-eligible pairs allowed. Blocked pairs must be zeroed with rejection_log, blocked_routes, provenance. Link to `reports/portfolio_gating_mt.json`, `reports/execution_capacity_mt.json`, `reports/order_routing_realism_mt.json`. Must be fail-closed.
> - **Drift monitoring:** Track cointegration drift, spread stationarity/regime changes, threshold drift, execution drift vs MT expectations. All checks causal/trailing only. Must detect and report drift but **NEVER** auto-lift blocks. Any drift that would suggest weakening gates is flagged as a violation.
> - **Cointegration-gated alerting:** Deterministic alert rules that fire only on policy violations/drift/gate breaches; alerts must respect gating (no alerts suggesting allocation to blocked pairs). Schema must include severity, evidence, provenance, gating_context, blocked_routes.
> - **Schema/monotonicity/provenance:** Full schema validation, monotonicity where applicable. Every artifact must include `real_data_only`, `fabricated_data`, `computed_at`, `source`, `gating_context`, `blocked_routes`/rationale. No synthetic fabrication.
> - **Remove bottlenecks:** If any existing path blocks efficient progress (tests/artifacts missing, gating gaps), fix/remove bottlenecks with artifacts/tests. Do not create new bottlenecks. Coasting = failure.
>
> **COMPLETION CRITERIA (BLOCKING):** All three artifacts and both tests exist, follow schemas consistent with prior MT artifacts, preserve gating (17 blocked at 1h/1d, only POL/BTC eligible at 4h), verification commands pass (ruff + targeted pytest), and this handoff updated with concrete evidence (artifact paths, test results, counts). Do not stop until done.

## CURRENT VERIFIED STATE (2026-11-01T18:12:29Z)
- Branch: `main`. HEAD = recent checkpoint commits (clean working tree).
- **Campaign 6 DONE:** MT cointegration stability + structural-break re-validation.
- **Campaign 7 DONE:** Portfolio-level cointegration gating integrated MT.
- **Campaign 8 DONE:** Execution realism MT.
- **Campaign 9 DONE:** Live-ready execution hardening + cointegration-gated capacity constraints.
- **Campaign 10 (ACTIVE - HEAVY):** Live paper-trading deployment bridge + drift monitoring + cointegration-gated alerting. Sole focus.
- Data: `data/cache/` real Binance spot 1h (2026-04-01→2026-10-30) for 14 symbols + `volume_1h_full`; offline-capable. Real data only.
- Integrity: `ruff` clean, targeted pytest passing (31 passed).

## BOTTLENECKS (REMOVED / PREVENTED)
Bottlenecks removed across campaigns; gating invariants tested. Handoff is single durable source of truth. Next-agent boot sequence explicit and unambiguous.

## FOCUS CAMPAIGNS (HISTORY)
- Campaign 1-9 DONE as above.
- **Campaign 10 (ACTIVE - HEAVY, DO NOT SKIP):** Live paper-trading deployment bridge + drift monitoring + cointegration-gated alerting. Produce `paper_trading_bridge_mt.json`, `drift_monitor_mt.json`, `alerting_rules_mt.json` + `test_paper_trading_bridge_gating.py`, `test_drift_monitor_schema.py`. Preserve honest blocking.

## HARD CONSTRAINTS
- **REAL DATA ONLY** — no fabrication. Resample of cached 1h is allowed (still real data).
- **NO WEAKENING THRESHOLDS** without ironclad justification + tests. Gate thresholds unchanged: rolling ≥ 0.6, EG p ≤ 0.05, half-life (1, 500).
- **PRESERVE GREEN** — all existing tests green; ruff clean.
- **CAUSAL ONLY** — no lookahead. Trailing windows only.
- **HONEST BLOCKING** — blocked pairs receive zero weight/fills/capacity allocation; full provenance; no forced blocking.
- **FAIL-CLOSED** — capacity/routing/drift/alerting constraints never lift gating blocks. Only gated-eligible pairs can be feasible.
- **HEAVY MANDATE** — produce artifacts/tests/logs/provenance. No coasting. If stuck, do more verification/artifacts, not less.

## VERIFICATION COMMANDS (RUN OFTEN)
```bash
python -m ruff check backtest/ strategies/ utils/ tests/ examples/ scripts/
python -m pytest tests/test_cointegration_diagnostics_schema.py tests/test_cointegration_threshold_invariance.py tests/test_portfolio_gating_mt.py tests/test_execution_gating_consistency.py tests/test_execution_realism_schema.py tests/test_execution_capacity_gating.py tests/test_order_routing_schema.py -v
```
