# DURABLE HANDOFF | 2026-10-31T18:12:13Z | SINGLE MANDATORY NEXT TASK

## REPO IDENTITY (LAW) — PRIORITIZE BY REPO NAME
- Repo: `cryptoquantstatarbstrats` — **Crypto Quant Stat Arb Strategies**.
- **CORE = COINTEGRATION/PAIRS TRADING.** This is the primary edge. All other work (regime, tail risk, portfolio construction) MUST serve cointegration rigor. Prioritize cointegration diagnostics above everything else.
- Real data only: Binance public REST only. Synthetic/fabricated data strictly limited to isolated unit tests with explicit `fabricated_data: true`. No silent fabrication anywhere.
- **NETWORK (unblocked via www.binance.com).** `api.binance.com` (and `api1/2/3`, `fapi.binance.com`) returns HTTP 451 and is never relied upon as a primary path. The loader's host chain tries `www.binance.com` first. Where a series still cannot be reconstructed, mark `status: "blocked_or_insufficient_data"`, populate `blocked_routes[]`, add detailed rationale + full provenance, and MOVE ON. Never fabricate.
- **Coasting = failure.** Every action must produce checkable artifacts, tests, provenance, and logs. No speculative "maybe later" without concrete next steps.

## CURRENT VERIFIED STATE (2026-10-31T18:12:13Z)
- Branch: `main` (clean). Working tree clean.
- **GREEN BASELINE (must remain):** `ruff check backtest/ strategies/ utils/ tests/ examples/` → all checks passed | `pytest tests/ -q` → **555 passed, 1 skipped** | `mypy backtest/ strategies/ utils/` → Success, no issues found.
- Artifact: `reports/portfolio_real.json` (`real_data_only: true`, `fabricated_data: false`, `n_bars: 5112`).
- `cointegration_diagnostics`: publication-grade target schema for all 17 pairs (EG/Johansen with cv90/95/99+rank, per-leg ADF/KPSS, spread hedge ratio/ADF/KPSS, half-life OU with 1<hl<500, Hurst, mr_favorable, rolling stability windows/details, structural breaks, 7-gate set, full provenance). POL/BTC passes EG+Johansen+spread_mr+hl_bounds but rolling_stability fails (all_pass False). BTC/SOL/ADA/ETH/DOT/ETH show honest hl>500 failures (never clamped).
- `parameter_stability`: per-pair entries have `top_params`, `pair_metrics`, `degradation`, `regime_notes`, `provenance`; `portfolio_level` has provenance. All real-data only.
- `tail_risk`: `portfolio` VaR/CVaR/CDaR present; `regime_conditioned` filled from real `detect_regimes` with provenance; `permutation_test` has n_permutations >= 3000.
- Modules: `utils/cointegration.py` (target schema builders, blocked_schema_diagnostics), `strategies/pairs_trading.py::get_cointegration_diagnostics` + enriched gates operationalized, `examples/run_portfolio_real.py` (passes enriched_diagnostics with `use_enriched_gates=True`, `strict_enriched_gates=True`).
- **OPERATIONALIZED:** Enriched cointegration diagnostics enforced causally in `CointegrationPairsStrategy.generate_signals()` with cached pair-level gates; strict-by-default behavior in place. Strategy enriched-gate tests exist and passing.

## CRITICAL BOTTLENECKS TO REMOVE (THIS CAMPAIGN)
1. **HEDGE RATIO ROBUSTNESS.** Rolling OLS hedge ratio is sensitive to outliers/nonstationarity; need to harden (winsorization/clipping, minimum variance guardrails, positive hedge ratio enforcement with logging) without lookahead. Must not fabricate. Document provenance.
2. **GATE COVERAGE GAPS.** Ensure all 7 gates (eg_pass, johansen_pass, spread_mr_pass, hl_bounds_pass, rolling_stable_ok, leg_stationarity_ok, structural_breaks discipline) are enforced with explicit precedence and tested under strict/non-strict. Add missing edge-case tests.
3. **CAUSALITY ENFORCEMENT.** Audit all enriched-gate paths for lookahead (cached vs per-bar). Add a test that would catch future leakage. Keep trailing-only.
4. **REAL-DATA COVERAGE.** Expand real-data validation on portfolio output (reports/portfolio_real.json) — ensure gates align with reported diagnostics; no silent promotion of blocked pairs.
5. **PERFORMANCE/CLARITY.** Remove any unnecessary recomputation; keep deterministic ordering. Preserve green.

## NEXT SESSION START POINT (EXECUTE IN ORDER, NO DRIFT)

### 0) VERIFY GREEN (MANDATORY)
```bash
export PATH=/home/runner/work/_temp/kilo-home/.local/bin:$PATH
PYTHONPATH=/home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats python -m ruff check backtest/ strategies/ utils/ tests/ examples/ && \
PYTHONPATH=/home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats python -m pytest tests/ -q && \
PYTHONPATH=/home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats python -m mypy backtest/ strategies/ utils/
```
Must remain green. If broken, fix first.

### 1) INVENTORY (FOCUS)
- Read `strategies/pairs_trading.py` fully — hedge ratio calculation, enriched gate logic, causality.
- Read `utils/cointegration.py` — gate definitions, schema.
- Read `tests/test_strategies.py` — add targeted tests for identified gaps.
- Read `reports/portfolio_real.json` — validate gate alignment with reality.

### 2) HARDEN + TEST (HEAVY WORK — CORE MISSION)
**Make cointegration enforcement bulletproof.** Cointegration is LAW.
- **Harden hedge ratio:** Add guards (rolling_var > eps, winsorize/clip beta to reasonable range e.g. [1e-6, 1e6] or pair-specific sanity), handle inf/nan, log reasons when rejecting/clamping. Never fabricate. Preserve opposing-leg weights.
- **Tighten gate enforcement:** Ensure cached diagnostics take precedence; per-bar fallback only when no cached diagnostics; strict blocks missing/None/flagged. Add tests for structural_breaks.flagged under strict (must block). Add test proving cached all_pass=False blocks entries.
- **Causality audit:** Add explicit test ensuring gates don't use future data (use synthetic series where future leakage would be detectable). Keep trailing windows only.
- **Real-data sanity:** Cross-check a few pairs from `reports/portfolio_real.json` against strategy behavior expectations; document any discrepancies with provenance.
- **Edge cases:** hl>500, rolling_stable false, leg_stationarity false — must block under strict.

### 3) VERIFY END-TO-END (MANDATORY)
```bash
export PATH=/home/runner/work/_temp/kilo-home/.local/bin:$PATH
PYTHONPATH=/home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats python -u examples/run_portfolio_real.py
PYTHONPATH=/home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats python -m pytest tests/ -q
PYTHONPATH=/home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats python -m ruff check backtest/ strategies/ utils/ tests/ examples/
PYTHONPATH=/home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats python -m mypy backtest/ strategies/ utils/
```
All must pass. Zero regressions. Do not commit unless explicitly requested.

### 4) DOCS & PROVENANCE
- Update `README.md` with hedge ratio guards and gate enforcement notes.
- Add brief comments explaining causality/strict defaults.
- Keep full provenance; no fabrication.

## SINGLE MANDATORY OBJECTIVE (HEAVY WORK REQUIRED)
**Bulletproof the cointegration gating and hedge ratio robustness in `CointegrationPairsStrategy`.** Add network-independent tests proving strict enforcement (cached gates, structural breaks, missing/None), harden rolling hedge ratio against numerical issues without lookahead, audit causality, and keep the suite green. This is the core of `cryptoquantstatarbstrats` — do the heavy lifting. No coasting.

## HARD CONSTRAINTS
- **REAL DATA ONLY** — isolated tests only with explicit `fabricated_data: true` if fabricating diagnostics
- **NO SHORTCUTS / NO FABRICATION** — omit+document with full provenance if unavailable
- **PRESERVE GREEN** — >=555 passed, 0 new failures
- **HEAVY MANDATE** — complete full campaign, no coasting
- **BOTTLENECK REMOVAL** — eliminate inefficiencies, explicitly route around 451
- **COINTEGRATION IS LAW** — prioritize above all else
- **UNBUFFERED** — use `python -u`, deterministic ordering
- **CAUSAL ONLY** — no lookahead in gates/signals
