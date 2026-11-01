# SINGLE DURABLE HANDOFF | 2026-11-01T15:06:10Z | CAMPAIGN 7 ACTIVE (PORTFOLIO GATING + WALK-FORWARD + RISK STRESS)

## REPO IDENTITY (LAW) — PRIORITIZE BY REPO NAME
- Repo: `cryptoquantstatarbstrats` — **Crypto Quant Stat Arb Strategies**.
- **CORE = COINTEGRATION / PAIRS TRADING.** Every other line of work serves cointegration rigor. Cointegration is law.
- Real data only: Binance public REST via `www.binance.com`. Never fabricate.
- Coasting = failure. Every action must produce checkable artifacts, tests, provenance, logs.
- Working tree: `main` clean. Do **not** commit unless explicitly requested.

## CURRENT VERIFIED STATE (2026-11-01T14:10:11Z)
- Branch: `main`. Up to date with `origin/main`. HEAD = `50a2e87` (chore(kilo): checkpoint agent session). Working tree clean.
- **Campaign 6 DONE (multi-timeframe cointegration stability + structural-break re-validation):**
  1. `examples/run_cointegration_diagnostics_oos_mt.py` — resamples cached 1h `data/cache/` into 4h and 1d (causal trailing `.resample("4h"/"D").last()`, no lookahead) and runs `target_schema_diagnostics` on all 17 pairs per timeframe. Reports `reports/cointegration_diagnostics_oos_mt_4h.json` and `_1d.json` with full provenance + a new per-pair `metrics` block (`eg_pvalue`, `spread_adf_pvalue`, `half_life_ou`, `hurst_exponent`, `rolling_frac_stable`, `leg1_adf_pvalue`, `leg2_adf_pvalue`). `computed_at` present per report/pair.
  2. **Honest blocking result:** 4h = **1/17 pass all gates** (`POL/BTC` passes honestly: rolling frac 0.708 ≥ 0.6, hl 30.5 in (1,500), hurst 0.491 < 0.5, eg p 4.7e-4, spread adf p 6.9e-5, no structural break). **Blocking is NOT timeframe-robust for POL/BTC** — its 1h `rolling_stable_ok` block is a 1h-specific artifact, not a universal failure. 1d = **0/17 pass all gates** (all pairs blocked, non-empty `blocked_routes`). No thresholds changed; no forced blocking.
  3. `examples/make_mt_reports.py` re-run: `reports/mt_blocking_matrix.json` (17 pairs × 1h/4h/1d: `all_pass`, `blocked_routes`, `rolling_frac_stable`, `structural_breaks_flagged`) and `reports/mt_structural_breaks_summary.json` (17 pairs × 3 timeframes: `flagged`, `breaks` with `relative_change`, causal half-sample Chow heuristic) — both fully populated.
  4. `tests/test_cointegration_threshold_invariance.py` — REPORTS list already included both mt reports; metric pinning is now active (was vacuous before the `metrics` block existed). Gate-conditioned: half-life/hurst pinned only when the corresponding gate passes; raw metric values are data-dependent, never weakened. Gate thresholds unchanged (rolling 0.6, EG 0.05, hl (1,500)).
  5. Verified: ruff clean; `tests/test_cointegration_diagnostics_schema.py` + `tests/test_cointegration_threshold_invariance.py` = **26 passed**.
- Data: `data/cache/` holds real Binance spot 1h (2026-04-01→2026-10-30) for 12 symbols (ADA, AVAX, BNB, BTC, DOT, ETH, LINK, LTC, POL, SOL, XRP). Offline-capable.

## BOTTLENECKS (ALL REMOVED / MITIGATED — NONE REMAINING)
1. mt blocking matrix + structural-breaks summary were empty stubs — now populated (17 pairs × 3 timeframes).
2. mt reports lacked `metrics` block — added; threshold-invariance pinning now active and green.
3. Ruff E501 — fixed, clean.
4. Network — offline via `data/cache/` (real public Binance 1h); `www.binance.com` preferred when available.
5. Handoff friction — this single handoff is the only starting instruction.

## SINGLE INITIAL TASK MESSAGE (START HERE — NO DEVIATION)
**OBJECTIVE (CAMPAIGN 7 — HEAVY, NON-OPTIONAL):** Portfolio-level cointegration gating integration + walk-forward portfolio re-validation across 1h/4h/1d on real cached data. Prove the portfolio respects enforced cointegration gating at every timeframe (fail-closed), that walk-forward IS/OOS degradation is measured honestly per timeframe, and that risk controls (gross exposure, per-pair caps, correlation cap, CVaR cap, drawdown circuit breaker) hold on mt data. Produce checkable artifacts, tests, and provenance. Do not coast.

**PRIORITY ORDER (EXECUTE IN ORDER):**
1. **Portfolio-level cointegration gating integration (HIGHEST ROI):** Extend/verify `examples/run_portfolio_real.py` (or a new `examples/run_portfolio_gating_mt.py`) so the multi-asset portfolio construction applies enriched cointegration gates causally per pair per timeframe: a pair is eligible for allocation at a bar only if its trailing-window diagnostic on that bar's timeframe passes `all_pass` (fail-closed); pairs blocked on any timeframe are excluded from that timeframe's book with provenance. Run on real cached data for 1h, 4h, 1d over the full cached window. Produce `reports/portfolio_gating_mt.json` with per-timeframe eligible-pair rosters, excluded pairs + blocked_routes, allocation weights, gross/net exposure, and full provenance (`real_data_only`, `fabricated_data: false`, `computed_at`, `source`). Assert: no blocked pair ever receives weight on any timeframe.
2. **Walk-forward portfolio re-validation on mt timeframes:** Walk-forward (rolling, train≈1000/test≈200 bars, ≥12 splits per timeframe) on real cached 1h/4h/1d data; report per-timeframe IS/OOS mean return, Sharpe, max drawdown, OOS/IS degradation, and aggregate across timeframes. Compare to pair-matched equal-weight buy-and-hold benchmarks per timeframe. Produce `reports/portfolio_walkforward_mt.json`. Honest: degradation recorded, never hidden; no synthetic data.
3. **Risk-control stress on mt data:** Fee × slippage grid per timeframe on the gated portfolio (0 / 0.05% / 0.10% / 0.20% fee with proportional slippage); correlation-exposure cap, CVaR cap, drawdown circuit breaker (-10%) tested on real history per timeframe. Produce `reports/portfolio_cost_stress_mt.json`. Confirm cost sensitivity is monotonic per timeframe.
4. **Tests + lock-in:** Add network-independent tests covering `portfolio_gating_mt.json` schema, fail-closed gating invariant (blocked pairs have zero weight), risk-control consistency, and artifact provenance. Ensure `tests/test_cointegration_diagnostics_schema.py`, `tests/test_cointegration_threshold_invariance.py`, and the new tests pass; ruff clean.
5. **Verify & record:** Run ruff + full targeted pytest. Update this handoff only if new hard blockers found (do not rewrite the mission).

## FOCUS CAMPAIGNS
- Campaign 1 (DONE): Cointegration diagnostics recompute (real data)
- Campaign 2 (DONE): POL/BTC regime analysis + causal filter eval (kept blocked)
- Campaign 3 (DONE): Honest blocking audit + evidence lock-in + near-miss re-exam
- Campaign 4 (DONE): OOS robustness re-validation (0/17 pass, window-robust) + bottleneck removal
- Campaign 5 (DONE): Different-window OOS v2 + threshold-invariance lock-in + rolling stability deep-dive
- Campaign 6 (DONE): Multi-timeframe (4h/1d) rolling stability + structural-break re-validation across all 17 pairs (POL/BTC passes honestly on 4h — blocking not timeframe-robust; 1d 0/17)
- Campaign 7 (ACTIVE/NEXT): Portfolio-level cointegration gating integration + walk-forward portfolio re-validation on mt timeframes

## HARD CONSTRAINTS
- **REAL DATA ONLY** — no fabrication. Resample of cached 1h is allowed (still real data); no synthetic substitution in Campaign 7 artifacts.
- **NO WEAKENING THRESHOLDS** without ironclad justification + tests. Gate thresholds unchanged: rolling ≥ 0.6, EG p ≤ 0.05, half-life (1, 500).
- **PRESERVE GREEN** — diagnostics schema tests green; threshold-invariance tests green; ruff clean.
- **CAUSAL ONLY** — no lookahead. Trailing windows only. Resample must not use future bars.
- **HONEST BLOCKING** — blocked pairs receive zero weight; `blocked_or_insufficient_data` with non-empty `blocked_routes` and full provenance; no forced blocking (POL/BTC 4h pass stands as honest evidence).
- **HEAVY MANDATE** — produce artifacts/tests/logs. No coasting.

## VERIFICATION COMMANDS
```bash
python -m ruff check backtest/ strategies/ utils/ tests/ examples/ scripts/
python -m pytest tests/test_cointegration_diagnostics_schema.py tests/test_cointegration_threshold_invariance.py -q
```

**START NOW.** Execute Campaign 7 in order. Do not wait for non-running regen.
