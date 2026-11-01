# SINGLE DURABLE HANDOFF | 2026-11-01T16:04:30Z | CAMPAIGN 7 COMPLETE (PORTFOLIO GATING + WALK-FORWARD + RISK STRESS) | NEXT: CAMPAIGN 8 (EXECUTION REALISM + LIVE-READY COINTEGRATION VALIDATION)

## REPO IDENTITY (LAW) — PRIORITIZE BY REPO NAME
- Repo: `cryptoquantstatarbstrats` — **Crypto Quant Stat Arb Strategies**.
- **CORE = COINTEGRATION / PAIRS TRADING.** Every other line of work serves cointegration rigor. Cointegration is law.
- Real data only: Binance public REST via `www.binance.com`. Never fabricate. Resampling cached 1h is allowed only if still from real data.
- Coasting = failure. Every action must produce checkable artifacts, tests, provenance, logs.
- Working tree: `main` clean. Do **not** commit unless explicitly requested.

## NEXT AGENT START HERE (TIMESTAMPED, MANDATORY, NO DEVIATION)
**TIMESTAMP:** 2026-11-01T16:04:30Z
**TARGET SESSION:** Next agentic work session (immediate)
**MISSION:** Continue enforcing cointegration law with heavy, verifiable work. Preserve all green state. Remove any remaining friction. Build forward only with evidence.

### IMMEDIATE BOOT SEQUENCE (MUST DO FIRST)
1. **Verify integrity (blocking):** Run the verification commands below. All must pass. If anything fails, fix it as the top priority with artifacts/tests before doing anything else.
2. **Read the law:** Re-read this handoff fully. Treat HARD CONSTRAINTS as non-negotiable.
3. **Audit artifacts:** Confirm `reports/portfolio_gating_mt.json`, `reports/portfolio_walkforward_mt.json`, `reports/portfolio_cost_stress_mt.json`, `reports/mt_blocking_matrix.json`, `reports/mt_structural_breaks_summary.json`, `reports/cointegration_diagnostics_oos_mt_4h.json`, `reports/cointegration_diagnostics_oos_mt_1d.json` exist and are valid JSON with provenance.
4. **Do not speculate blindly:** Only extend if new real data/windows appear OR if explicitly needed to close a concrete gap that would violate cointegration rigor. Otherwise execute Campaign 8 as specified.

### SINGLE INITIAL TASK MESSAGE (COPY/PASTE TO GUIDE WORK)
> **OBJECTIVE (HEAVY):** Extend cointegration-driven pairs trading validation to execution realism using ONLY real data. Enforce fail-closed gating end-to-end. Every eligible allocation must remain traceable to passing enriched gates per (pair, timeframe). No threshold weakening. No fabrication. Produce artifacts, tests, provenance, and logs for every step. Coasting = failure.

## CURRENT VERIFIED STATE (2026-11-01T15:07:00Z)
- Branch: `main`. Up to date with `origin/main`. HEAD = `50a2e87` (chore(kilo): checkpoint agent session). Working tree clean.
- **Campaign 6 DONE:** MT cointegration stability + structural-break re-validation (4h: 1/17 pass all gates [POL/BTC passes honestly]; 1d: 0/17). MT blocking matrix + structural breaks populated. Threshold invariance green.
- **Campaign 7 DONE:** Portfolio-level cointegration gating integrated MT (fail-closed, no blocked pair gets weight). Walk-forward MT + risk/cost stress MT artifacts created with provenance. Tests passing.
- Data: `data/cache/` real Binance spot 1h (2026-04-01→2026-10-30) for 12 symbols; offline-capable.

## BOTTLENECKS (REMOVED / PREVENTED)
1. MT blocking matrix + structural-breaks summary empty → populated (Campaign 6).
2. MT reports lacked `metrics` block → added; threshold-invariance pinning active (Campaign 6).
3. Ruff E501 fixed (Campaign 6).
4. Portfolio gating not MT-integrated → integrated with fail-closed enforcement + artifacts/tests (Campaign 7).
5. Walk-forward/cost-stress MT artifacts missing → created from gated results with provenance (Campaign 7).
6. Handoff friction → single durable handoff (this file). Next-agent boot sequence explicit. Bottlenecks cannot be silently reintroduced (gating invariant tested).

## FOCUS CAMPAIGNS
- Campaign 1 (DONE): Cointegration diagnostics recompute (real data)
- Campaign 2 (DONE): POL/BTC regime analysis + causal filter eval (kept blocked)
- Campaign 3 (DONE): Honest blocking audit + evidence lock-in + near-miss re-exam
- Campaign 4 (DONE): OOS robustness re-validation (0/17 pass, window-robust) + bottleneck removal
- Campaign 5 (DONE): Different-window OOS v2 + threshold-invariance lock-in + rolling stability deep-dive
- Campaign 6 (DONE): Multi-timeframe (4h/1d) rolling stability + structural-break re-validation across all 17 pairs
- Campaign 7 (COMPLETE): Portfolio-level cointegration gating integration + walk-forward portfolio re-validation + risk-control stress on mt timeframes (1h/4h/1d)
- **Campaign 8 (NEXT - HEAVY, DO NOT SKIP): EXECUTION REALISM + COINTEGRATION-DRIVEN EXECUTION VALIDATION**
  - **Goal:** Make the cointegration-gated MT portfolio execution-realistic using only real data/causal logic. Force heavy, verifiable artifacts.
  - **Required artifacts (must produce):**
    1. `reports/execution_realism_mt.json` - Per (timeframe,pair), slippage/fee/tick/lot aware fills, latency assumptions grounded, partial fills, rejection logic, borrow/fee realism where applicable. Must show **only gated-eligible pairs** get fills; blocked pairs have `execution_blocked_by_gating: true` with routes.
    2. `reports/turnover_slippage_mt.json` - Turnover decomposition, implementation shortfall decomposition by component, daily/rolling, linked to walk-forward windows. Provenance to `portfolio_gating_mt.json` + `portfolio_walkforward_mt.json`.
    3. `reports/execution_stress_grid_mt.json` - Expanded fee×slippage×impact grid across 1h/4h/1d; monotonicity enforced; breakeven analysis; fail if any eligible pair becomes untradable under stress without being re-gated honestly.
  - **Required tests (must add/pass):**
    1. `tests/test_execution_gating_consistency.py` - Fail-closed: execution never allocates to non-eligible/gated-blocked pairs; cross-check against gating artifact invariants.
    2. `tests/test_execution_realism_schema.py` - Schema validation, provenance links, required fields, monotonicity checks.
  - **Discipline:** Causal only, real data/resample only, no threshold weakening, preserve all existing green tests. Update this handoff with evidence on completion.

## HARD CONSTRAINTS
- **REAL DATA ONLY** — no fabrication. Resample of cached 1h is allowed (still real data).
- **NO WEAKENING THRESHOLDS** without ironclad justification + tests. Gate thresholds unchanged: rolling ≥ 0.6, EG p ≤ 0.05, half-life (1, 500).
- **PRESERVE GREEN** — all existing tests green; ruff clean.
- **CAUSAL ONLY** — no lookahead. Trailing windows only.
- **HONEST BLOCKING** — blocked pairs receive zero weight/fills; full provenance; no forced blocking.
- **HEAVY MANDATE** — produce artifacts/tests/logs. No coasting. If stuck, do more verification/artifacts, not less.

## VERIFICATION COMMANDS (RUN OFTEN)
```bash
python -m ruff check backtest/ strategies/ utils/ tests/ examples/ scripts/
python -m pytest tests/test_cointegration_diagnostics_schema.py tests/test_cointegration_threshold_invariance.py tests/test_portfolio_gating_mt.py -v
```

**STATE: STABLE. Campaign 7 complete. Campaign 8 ready to execute with heavy mandate. No blocking issues.**
