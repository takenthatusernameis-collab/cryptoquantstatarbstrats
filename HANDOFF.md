TIMESTAMP: 2026-11-04T10:53:13Z | REPO: cryptoquantstatarbstrats
# PRIORITY: CROSS-STRATEGY PUBLICATION-GRADE REAL-MARKET VALIDATION & PARITY LOCK (NEXT CAMPAIGN) — STAT-ARB PARITY & DIAGNOSTICS HARDENING IS COMPLETE & VERIFIED
# STATUS: STAT-ARB PARITY & DIAGNOSTICS HARDENING CAMPAIGN FINALIZED — NEXT CAMPAIGN ARMED

> **SINGLE SOURCE OF TRUTH. THIS SUPERSEDES ALL PREVIOUS HANDOFF ENTRIES. READ THIS FIRST. NO OTHER PRIORITY FILES.**

## COMPLETED CAMPAIGN RECORD (STAT-ARB STRATEGY PARITY & DIAGNOSTICS HARDENING — FINAL, 2026-11-04T10:53:13Z)

**VERIFIED STATE:**
- Full suite: **813 passed, 1 skipped, 0 failures** (was 802/1/0 at campaign start; all five strategy parity tests added and passing)
- Cointegration parity regression: 9/9 passed; all cointegration tests 146 passed; strategies tests 55 passed
- Lint/mypy: mypy clean on touched modules; ruff clean

**SECTION-5 DISCIPLINE ITEMS — ALL IMPLEMENTED IN CODE (verified by read):**
- [x] `strategies/mean_reversion.py`: `_evaluate_enriched_gates_strict` fail-closed (None/missing gates block; flagged=True blocks; flagged=None/missing structural_breaks blocks under strict; no `or True` / `is None -> True` coercion); `_build_diagnostics` returns `{gates, structural_breaks, provenance, blocked_routes, cost_stress, cost_grid}` real-data-only; `generate_signals` defaults `use_enriched_gates=True`, `strict_enriched_gates=True`; missing/failed diagnostics block entries.
- [x] `strategies/momentum.py`: same fail-closed diagnostics + gating + defaults.
- [x] `strategies/term_structure.py`: same fail-closed diagnostics + gating + defaults (IV tenor spread; resolves `iv_30d`/`iv_90d`).
- [x] `strategies/volatility_surface.py`: same fail-closed diagnostics + gating + defaults (IV percentile regime).
- [x] `strategies/cross_exchange.py`: same fail-closed diagnostics + gating + defaults (relative spread across two exchange columns; explicit gross-normalized weights).
- [x] Parity tests per strategy using shared helper `tests/cointegration_parity.assert_cached_vs_perbar_gate_parity_strict()`:
  - `tests/test_mean_reversion_parity_regression.py`
  - `tests/test_momentum_parity_regression.py`
  - `tests/test_term_structure_parity_regression.py`
  - `tests/test_volatility_surface_parity_regression.py`
  - `tests/test_cross_exchange_parity_regression.py`
- [x] Provenance + blocked-route coverage: cache hits replay provenance; blocked routes never masked; real-data-only, `fabricated_data: false`.

**BOTTLENECKS — ALL REMOVED:** No fail-open coercions remain in any strategy; zero ad-hoc parity checks outside the shared helper; all five strategies meet the cointegration publication-grade bar.

## INITIAL TASK MESSAGE FOR NEXT AGENTIC WORK SESSION (START HERE - DO NOT SKIP)

**TIMESTAMP:** 2026-11-04T10:53:13Z
**REPO:** `cryptoquantstatarbstrats` (= Crypto Quant Stat Arb Strategies — stat-arb strategies, plural)
**MANDATE:** You are working the **CROSS-STRATEGY PUBLICATION-GRADE REAL-MARKET VALIDATION & PARITY LOCK** campaign. Execution > narration. Ship code + tests + real-data evidence or do not stop. Every strategy in this repo (`mean_reversion`, `momentum`, `term_structure`, `volatility_surface`, `cross_exchange`, plus `CointegrationPairsStrategy`) must be validated on real public Binance spot candles with the same fail-closed gate discipline, or it is a weak link.

**REPO SIGNAL (WHY THIS CAMPAIGN):** `cryptoquantstatarbstrats` = Crypto Quant Stat Arb Strategies, plural. The per-strategy parity & diagnostics hardening campaign is complete and verified (813/1/0): all five non-pairs strategies now emit enriched diagnostics with fail-closed enriched-gate enforcement and shared parity tests. What remains is end-to-end real-market validation parity across all strategies: real-data walk-forward sweeps, full-dataset replays, transaction-cost sensitivity grids, execution realism, and a cross-strategy portfolio, each with ironclad provenance (`real_data_only: true`, `fabricated_data: false`) and regression tests that auto-reject any regression. Pairs already has `reports/pairs_real_market.json` + `examples/run_pairs_multi.py`; mean reversion has `reports/mean_reversion_real_market.json` + `examples/run_mean_reversion_real.py`. The remaining strategies and the cross-strategy rollup need equivalent real-data evidence + regression locks.

**IMMEDIATE MISSION (UNSKIPPABLE, P0):**
For each of `momentum`, `term_structure`, `volatility_surface`, `cross_exchange` (and re-confirm `mean_reversion`):
1. Real-data walk-forward sweep + full-dataset replay on public Binance spot candles (1h, BTC/ETH/SOL where applicable; term_structure needs real `iv_30d`/`iv_90d` columns — CLI must not fabricate IV), producing a `reports/<strategy>_real_market.json` artifact with schema: walk-forward table, replay block (total_return, sharpe_ratio, max_drawdown, calmar_ratio, final_equity), buy-and-hold benchmark, cost_sensitivity grid (fees × slippage), full provenance (`real_data_only`, `fabricated_data: false`, `computed_at`, `blocked_routes`, `rationale`). Never fabricate candles/IV/volume.
2. Reproduce via an `examples/run_<strategy>_real.py` script (mirror `examples/run_mean_reversion_real.py`) that runs end-to-end with `DataLoader.load_binance_data()`.
3. Add a regression test `tests/test_<strategy>_real_market_regression.py` asserting the artifact schema, `real_data_only: true`, `fabricated_data: false`, non-empty blocked-routes provenance, and that replay metrics are present and finite — no synthetic data as evidence (synthetic only when explicitly flagged `fabricated_data: true`).
4. Cross-strategy parity lock: extend/add a `tests/test_cross_strategy_parity_lock.py` asserting all strategies share the same fail-closed gate contract (`use_enriched_gates=True`/`strict_enriched_gates=True` defaults; `None`/missing gates block; `flagged=True` blocks; `flagged=None`/missing `structural_breaks` blocks under strict; no `or True` / `is None -> True`) and cached-vs-per-bar gate parity via the shared helper — zero bespoke parity assertions.
5. Real-data-only evidence mandate: no synthetic/fabricated candles/IV/volume as evidence for any new artifact or test.

**FAIL CONDITIONS (AUTO-REJECT TERMINATION):**
- Any new strategy code with fail-open coercion (`or True`, `is None: True`, ternaries collapsing None/False to pass)
- Any strategy emitting entries without fail-closed enriched-gate enforcement under `strict_enriched_gates=True`
- Any cached-vs-per-bar comparison outside the shared parity helper (bespoke `assert` blocks forbidden)
- Any real-market artifact or test using synthetic/fabricated data as evidence without explicit `fabricated_data: true` flag
- Ending without >=1 real-market artifact + regression test per strategy (`momentum`, `term_structure`, `volatility_surface`, `cross_exchange`) and the cross-strategy parity lock test
- Weakening `use_enriched_gates`, `strict_enriched_gates`, provenance, or real-data requirements
- Leaving any strategy without `reports/<strategy>_real_market.json` + `examples/run_<strategy>_real.py` + regression test

**EXECUTE IN THIS EXACT ORDER (NO DETOUR):**

### 1) BASELINE VERIFICATION (FAIL FAST)
```bash
cd /home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats
python -m pytest tests/ -q
```
**MUST BE GREEN (813/1/0 or better).** Fix regressions before proceeding.

### 2) AUDIT EXISTING REAL-MARKET ARTIFACTS (P0)
Confirm what exists per strategy:
- `reports/pairs_real_market.json` + `examples/run_pairs_multi.py` (pairs — exists)
- `reports/mean_reversion_real_market.json` + `examples/run_mean_reversion_real.py` (mean reversion — exists)
- `reports/<strategy>_real_market.json` + `examples/run_<strategy>_real.py` for momentum, term_structure, volatility_surface, cross_exchange (gap to close)
- `reports/portfolio_real.json` + `examples/run_portfolio_real.py` (cross-strategy portfolio — exists; confirm schema)

### 3) BUILD REAL-MARKET ARTIFACTS + RUN SCRIPTS PER STRATEGY (P0)
Per strategy: walk-forward sweep + replay + cost-sensitivity grid on real Binance spot candles → `reports/<strategy>_real_market.json` + `examples/run_<strategy>_real.py`, full provenance, real-data-only.

### 4) ADD REGRESSION TESTS PER STRATEGY + CROSS-STRATEGY PARITY LOCK (P0)
`tests/test_<strategy>_real_market_regression.py` per strategy + `tests/test_cross_strategy_parity_lock.py` enforcing the shared fail-closed gate contract and cached-vs-per-bar parity via `tests/cointegration_parity.assert_cached_vs_perbar_gate_parity_strict()`.

### 5) VERIFY, LINT, TYPECHECK, SHIP WITH EVIDENCE (MANDATORY)
```bash
python -m pytest tests/ -q
python -m ruff check strategies/ backtest/ utils/ tests/ examples/ data/
python -m mypy backtest strategies utils data
```
**DO NOT END UNTIL ALL PASS.** Report files changed, artifacts added per strategy, tests added, and verification results.

## CURRENT VERIFIED STATE (2026-11-04T10:53:13Z)
- Stat-arb parity & diagnostics hardening: COMPLETE & VERIFIED (813 passed, 1 skipped, 0 failures; all 5 strategies hardened; parity tests present)
- Next campaign: CROSS-STRATEGY PUBLICATION-GRADE REAL-MARKET VALIDATION & PARITY LOCK — ARMED, NOT STARTED
- Strategies needing real-market artifacts: momentum, term_structure, volatility_surface, cross_exchange

## DISCIPLINE (NON-NEGOTIABLE)
- **HEAVY WORK REQUIRED.** No audit-only, no summary-only termination.
- **TRACE BEFORE CHANGE.** Read source+tests to understand causality.
- **FAIL-CLOSED.** Never weaken `use_enriched_gates`, `strict_enriched_gates`, provenance, or real-data requirements.
- **PARITY IS LAW.** Use `tests/cointegration_parity.assert_cached_vs_perbar_gate_parity_strict()` for all cached-vs-per-bar gate parity. No bespoke parity assertions.
- **NO COERCION.** `or True`, `is None -> True`, equivalent forbidden.
- **REAL-DATA ONLY.** `real_data_only: true`, `fabricated_data: false` for all evidence; synthetic only when explicitly flagged `fabricated_data: true`.
- **PUBLICATION-GRADE.** Full provenance, evidence required, every strategy held to the same bar.
- **SINGLE HANDOFF.** This file is the only durable handoff.
