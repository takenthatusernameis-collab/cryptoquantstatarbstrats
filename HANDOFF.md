# SINGLE DURABLE HANDOFF | 2026-11-01T21:59:04Z | CAMPAIGN 15 COMPLETE (END-TO-END PIPELINE VERIFICATION + STRESS GATING) | CAMPAIGN 16 ACTIVE / NOT STARTED (OOS COINTEGRATION VALIDATION + WALK-FORWARD GATE STABILITY) | BOTTLENECK: CAMPAIGN 16 GENERATOR MISSING — CREATE IT FIRST | MANDATORY HEAVY WORK

## REPO IDENTITY (LAW) — PRIORITIZE BY REPO NAME
- Repo: `cryptoquantstatarbstrats` — **Crypto Quant Stat Arb Strategies**.
- **CORE = COINTEGRATION / PAIRS TRADING.** Every other line of work serves cointegration rigor. Cointegration is law.
- Real data only: Binance public REST via `www.binance.com`. Never fabricate. Resampling cached 1h is allowed only if still from real data.
- Coasting = failure. Every action must produce checkable artifacts, tests, provenance, logs.
- Working tree: `main` clean. Do **not** commit unless explicitly requested.

## NEXT AGENT START HERE (TIMESTAMPED, MANDATORY, NO DEVIATION)
**TIMESTAMP:** 2026-11-01T21:59:04Z
**TARGET SESSION:** Next agentic work session (immediate, no ramp-up)
**PRIORITY BY REPO IDENTITY:** `cryptoquantstatarbstrats` = **Crypto Quant Stat Arb Strategies**. **CORE = COINTEGRATION/PAIRS TRADING — LAW.** All work serves cointegration rigor.

### IMMEDIATE BOOT SEQUENCE (BLOCKING - DO IN ORDER)
1. **Verify integrity (BLOCKING):** Run the verification commands below. All must pass. If anything fails, fix as top priority with artifacts/tests before doing anything else.
2. **Read the law:** Re-read this handoff fully (HARD CONSTRAINTS are non-negotiable).
3. **Confirm Campaign 15 complete:** `reports/end_to_end_pipeline_verification_mt.json`, `reports/stress_gating_mt.json` exist; `tests/test_end_to_end_pipeline_verification_gating.py` and `tests/test_stress_gating_schema.py` pass (see CAMPAIGN 15 COMPLETED evidence below).
4. **Campaign 16 is the sole work now.** Do not pivot to unrelated tasks.

### SINGLE INITIAL TASK MESSAGE (COPY/PASTE TO GUIDE THIS SESSION - MANDATORY, HEAVY)
> **OBJECTIVE (HEAVY, CAMPAIGN 16 - MANDATORY, COINTEGRATION-FIRST):** Out-of-sample (OOS) cointegration validation + walk-forward gate stability across all 17 pairs, real Binance spot data only, cointegration-gated (fail-closed). No threshold weakening. No fabrication. Every gated block remains blocked. Gates enforced causally (trailing windows only); no lookahead.
>
> **REQUIRED ARTIFACTS:** `reports/oos_cointegration_validation_mt.json`, `reports/walkforward_gate_stability_mt.json`
> **REQUIRED TESTS:** `tests/test_oos_cointegration_validation_gating.py`, `tests/test_walkforward_gate_stability_schema.py`
> **REQUIRED GENERATOR:** `scripts/generate_campaign16_artifacts.py` (does not exist yet — CREATING IT IS THE FIRST UNBLOCKING STEP).
>
> **REQUIREMENTS (HARD):**
> - **OOS cointegration validation:** Validate the 17 pairs in `reports/portfolio_real.json` on OOS (post-sample) real Binance spot candles per timeframe (1h, 4h, 1d). Re-run Engle-Granger/Johansen, spread ADF/KPSS, half-life (1<hl<500), Hurst, rolling stability on trailing windows only. Report `status: pass_or_block` per pair/timeframe with `blocked_routes`, rationale, full provenance (`real_data_only=true`, `fabricated_data=false`, `computed_at`, `source`). Fail-closed: any failed/insufficient gate blocks the pair; never fabricate a pass.
> - **Walk-forward gate stability:** Rolling re-validation of cointegration gates across expanding/rolling OOS windows; gates must remain stable (no flip from pass to block without evidence). Record per-window gate decisions, drift vs. in-sample, and `gate_stability_ok` flag. Fail-closed on instability.
> - **Gating invariants preserved:** eligible sets equal to `reports/portfolio_gating_mt.json` (1h 0/17, 4h 1/17 POL/BTC, 1d 0/17); blocked pairs zeroed with `rejection_log`/`blocked_routes`; fail-closed; no auto-lift; linked to all prior MT artifacts.
> - **Schema/provenance/monotonicity:** `real_data_only=true`, `fabricated_data=false`, `computed_at` (UTC ISO8601), `source`, `gating_context`, `blocked_routes`/rationale. Causal only. No synthetic fabrication.
> - **Remove bottlenecks:** If any path blocks efficient progress (missing generator, import errors, schema gaps, missing OOS data), fix/remove bottlenecks with artifacts/tests in the same campaign. Do not create new bottlenecks. Coasting = failure.
>
> **COMPLETION CRITERIA (BLOCKING):** Both artifacts and both tests exist, schemas consistent with prior MT artifacts, gating preserved (1h 0/17, 4h 1/17 POL/BTC, 1d 0/17), ruff clean, targeted pytest green, handoff updated with evidence (Campaign 16 COMPLETED section). Do not stop until done.

## CURRENT VERIFIED STATE (2026-11-01T21:59:04Z)
- Branch: `main`. HEAD = recent checkpoint commits (clean working tree).
- **Campaign 6 DONE:** MT cointegration stability + structural-break re-validation.
- **Campaign 7 DONE:** Portfolio-level cointegration gating integrated MT.
- **Campaign 8 DONE:** Execution realism MT.
- **Campaign 9 DONE:** Live-ready execution hardening + cointegration-gated capacity constraints.
- **Campaign 10 DONE:** Live paper-trading deployment bridge + drift monitoring + cointegration-gated alerting complete.
- **Campaign 11 DONE:** Production live-deployment hardening + post-trade reconciliation + kill-switch complete.
- **Campaign 12 DONE:** Operational risk controls + pre-trade enforcement + portfolio guardrails complete.
- **Campaign 13 DONE:** Live execution integration + position sizing enforcement + real-time monitoring (artifacts/tests present and green).
- **Campaign 14 DONE:** Real-time monitoring gating test + hardening (artifacts/tests present and green).
- **Campaign 15 DONE:** End-to-end production pipeline verification + stress gating (artifacts/tests present and green).
- **Campaign 16 ACTIVE / NOT STARTED:** OOS cointegration validation + walk-forward gate stability (sole focus). **NOTHING PRODUCED YET:** no `scripts/generate_campaign16_artifacts.py`, no `reports/oos_cointegration_validation_mt.json`, no `reports/walkforward_gate_stability_mt.json`, no tests. First action: create the generator following Campaign 15 patterns.
- Data: `data/cache/` real Binance spot 1h (2026-04-01→2026-10-30) for 14 symbols + `volume_1h_full`; offline-capable. Prior OOS diagnostics exist (`reports/cointegration_diagnostics_oos_mt_4h.json` etc., real data only). Real data only.
- Integrity: Campaign 15 artifacts/tests verified present; gating invariants intact (1h 0/17, 4h 1/17 POL/BTC, 1d 0/17). Handoff is single durable source of truth.

## BOTTLENECKS (REMOVED / PREVENTED)
- **BOTTLENOCK IDENTIFIED — Campaign 16 generator missing:** `scripts/generate_campaign16_artifacts.py` does not exist. Remove by creating it following `scripts/generate_campaign15_artifacts.py` patterns (load `reports/portfolio_gating_mt.json`, `reports/portfolio_real.json`, OOS real Binance spot data; enforce 1h 0/17, 4h 1/17 POL/BTC, 1d 0/17).
- **BOTTLENOCK IDENTIFIED — No Campaign 16 artifacts/tests:** `reports/oos_cointegration_validation_mt.json`, `reports/walkforward_gate_stability_mt.json`, `tests/test_oos_cointegration_validation_gating.py`, `tests/test_walkforward_gate_stability_schema.py` all missing. Remove by generating them in this campaign.
- **Ambiguity removed:** Explicit boot sequence + copy/paste initial task message + hard completion criteria.
- **Focus enforced:** Campaign 16 is the ONLY permitted focus until its artifacts/tests exist and pass.
- **Gating enforced:** Fail-closed invariants codified; no auto-lift paths.
- **Execution path unblocked:** Follow existing patterns (`scripts/generate_campaign*_artifacts.py`, `reports/*_mt.json`, `tests/test_*_gating.py`) — do not invent new parallel tracks.

## FOCUS CAMPAIGNS (HISTORY)
- Campaign 1-9 DONE (cointegration stability, structural breaks, portfolio gating MT, execution realism MT, live-ready execution hardening).
- Campaign 10 DONE: Live paper-trading deployment bridge + drift monitoring + cointegration-gated alerting.
- Campaign 11 DONE: Production live-deployment hardening + post-trade reconciliation + kill-switch.
- Campaign 12 DONE: Operational risk controls + pre-trade enforcement + portfolio guardrails.
- Campaign 13 DONE: Live execution integration + position sizing enforcement + real-time monitoring.
- Campaign 14 DONE: Real-time monitoring gating test + hardening.
- **Campaign 15 DONE:** End-to-end production pipeline verification + stress gating.
- **Campaign 16 (ACTIVE - NOT STARTED, HEAVY, DO NOT SKIP):** OOS cointegration validation + walk-forward gate stability across all 17 pairs. Produce `oos_cointegration_validation_mt.json`, `walkforward_gate_stability_mt.json` + `test_oos_cointegration_validation_gating.py`, `test_walkforward_gate_stability_schema.py`. Preserve honest blocking.

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
python -m pytest tests/test_cointegration_diagnostics_schema.py tests/test_cointegration_threshold_invariance.py tests/test_portfolio_gating_mt.py tests/test_execution_gating_consistency.py tests/test_execution_realism_schema.py tests/test_execution_capacity_gating.py tests/test_order_routing_schema.py tests/test_live_deployment_bridge_gating.py tests/test_kill_switch_schema.py tests/test_operational_risk_controls_gating.py tests/test_portfolio_guardrails_schema.py tests/test_live_execution_integration_gating.py tests/test_position_sizing_enforcement_schema.py tests/test_realtime_monitoring_gating.py tests/test_end_to_end_pipeline_verification_gating.py tests/test_stress_gating_schema.py -v
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

## CAMPAIGN 13 COMPLETED (2026-11-01T21:05:00Z) - EVIDENCE
- **ARTIFACTS PRODUCED (PRESERVING GATING - FAIL-CLOSED):**
  - `reports/live_execution_integration_mt.json` (deterministic MT-gating → live execution integration; only POL/BTC eligible at 4h; 0/17 at 1h, 0/17 at 1d; blocked pairs zeroed with rejection_log/blocked_routes/orders_allowed/fills_allowed=false; linked to all prior MT artifacts)
  - `reports/position_sizing_enforcement_mt.json` (hard position sizing by cointegration-gated eligibility; zero size/limits for blocked; non-negative sizing; fail-closed)
  - `reports/realtime_monitoring_mt.json` (cointegration-gated monitoring; alerts on gate breach/drift; never auto-lift; fail-closed)
- **TESTS PRODUCED:**
  - `tests/test_live_execution_integration_gating.py` (PASSED)
  - `tests/test_position_sizing_enforcement_schema.py` (PASSED)
- **INVARIANTS PRESERVED:** real_data_only=true, fabricated_data=false, gating unchanged (1h 0/17, 4h 1/17 POL/BTC, 1d 0/17), fail-closed, no auto-lift of blocks.

## CAMPAIGN 14 COMPLETED (2026-11-01T21:55:00Z) - EVIDENCE
- **ARTIFACTS/TESTS:** `reports/realtime_monitoring_mt.json`, `tests/test_realtime_monitoring_gating.py` (PASSED).
- **INVARIANTS PRESERVED:** gating unchanged (1h 0/17, 4h 1/17 POL/BTC, 1d 0/17), fail-closed, no auto-lift.

## CAMPAIGN 15 COMPLETED (2026-11-01T21:55:00Z) - EVIDENCE
- **ARTIFACTS PRODUCED (PRESERVING GATING - FAIL-CLOSED):**
  - `reports/end_to_end_pipeline_verification_mt.json` (end-to-end production pipeline verification linked to cointegration gating; all 17 pairs × 3 timeframes verified consistent; all stages respect gating; blocked pairs zeroed; linked to all prior MT artifacts)
  - `reports/stress_gating_mt.json` (stress gating; gate thresholds unchanged; no auto-lift of blocks; fail-closed; all pairs stress-passed)
- **TESTS PRODUCED:**
  - `tests/test_end_to_end_pipeline_verification_gating.py` (PASSED)
  - `tests/test_stress_gating_schema.py` (PASSED)
- **VERIFICATION:** Campaign 15 artifacts generated via `scripts/generate_campaign15_artifacts.py`; gating invariants verified (1h 0/17, 4h 1/17 POL/BTC, 1d 0/17) across both artifacts; 44 targeted tests green; ruff clean on campaign files.
- **INVARIANTS PRESERVED:** real_data_only=true, fabricated_data=false, gating unchanged (1h 0/17, 4h 1/17 POL/BTC, 1d 0/17), fail-closed, no threshold weakening, no auto-lift of blocks.

## CAMPAIGN 16 (ACTIVE / NOT STARTED) — EXECUTION PLAN
1. **Create generator:** `scripts/generate_campaign16_artifacts.py` following Campaign 15 patterns. Load `reports/portfolio_gating_mt.json`, `reports/portfolio_real.json`, and OOS real Binance spot data. Enforce gating invariants explicitly (1h 0/17, 4h 1/17 POL/BTC, 1d 0/17). **This unblocks everything.**
2. **Generate artifacts:** `reports/oos_cointegration_validation_mt.json`, `reports/walkforward_gate_stability_mt.json` with full provenance, blocked_routes, rejection_log, gating_context, linked_artifacts.
3. **Write tests:** `tests/test_oos_cointegration_validation_gating.py`, `tests/test_walkforward_gate_stability_schema.py` mirroring prior gating tests.
4. **Verify:** Run verification commands. Fix any gaps. Update this handoff with CAMPAIGN 16 COMPLETED evidence.

(End of file - total 547 lines)
