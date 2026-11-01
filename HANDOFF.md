# SINGLE DURABLE HANDOFF | 2026-11-01T21:00:17Z | CAMPAIGN 13 ACTIVE (LIVE EXECUTION INTEGRATION + POSITION SIZING ENFORCEMENT + REAL-TIME MONITORING) | BOTTLENECKS CLEARED | MANDATORY HEAVY WORK

## REPO IDENTITY (LAW) — PRIORITIZE BY REPO NAME
- Repo: `cryptoquantstatarbstrats` — **Crypto Quant Stat Arb Strategies**.
- **CORE = COINTEGRATION / PAIRS TRADING.** Every other line of work serves cointegration rigor. Cointegration is law.
- Real data only: Binance public REST via `www.binance.com`. Never fabricate. Resampling cached 1h is allowed only if still from real data.
- Coasting = failure. Every action must produce checkable artifacts, tests, provenance, logs.
- Working tree: `main` clean. Do **not** commit unless explicitly requested.

## NEXT AGENT START HERE (TIMESTAMPED, MANDATORY, NO DEVIATION)
**TIMESTAMP:** 2026-11-01T21:00:17Z
**TARGET SESSION:** Next agentic work session (immediate, no ramp-up)
**PRIORITY BY REPO IDENTITY:** `cryptoquantstatarbstrats` = **Crypto Quant Stat Arb Strategies**. **CORE = COINTEGRATION/PAIRS TRADING — LAW.** All work serves cointegration rigor.

### IMMEDIATE BOOT SEQUENCE (BLOCKING - DO IN ORDER)
1. **Verify integrity (BLOCKING):** Run the verification commands below. All must pass. If anything fails, fix as top priority with artifacts/tests before doing anything else.
2. **Read the law:** Re-read this handoff fully (HARD CONSTRAINTS are non-negotiable).
3. **Confirm Campaign 12 complete:** `reports/operational_risk_controls_mt.json`, `reports/pre_trade_enforcement_mt.json`, `reports/portfolio_guardrails_mt.json` exist; `tests/test_operational_risk_controls_gating.py` and `tests/test_portfolio_guardrails_schema.py` pass (see CAMPAIGN 12 COMPLETED evidence below).
4. **Campaign 13 artifacts/tests do NOT exist yet — sole work now.** Do not pivot to unrelated tasks.

### SINGLE INITIAL TASK MESSAGE (COPY/PASTE TO GUIDE THIS SESSION - MANDATORY, HEAVY)
> **OBJECTIVE (HEAVY, CAMPAIGN 13 - MANDATORY, COINTEGRATION-FIRST):** Build live execution integration + position sizing enforcement + real-time monitoring, cointegration-gated (fail-closed). Real data only. No threshold weakening. No fabrication. Every gated block remains blocked.
>
> **REQUIRED ARTIFACTS:** `reports/live_execution_integration_mt.json`, `reports/position_sizing_enforcement_mt.json`, `reports/realtime_monitoring_mt.json`
> **REQUIRED TESTS:** `tests/test_live_execution_integration_gating.py`, `tests/test_position_sizing_enforcement_schema.py` (and ensure schemas align with existing gating tests; if gaps exist, create minimal additional tests only to enforce invariants)
>
> **REQUIREMENTS (HARD):**
> - **Live execution integration:** Deterministic integration mapping from MT-gated state to live execution interface; only gated-eligible pairs (POL/BTC at 4h; 0/17 at 1h, 0/17 at 1d); blocked pairs zeroed/enforced with `rejection_log`/`blocked_routes`/`orders_allowed`/`fills_allowed` = false; fail-closed; link to all prior artifacts (`reports/portfolio_gating_mt.json`, `reports/execution_capacity_mt.json`, `reports/order_routing_realism_mt.json`, `reports/live_deployment_bridge_mt.json`, `reports/kill_switch_rules_mt.json`, `reports/operational_risk_controls_mt.json`, `reports/pre_trade_enforcement_mt.json`, `reports/portfolio_guardrails_mt.json`).
> - **Position sizing enforcement:** Hard enforcement of position sizes strictly by cointegration-gated eligibility; no size inflation for blocked pairs; max position limits per eligible pair with full provenance; sizing must be non-negative and zero for blocked; fail-closed.
> - **Real-time monitoring:** Cointegration-gated monitoring with alerts on gate breaches/drift; must respect all gates (never auto-lift); fail-closed with evidence/provenance/blocked_routes; must not infer eligibility from price/vol alone.
> - **Schema/provenance/monotonicity:** `real_data_only=true`, `fabricated_data=false`, `computed_at` (UTC ISO8601), `source`, `gating_context`, `blocked_routes`/rationale. No synthetic fabrication. Causal only (trailing windows).
> - **Remove bottlenecks:** If any existing path blocks efficient progress (missing generator, import errors, schema gaps), fix/remove bottlenecks with artifacts/tests in the same campaign. Do not create new bottlenecks. Coasting = failure.
>
> **COMPLETION CRITERIA (BLOCKING):** All three artifacts and both tests exist, schemas consistent with prior MT artifacts, gating preserved (1h 0/17, 4h 1/17 POL/BTC, 1d 0/17), ruff clean, targeted pytest green, handoff updated with evidence (Campaign 13 COMPLETED section). Do not stop until done.

## CURRENT VERIFIED STATE (2026-11-01T21:00:17Z)
- Branch: `main`. HEAD = recent checkpoint commits (clean working tree).
- **Campaign 6 DONE:** MT cointegration stability + structural-break re-validation.
- **Campaign 7 DONE:** Portfolio-level cointegration gating integrated MT.
- **Campaign 8 DONE:** Execution realism MT.
- **Campaign 9 DONE:** Live-ready execution hardening + cointegration-gated capacity constraints.
- **Campaign 10 DONE:** Live paper-trading deployment bridge + drift monitoring + cointegration-gated alerting complete.
- **Campaign 11 DONE:** Production live-deployment hardening + post-trade reconciliation + kill-switch complete.
- **Campaign 12 DONE:** Operational risk controls + pre-trade enforcement + portfolio guardrails complete.
- **Campaign 13 ACTIVE:** Live execution integration + position sizing enforcement + real-time monitoring (NOT STARTED — create generator + artifacts + tests now).
- Data: `data/cache/` real Binance spot 1h (2026-04-01→2026-10-30) for 14 symbols + `volume_1h_full`; offline-capable. Real data only.
- Integrity: Campaign 12 artifacts/tests verified present; gating invariants intact. Handoff is single durable source of truth.

## BOTTLENECKS (REMOVED / PREVENTED)
- **Ambiguity removed:** Explicit boot sequence + copy/paste initial task message + hard completion criteria.
- **Focus enforced:** Campaign 13 is the ONLY permitted focus until its artifacts/tests exist and pass.
- **Gating enforced:** Fail-closed invariants codified; no auto-lift paths.
- **Execution path unblocked:** Follow existing patterns (`scripts/generate_campaign*_artifacts.py`, `reports/*_mt.json`, `tests/test_*_gating.py`) — do not invent new parallel tracks.

## FOCUS CAMPAIGNS (HISTORY)
- Campaign 1-9 DONE (cointegration stability, structural breaks, portfolio gating MT, execution realism MT, live-ready execution hardening).
- Campaign 10 DONE: Live paper-trading deployment bridge + drift monitoring + cointegration-gated alerting.
- Campaign 11 DONE: Production live-deployment hardening + post-trade reconciliation + kill-switch.
- Campaign 12 DONE: Operational risk controls + pre-trade enforcement + portfolio guardrails.
- **Campaign 13 (ACTIVE - HEAVY, DO NOT SKIP):** Live execution integration + position sizing enforcement + real-time monitoring. Produce `live_execution_integration_mt.json`, `position_sizing_enforcement_mt.json`, `realtime_monitoring_mt.json` + `tests/test_live_execution_integration_gating.py`, `tests/test_position_sizing_enforcement_schema.py`. Preserve honest blocking.

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
python -m pytest tests/test_cointegration_diagnostics_schema.py tests/test_cointegration_threshold_invariance.py tests/test_portfolio_gating_mt.py tests/test_execution_gating_consistency.py tests/test_execution_realism_schema.py tests/test_execution_capacity_gating.py tests/test_order_routing_schema.py tests/test_live_deployment_bridge_gating.py tests/test_kill_switch_schema.py tests/test_operational_risk_controls_gating.py tests/test_portfolio_guardrails_schema.py -v
```

## CAMPAIGN 11 COMPLETED (2026-11-01T19:52:00Z) - EVIDENCE
- **ARTIFACTS PRODUCED (PRESERVING GATING - FAIL-CLOSED):**
  - `reports/live_deployment_bridge_mt.json` (production live-deployment bridge from MT-gated state; only POL/BTC eligible at 4h; 0/17 at 1h, 0/17 at 1d; blocked pairs zeroed with rejection_log/blocked_routes/orders_allowed/fills_allowed=false; full provenance; linked to prior artifacts)
  - `reports/post_trade_reconciliation_mt.json` (post-trade reconciliation vs gated state; mismatches_detect_only; auto_lift_blocks_forbidden; never_auto_lift_gates)
  - `reports/kill_switch_rules_mt.json` (cointegration-gated kill-switch; respect gating/fail-closed; no_auto_lift_of_blocks; severity with evidence/provenance/gating_context/blocked_routes)
- **TESTS PRODUCED:**
  - `tests/test_live_deployment_bridge_gating.py` (PASSED) - bridge enforces gating invariants, zero allocation for blocked, links prior artifacts
  - `tests/test_kill_switch_schema.py` (PASSED) - kill-switch schema/invariants, reconciliation invariants, gated triggers with evidence
- **INVARIANTS PRESERVED:** real_data_only=true, fabricated_data=false, gating unchanged (1h 0/17, 4h 1/17 POL/BTC, 1d 0/17), fail-closed, no threshold weakening, no auto-lift of blocks.

## CAMPAIGN 12 COMPLETED (2026-11-01T19:58:00Z) - EVIDENCE
- **ARTIFACTS PRODUCED (PRESERVING GATING - FAIL-CLOSED):**
  - `reports/operational_risk_controls_mt.json` (operational risk controls + pre-trade enforcement mapping from MT-gated state; only POL/BTC eligible at 4h; 0/17 at 1h, 0/17 at 1d; blocked pairs zeroed/enforced with rejection_log/blocked_routes; full provenance; linked to portfolio_gating_mt.json/execution_capacity_mt.json/order_routing_realism_mt.json/live_deployment_bridge_mt.json/kill_switch_rules_mt.json)
  - `reports/pre_trade_enforcement_mt.json` (hard pre-trade enforcement; orders/position increases blocked for gated-blocked pairs; cointegration-gated checks; fail-closed; no_auto_lift_of_blocks)
  - `reports/portfolio_guardrails_mt.json` (portfolio guardrails enforcing cointegration gating; risk budget not allocated to blocked pairs; fail-closed; no_auto_lift_of_blocks)
- **TESTS PRODUCED:**
  - `tests/test_operational_risk_controls_gating.py` (PASSED) - operational risk controls enforce gating invariants, zero allocation/limits for blocked, rejection logs + blocked routes present
  - `tests/test_portfolio_guardrails_schema.py` (PASSED) - portfolio guardrails/pre-trade enforcement schema/invariants, gated triggers with evidence, no auto-lift
- **VERIFICATION:**
  - Campaign 12 artifacts generated via `scripts/generate_campaign12_artifacts.py`
  - Gating invariants verified programmatically (1h 0/17, 4h 1/17 POL/BTC, 1d 0/17) across all three artifacts
- **INVARIANTS PRESERVED:** real_data_only=true, fabricated_data=false, gating unchanged (1h 0/17, 4h 1/17 POL/BTC, 1d 0/17), fail-closed, no threshold weakening, no auto-lift of blocks.

## CAMPAIGN 13 (ACTIVE) — EXECUTION PLAN
1. **Create generator:** `scripts/generate_campaign13_artifacts.py` following Campaign 12 patterns. Load all prior MT artifacts + `portfolio_gating_mt.json`. Enforce gating invariants explicitly (1h 0/17, 4h 1/17 POL/BTC, 1d 0/17).
2. **Generate artifacts:** `reports/live_execution_integration_mt.json`, `reports/position_sizing_enforcement_mt.json`, `reports/realtime_monitoring_mt.json` with full provenance, blocked_routes, rejection_log, gating_context, linked_artifacts.
3. **Write tests:** `tests/test_live_execution_integration_gating.py`, `tests/test_position_sizing_enforcement_schema.py` mirroring Campaign 12 gating tests (eligible sets equal to gating, blocked zeroed, rejection logs present, provenance/gating_context correct).
4. **Verify:** Run verification commands. Fix any gaps. Update this handoff with CAMPAIGN 13 COMPLETED evidence.
