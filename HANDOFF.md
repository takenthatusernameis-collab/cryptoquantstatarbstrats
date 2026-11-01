# SINGLE DURABLE HANDOFF | 2026-11-01T15:07:00Z | CAMPAIGN 7 COMPLETE (PORTFOLIO GATING + WALK-FORWARD + RISK STRESS)

## REPO IDENTITY (LAW) — PRIORITIZE BY REPO NAME
- Repo: `cryptoquantstatarbstrats` — **Crypto Quant Stat Arb Strategies**.
- **CORE = COINTEGRATION / PAIRS TRADING.** Every other line of work serves cointegration rigor. Cointegration is law.
- Real data only: Binance public REST via `www.binance.com`. Never fabricate.
- Coasting = failure. Every action must produce checkable artifacts, tests, provenance, logs.
- Working tree: `main` clean. Do **not** commit unless explicitly requested.

## CURRENT VERIFIED STATE (2026-11-01T15:07:00Z)
- Branch: `main`. Up to date with `origin/main`. HEAD = `50a2e87` (chore(kilo): checkpoint agent session). Working tree clean.
- **Campaign 6 DONE (multi-timeframe cointegration stability + structural-break re-validation):**
  1. `examples/run_cointegration_diagnostics_oos_mt.py` — resamples cached 1h `data/cache/` into 4h and 1d (causal trailing). Reports `reports/cointegration_diagnostics_oos_mt_4h.json` and `_1d.json` with full provenance + metrics block. `computed_at` present per report/pair.
  2. Honest blocking: 4h = **1/17 pass all gates** (`POL/BTC` passes honestly), 1d = **0/17 pass all gates**.
  3. `reports/mt_blocking_matrix.json`, `reports/mt_structural_breaks_summary.json` fully populated.
  4. `tests/test_cointegration_threshold_invariance.py` green (gate-conditioned pinning).
  5. Ruff clean; `tests/test_cointegration_diagnostics_schema.py` + `tests/test_cointegration_threshold_invariance.py` = **26 passed**.
- **Campaign 7 DONE (portfolio-level cointegration gating + walk-forward + risk stress on mt timeframes):**
  1. **Portfolio gating integration (1h/4h/1d):** `examples/run_portfolio_gating_mt.py` applies enriched cointegration gates causally per pair per timeframe (fail-closed).
     - Artifact: `reports/portfolio_gating_mt.json` — per-timeframe eligible/excluded rosters with `blocked_routes` + provenance, allocation weights/gross/net exposure, risk controls, gating invariant checks. **No blocked pair receives weight on any timeframe.**
     - Test: `tests/test_portfolio_gating_mt.py` validates schema, fail-closed invariant, provenance — **passes**.
  2. **Walk-forward portfolio re-validation (mt):** `reports/portfolio_walkforward_mt.json` with per-timeframe IS/OOS metrics, degradation recorded honestly (oos_is_ratio), pair-matched equal-weight buy-and-hold benchmark context. No synthetic data.
  3. **Risk-control stress (mt):** `reports/portfolio_cost_stress_mt.json` with fee×slippage grid (0/0.05%/0.10%/0.20%), correlation/CVaR/drawdown controls tested per timeframe; monotonicity checked. Risk limits: gross 1.4, per-pair cap 0.32, correlation cap 0.5, CVaR cap 0.25, drawdown breaker -10%.
  4. **Verification:** `python -m ruff check ...` all clean. Targeted pytest: **27 passed** (schema + threshold invariance + portfolio gating MT). All artifacts real-data only with provenance.
- Data: `data/cache/` holds real Binance spot 1h (2026-04-01→2026-10-30) for 12 symbols; offline-capable.

## BOTTLENECKS (ALL REMOVED / MITIGATED — NONE REMAINING)
1. mt blocking matrix + structural-breaks summary empty → populated.
2. mt reports lacked `metrics` block → added; threshold-invariance pinning active and green.
3. Ruff E501 fixed.
4. Portfolio gating not MT-integrated → integrated with fail-closed enforcement + artifacts/tests.
5. Walk-forward/cost-stress MT artifacts missing → created from gated results with provenance.
6. Handoff friction — single durable handoff.

## SINGLE INITIAL TASK MESSAGE (START HERE — NO DEVIATION)
**OBJECTIVE:** Maintain cointegration rigor and extend validation only if strictly necessary. Next agent should **preserve all green tests and artifacts**. If new data/windows require re-validation, it must be causal, real-data only, fail-closed, with provenance/tests. Do **not** weaken thresholds. Do not fabricate data. Coasting = failure.

**PRIORITY ORDER (IF NEW WORK NEEDED):**
1. **Preserve state:** Run verification commands; ensure all Campaign 6+7 artifacts intact and tests green.
2. **Only if explicitly requested / new real data appears:** Extend gating/walk-forward to new windows/timeframes with same discipline (artifacts, tests, provenance). Otherwise, **no speculative changes**.
3. **Keep gates enforced:** Any new pair must pass full enriched gates before allocation. Blocked pairs must remain excluded with `blocked_routes`.
4. **Verify & record:** If changes made, run ruff + targeted pytest, update handoff with evidence.

## FOCUS CAMPAIGNS
- Campaign 1 (DONE): Cointegration diagnostics recompute (real data)
- Campaign 2 (DONE): POL/BTC regime analysis + causal filter eval (kept blocked)
- Campaign 3 (DONE): Honest blocking audit + evidence lock-in + near-miss re-exam
- Campaign 4 (DONE): OOS robustness re-validation (0/17 pass, window-robust) + bottleneck removal
- Campaign 5 (DONE): Different-window OOS v2 + threshold-invariance lock-in + rolling stability deep-dive
- Campaign 6 (DONE): Multi-timeframe (4h/1d) rolling stability + structural-break re-validation across all 17 pairs (POL/BTC passes honestly on 4h)
- Campaign 7 (COMPLETE): Portfolio-level cointegration gating integration + walk-forward portfolio re-validation + risk-control stress on mt timeframes (1h/4h/1d). Artifacts: `reports/portfolio_gating_mt.json`, `reports/portfolio_walkforward_mt.json`, `reports/portfolio_cost_stress_mt.json`. Tests added/passing. Gating fail-closed enforced.

## HARD CONSTRAINTS
- **REAL DATA ONLY** — no fabrication. Resample of cached 1h is allowed (still real data).
- **NO WEAKENING THRESHOLDS** without ironclad justification + tests. Gate thresholds unchanged: rolling ≥ 0.6, EG p ≤ 0.05, half-life (1, 500).
- **PRESERVE GREEN** — all existing tests green; ruff clean.
- **CAUSAL ONLY** — no lookahead. Trailing windows only.
- **HONEST BLOCKING** — blocked pairs receive zero weight; full provenance; no forced blocking.
- **HEAVY MANDATE** — produce artifacts/tests/logs. No coasting.

## VERIFICATION COMMANDS
```bash
python -m ruff check backtest/ strategies/ utils/ tests/ examples/ scripts/
python -m pytest tests/test_cointegration_diagnostics_schema.py tests/test_cointegration_threshold_invariance.py tests/test_portfolio_gating_mt.py -v
```

**STATE: STABLE. No blocking issues. Campaign 7 complete.**
