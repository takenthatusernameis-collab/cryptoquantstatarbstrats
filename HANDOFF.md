# SINGLE DURABLE HANDOFF | 2026-11-01T18:11:33Z | CAMPAIGN 9 ACTIVE (LIVE-READY EXECUTION HARDENING + COINTEGRATION-GATED CAPACITY CONSTRAINTS) | BOTTLENECKS CLEARED | MANDATORY HEAVY WORK

## REPO IDENTITY (LAW) — PRIORITIZE BY REPO NAME
- Repo: `cryptoquantstatarbstrats` — **Crypto Quant Stat Arb Strategies**.
- **CORE = COINTEGRATION / PAIRS TRADING.** Every other line of work serves cointegration rigor. Cointegration is law.
- Real data only: Binance public REST via `www.binance.com`. Never fabricate. Resampling cached 1h is allowed only if still from real data.
- Coasting = failure. Every action must produce checkable artifacts, tests, provenance, logs.
- Working tree: `main` clean. Do **not** commit unless explicitly requested.

## NEXT AGENT START HERE (TIMESTAMPED, MANDATORY, NO DEVIATION)
**TIMESTAMP:** 2026-11-01T18:11:33Z
**TARGET SESSION:** Next agentic work session (immediate, no ramp-up)
**PRIORITY BY REPO IDENTITY:** `cryptoquantstatarbstrats` = **Crypto Quant Stat Arb Strategies**. **CORE = COINTEGRATION/PAIRS TRADING — LAW.** All work serves cointegration rigor.

### IMMEDIATE BOOT SEQUENCE (BLOCKING - DO IN ORDER)
1. **Verify integrity (BLOCKING):** Run verification commands below. All must pass. If anything fails, fix as top priority with artifacts/tests before doing anything else.
2. **Read the law:** Re-read this handoff fully (HARD CONSTRAINTS are non-negotiable).
3. **Audit existing state:** Confirm Campaign 8 artifacts exist: `reports/execution_realism_mt.json`, `reports/turnover_slippage_mt.json`, `reports/execution_stress_grid_mt.json`. Confirm gating artifacts exist: `reports/portfolio_gating_mt.json`, `reports/portfolio_walkforward_mt.json`, `reports/portfolio_cost_stress_mt.json`, `reports/mt_blocking_matrix.json`, `reports/mt_structural_breaks_summary.json`. Confirm all cointegration-gating tests pass.
4. **Identify the gap (BLOCKING):** Campaign 9 artifacts/tests do **NOT** exist yet. This is the **ONLY** work to do now. Do not pivot to unrelated tasks.

### CONCRETE GATING STATE (DO NOT WEAKEN — from reports/portfolio_gating_mt.json)
- Universe: 17 pairs (BTC/ETH, ETH/SOL, BTC/SOL, ADA/ETH, XRP/BTC, BNB/ETH, BTC/BNB, SOL/BNB, ADA/BTC, XRP/ETH, BNB/BTC, DOT/BTC, DOT/ETH, POL/BTC, AVAX/BTC, LINK/BTC, LTC/BTC).
- 1h: 0 eligible / 17 blocked. 4h: 1 eligible (POL/BTC) / 16 blocked. 1d: 0 eligible / 17 blocked.
- Only gated-eligible pairs may receive weight/fills/capacity. Blocked pairs = zero allocation, full provenance, honest blocking.
- Campaign 9 must **preserve** this exactly: capacity/routing constraints never lift gating blocks.

### SINGLE INITIAL TASK MESSAGE (COPY/PASTE TO GUIDE THIS SESSION - MANDATORY, HEAVY)
> **OBJECTIVE (HEAVY, CAMPAIGN 9 - MANDATORY, COINTEGRATION-FIRST):** Harden execution realism for live-readiness while strictly preserving cointegration gating (fail-closed). Only real data/causal logic. No threshold weakening. No fabrication. Every gated block must remain blocked. Treat this as the sole deliverable until complete.
>
> **REQUIRED ARTIFACTS (MUST PRODUCE):** `reports/execution_capacity_mt.json`, `reports/order_routing_realism_mt.json`, `reports/live_readiness_checklist_mt.json`
>
> **REQUIRED TESTS (MUST PRODUCE):** `tests/test_execution_capacity_gating.py`, `tests/test_order_routing_schema.py`
>
> **REQUIREMENTS (HARD):**
> - **Capacity constraints:** Per (timeframe,pair) capacity from real volume where available (max notional/ADV, borrow/shortability). Derive from cached/real sources only; provenance required. Capacity constraints **NEVER** lift gating blocks. Blocked pairs remain blocked with zero allocation. Explicitly record blocked-by-gating vs capacity-blocked with rationale.
> - **Order routing realism:** Model maker/taker, queue/latency, partial fills, reject/replace tied to gating. Deterministic behavior, causal only. Enforce fail-closed: only gated-eligible pairs feasible. Reject orders for blocked pairs with full rejection_log and blocked_routes.
> - **Live-readiness checklist:** Deterministic checklist with evidence links to artifacts/tests/gates; must show blocked pairs, capacity constraints, routing constraints, provenance. Must be machine-checkable.
> - **Schema/monotonicity:** Full schema validation, monotonicity checks (worse cost/latency -> worse outcomes). No synthetic fabrication.
> - **Provenance:** Every artifact must include `real_data_only`, `fabricated_data`, `computed_at`, `source`, `gating_context`, `blocked_routes`/rationale. Link back to `reports/portfolio_gating_mt.json` and prior execution artifacts.
> - **Remove bottlenecks:** If any existing path blocks efficient progress (tests/artifacts missing, gating gaps), fix/remove bottlenecks with artifacts/tests. Do not create new bottlenecks. Coasting = failure.
>
> **COMPLETION CRITERIA (BLOCKING):** All three artifacts and both tests exist, follow schemas consistent with prior MT artifacts, preserve gating (17 blocked at 1h/1d, only POL/BTC eligible at 4h), verification commands pass (ruff + targeted pytest), and this handoff updated with concrete evidence (artifact paths, test results, counts). Do not stop until done.

## CURRENT VERIFIED STATE (2026-11-01T18:11:33Z)
- Branch: `main`. HEAD = recent checkpoint commits (clean working tree).
- **Campaign 6 DONE:** MT cointegration stability + structural-break re-validation (4h: 1/17 pass all gates [POL/BTC passes honestly]; 1d: 0/17). MT blocking matrix + structural breaks populated. Threshold invariance green.
- **Campaign 7 DONE:** Portfolio-level cointegration gating integrated MT (fail-closed, no blocked pair gets weight). Walk-forward MT + risk/cost stress MT artifacts created with provenance. Tests passing.
- **Campaign 8 DONE:** Execution realism MT (fills/slippage/fees/latency/partial/rejects, fail-closed), turnover/implementation shortfall MT, execution stress grid MT, tests added and passing. All provenance linked.
- **Campaign 9 PENDING (ACTIVE GAP - SOLE FOCUS):** Artifacts `reports/execution_capacity_mt.json`, `reports/order_routing_realism_mt.json`, `reports/live_readiness_checklist_mt.json` and tests `tests/test_execution_capacity_gating.py`, `tests/test_order_routing_schema.py` do **NOT** exist yet. This is the **ONLY** work to do now.
- Data: `data/cache/` real Binance spot 1h (2026-04-01→2026-10-30) for 14 symbols + `volume_1h_full`; offline-capable. Real data only.
- Integrity: `ruff` clean, targeted pytest passing (31 passed).

## BOTTLENECKS (REMOVED / PREVENTED)
1. MT blocking matrix + structural-breaks summary empty → populated (Campaign 6).
2. MT reports lacked `metrics` block → added; threshold-invariance pinning active (Campaign 6).
3. Ruff E501 fixed (Campaign 6).
4. Portfolio gating not MT-integrated → integrated with fail-closed enforcement + artifacts/tests (Campaign 7).
5. Walk-forward/cost-stress MT artifacts missing → created from gated results with provenance (Campaign 7).
6. Execution realism missing → created with fail-closed enforcement + tests (Campaign 8).
7. Handoff friction → single durable handoff (this file). Next-agent boot sequence explicit and unambiguous. Campaign 9 gap surfaced explicitly with hard completion criteria. Bottlenecks cannot be silently reintroduced (gating invariants tested).

## FOCUS CAMPAIGNS (HISTORY)
- Campaign 1 (DONE): Cointegration diagnostics recompute (real data)
- Campaign 2 (DONE): POL/BTC regime analysis + causal filter eval (kept blocked)
- Campaign 3 (DONE): Honest blocking audit + evidence lock-in + near-miss re-exam
- Campaign 4 (DONE): OOS robustness re-validation (0/17 pass, window-robust) + bottleneck removal
- Campaign 5 (DONE): Different-window OOS v2 + threshold-invariance lock-in + rolling stability deep-dive
- Campaign 6 (DONE): Multi-timeframe (4h/1d) rolling stability + structural-break re-validation across all 17 pairs
- Campaign 7 (DONE): Portfolio-level cointegration gating integration + walk-forward portfolio re-validation + risk-control stress on mt timeframes (1h/4h/1d)
- Campaign 8 (DONE): Execution realism + cointegration-driven execution validation (execution_realism_mt, turnover_slippage_mt, execution_stress_grid_mt + tests)
- **Campaign 9 (ACTIVE - HEAVY, DO NOT SKIP): LIVE-READY EXECUTION HARDENING + COINTEGRATION-GATED CAPACITY CONSTRAINTS** - Sole focus. Produce `execution_capacity_mt.json`, `order_routing_realism_mt.json`, `live_readiness_checklist_mt.json` + `test_execution_capacity_gating.py`, `test_order_routing_schema.py`. Preserve honest blocking: 17 pairs blocked at 1h/1d, POL/BTC only eligible at 4h.

## HARD CONSTRAINTS
- **REAL DATA ONLY** — no fabrication. Resample of cached 1h is allowed (still real data).
- **NO WEAKENING THRESHOLDS** without ironclad justification + tests. Gate thresholds unchanged: rolling ≥ 0.6, EG p ≤ 0.05, half-life (1, 500).
- **PRESERVE GREEN** — all existing tests green; ruff clean.
- **CAUSAL ONLY** — no lookahead. Trailing windows only.
- **HONEST BLOCKING** — blocked pairs receive zero weight/fills/capacity allocation; full provenance; no forced blocking.
- **FAIL-CLOSED** — capacity/routing constraints never lift gating blocks. Only gated-eligible pairs can be feasible.
- **HEAVY MANDATE** — produce artifacts/tests/logs/provenance. No coasting. If stuck, do more verification/artifacts, not less.

## VERIFICATION COMMANDS (RUN OFTEN)
```bash
python -m ruff check backtest/ strategies/ utils/ tests/ examples/ scripts/
python -m pytest tests/test_cointegration_diagnostics_schema.py tests/test_cointegration_threshold_invariance.py tests/test_portfolio_gating_mt.py tests/test_execution_gating_consistency.py tests/test_execution_realism_schema.py -v
```
