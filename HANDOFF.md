# SINGLE DURABLE HANDOFF | 2026-11-01T17:06:30Z | CAMPAIGN 8 COMPLETE | NEXT: CAMPAIGN 9 (LIVE-READY EXECUTION HARDENING + COINTEGRATION-GATED CAPACITY CONSTRAINTS)

## REPO IDENTITY (LAW) — PRIORITIZE BY REPO NAME
- Repo: `cryptoquantstatarbstrats` — **Crypto Quant Stat Arb Strategies**.
- **CORE = COINTEGRATION / PAIRS TRADING.** Every other line of work serves cointegration rigor. Cointegration is law.
- Real data only: Binance public REST via `www.binance.com`. Never fabricate. Resampling cached 1h is allowed only if still from real data.
- Coasting = failure. Every action must produce checkable artifacts, tests, provenance, logs.
- Working tree: `main` clean. Do **not** commit unless explicitly requested.

## NEXT AGENT START HERE (TIMESTAMPED, MANDATORY, NO DEVIATION)
**TIMESTAMP:** 2026-11-01T17:06:30Z
**TARGET SESSION:** Next agentic work session (immediate)
**MISSION:** Execute Campaign 9 with heavy, verifiable work. Enforce cointegration gating (fail-closed). Remove friction. Produce required artifacts/tests. No coasting.

### IMMEDIATE BOOT SEQUENCE (MUST DO FIRST)
1. **Verify integrity (blocking):** Run verification commands below. All must pass. If anything fails, fix as top priority with artifacts/tests before doing anything else.
2. **Read the law:** Re-read this handoff fully. Treat HARD CONSTRAINTS as non-negotiable.
3. **Audit existing state:** Confirm Campaign 8 artifacts exist: `reports/execution_realism_mt.json`, `reports/turnover_slippage_mt.json`, `reports/execution_stress_grid_mt.json`. Confirm gating artifacts exist: `reports/portfolio_gating_mt.json`, `reports/portfolio_walkforward_mt.json`, `reports/portfolio_cost_stress_mt.json`, `reports/mt_blocking_matrix.json`, `reports/mt_structural_breaks_summary.json`.
4. **Identify the gap (blocking):** Campaign 9 artifacts/tests do **NOT** exist yet. This is the only work to do. Do not pivot to unrelated tasks.

### SINGLE INITIAL TASK MESSAGE (COPY/PASTE TO GUIDE WORK)
> **OBJECTIVE (HEAVY, CAMPAIGN 9 - MANDATORY):** Harden execution realism for live-readiness while strictly preserving cointegration gating (fail-closed). Only real data/causal logic. No threshold weakening. No fabrication.
> **REQUIRED ARTIFACTS:** `reports/execution_capacity_mt.json`, `reports/order_routing_realism_mt.json`, `reports/live_readiness_checklist_mt.json`
> **REQUIRED TESTS:** `tests/test_execution_capacity_gating.py`, `tests/test_order_routing_schema.py`
> **REQUIREMENTS:** Per (timeframe,pair) capacity constraints from real volume where available (max notional/ADV, borrow/shortability), order routing realism (maker/taker, queue/latency, partial fills, reject/replace) tied to gating, deterministic live-readiness checklist with evidence links. Blocked pairs must remain blocked (capacity never lifts gates). Full provenance, schema validation, monotonicity checks. Update this handoff with evidence on completion. Coasting = failure.

## CURRENT VERIFIED STATE (2026-11-01T17:06:30Z)
- Branch: `main`. HEAD = recent checkpoint commits (clean working tree).
- **Campaign 6 DONE:** MT cointegration stability + structural-break re-validation (4h: 1/17 pass all gates [POL/BTC passes honestly]; 1d: 0/17). MT blocking matrix + structural breaks populated. Threshold invariance green.
- **Campaign 7 DONE:** Portfolio-level cointegration gating integrated MT (fail-closed, no blocked pair gets weight). Walk-forward MT + risk/cost stress MT artifacts created with provenance. Tests passing.
- **Campaign 8 DONE:** Execution realism MT (fills/slippage/fees/latency/partial/rejects, fail-closed), turnover/implementation shortfall MT, execution stress grid MT, tests added and passing. All provenance linked.
- **Campaign 9 PENDING:** Artifacts and tests do not exist. This is the next heavy work.
- Data: `data/cache/` real Binance spot 1h (2026-04-01→2026-10-30) for 12 symbols; offline-capable.

## BOTTLENECKS (REMOVED / PREVENTED)
1. MT blocking matrix + structural-breaks summary empty → populated (Campaign 6).
2. MT reports lacked `metrics` block → added; threshold-invariance pinning active (Campaign 6).
3. Ruff E501 fixed (Campaign 6).
4. Portfolio gating not MT-integrated → integrated with fail-closed enforcement + artifacts/tests (Campaign 7).
5. Walk-forward/cost-stress MT artifacts missing → created from gated results with provenance (Campaign 7).
6. Execution realism missing → created with fail-closed enforcement + tests (Campaign 8).
7. Handoff friction → single durable handoff (this file). Next-agent boot sequence explicit and unambiguous. Campaign 9 gap surfaced explicitly. Bottlenecks cannot be silently reintroduced (gating invariants tested).

## FOCUS CAMPAIGNS (HISTORY)
- Campaign 1 (DONE): Cointegration diagnostics recompute (real data)
- Campaign 2 (DONE): POL/BTC regime analysis + causal filter eval (kept blocked)
- Campaign 3 (DONE): Honest blocking audit + evidence lock-in + near-miss re-exam
- Campaign 4 (DONE): OOS robustness re-validation (0/17 pass, window-robust) + bottleneck removal
- Campaign 5 (DONE): Different-window OOS v2 + threshold-invariance lock-in + rolling stability deep-dive
- Campaign 6 (DONE): Multi-timeframe (4h/1d) rolling stability + structural-break re-validation across all 17 pairs
- Campaign 7 (DONE): Portfolio-level cointegration gating integration + walk-forward portfolio re-validation + risk-control stress on mt timeframes (1h/4h/1d)
- Campaign 8 (DONE): Execution realism + cointegration-driven execution validation (execution_realism_mt, turnover_slippage_mt, execution_stress_grid_mt + tests)
- **Campaign 9 (ACTIVE - HEAVY, DO NOT SKIP): LIVE-READY EXECUTION HARDENING + COINTEGRATION-GATED CAPACITY CONSTRAINTS** - See NEXT AGENT START HERE.

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
