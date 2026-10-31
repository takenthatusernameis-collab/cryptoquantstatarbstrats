# DURABLE HANDOFF | 2026-10-31T18:28:41Z | SINGLE MANDATORY NEXT TASK

## REPO IDENTITY (LAW) — PRIORITIZE BY REPO NAME
- Repo: `cryptoquantstatarbstrats` — **Crypto Quant Stat Arb Strategies**.
- **CORE = COINTEGRATION/PAIRS TRADING.** This is the primary edge. All other work (regime, tail risk, portfolio construction) MUST serve cointegration rigor. Prioritize cointegration diagnostics above everything else.
- Real data only: Binance public REST only. Synthetic/fabricated data strictly limited to isolated unit tests with explicit `fabricated_data: true`. No silent fabrication anywhere.
- **NETWORK (unblocked via www.binance.com).** `api.binance.com` (and `api1/2/3`, `fapi.binance.com`) returns HTTP 451 and is never relied upon as a primary path. The loader's host chain tries `www.binance.com` first. Where a series still cannot be reconstructed, mark `status: "blocked_or_insufficient_data"`, populate `blocked_routes[]`, add detailed rationale + full provenance, and MOVE ON. Never fabricate.
- **Coasting = failure.** Every action must produce checkable artifacts, tests, provenance, and logs. No speculative "maybe later" without concrete next steps.

## CURRENT VERIFIED STATE (2026-10-31T18:12:13Z)
- Branch: `main` (clean). Working tree clean.
- **GREEN BASELINE (must remain):** `ruff check backtest/ strategies/ utils/ tests/ examples/` → all checks passed | `pytest tests/ -q` → **561 passed, 1 skipped** | `mypy backtest/ strategies/ utils/` → Success, no issues found.
- Artifact: `reports/portfolio_real.json` (`real_data_only: true`, `fabricated_data: false`, `n_bars: 5112`).
- `cointegration_diagnostics`: publication-grade target schema for all 17 pairs (EG/Johansen with cv90/95/99+rank, per-leg ADF/KPSS, spread hedge ratio/ADF/KPSS, half-life OU with 1<hl<500, Hurst, mr_favorable, rolling stability windows/details, structural breaks, 7-gate set, full provenance). POL/BTC passes EG+Johansen+spread_mr+hl_bounds but rolling_stability fails (all_pass False). BTC/SOL/ADA/ETH/DOT/ETH show honest hl>500 failures (never clamped).
- `parameter_stability`: per-pair entries have `top_params`, `pair_metrics`, `degradation`, `regime_notes`, `provenance`; `portfolio_level` has provenance. All real-data only.
- `tail_risk`: `portfolio` VaR/CVaR/CDaR present; `regime_conditioned` filled from real `detect_regimes` with provenance; `permutation_test` has n_permutations >= 3000.
- Modules: `utils/cointegration.py` (target schema builders, blocked_schema_diagnostics), `strategies/pairs_trading.py::get_cointegration_diagnostics` + enriched gates operationalized, `examples/run_portfolio_real.py` (passes enriched_diagnostics with `use_enriched_gates=True`, `strict_enriched_gates=True`).
- **OPERATIONALIZED:** Enriched cointegration diagnostics enforced causally in `CointegrationPairsStrategy.generate_signals()` with cached pair-level gates; strict-by-default behavior in place. Strategy enriched-gate tests exist and passing.
- **BOTTLENECKS CLEARED (this campaign):** hedge ratio guarded (winsorized/clipped to [1e-6, 1e6], positive enforcement `> 1e-18`, inf/nan handling, opposing-leg weights preserved); all 7 gates enforced with explicit precedence and tested under strict/non-strict incl. structural_breaks.flagged and cached all_pass=False blocks; causality audit complete (trailing-only windows, per-bar fallback fails closed); real-data coverage expanded and aligned with `reports/portfolio_real.json`.

## NEXT SESSION START POINT (EXECUTE IN ORDER, NO DRIFT)

### 0) VERIFY GREEN (MANDATORY)
```bash
export PATH=/home/runner/work/_temp/kilo-home/.local/bin:$PATH
PYTHONPATH=/home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats python -m ruff check backtest/ strategies/ utils/ tests/ examples/ && \
PYTHONPATH=/home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats python -m pytest tests/ -q && \
PYTHONPATH=/home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats python -m mypy backtest/ strategies/ utils/
```
Must remain green. If broken, fix first.

### 1) FOCUS CAMPAIGN — COINTEGRATION FAIL-CLOSED BY DEFAULT (HEAVY WORK — CORE MISSION)
**Make cointegration enforcement unavoidable.** Cointegration is LAW; the strategy must never silently trade a non-cointegrated pair.
- **Flip the enriched-gate default:** `use_enriched_gates` currently defaults to `False` in `strategies/pairs_trading.py:47`, so gates are opt-in. Change the default to `True` (fail-closed) so `CointegrationPairsStrategy` enforces the 7 enriched gates unless explicitly opted out. Update `__init__` docstring and README accordingly.
- **Gate enforcement audit:** Confirm cached diagnostics take precedence; per-bar fallback only when no cached diagnostics; strict blocks missing/None/flagged. `structural_breaks.flagged is True` must block under strict. `all_pass=False` cached must block entries.
- **Causality test:** Add an explicit test proving gates use trailing data only (no lookahead), using a synthetic series where future leakage would flip `enriched_gates_ok`. Keep trailing windows only.
- **Hedge ratio hardening (re-verify):** rolling_var > eps guard, winsorize/clip beta `[1e-6, 1e6]`, positive enforcement, log reject/clamp reasons. Preserve opposing-leg weights. No lookahead.
- **Edge cases under strict:** hl>500, rolling_stable false, leg_stationarity false must all block entries.
- **Tests:** Add targeted tests in `tests/test_strategies.py` for the new default, structural breaks flagged, missing/None gates, causality, and hedge ratio guards.

### 2) VERIFY END-TO-END (MANDATORY)
```bash
export PATH=/home/runner/work/_temp/kilo-home/.local/bin:$PATH
PYTHONPATH=/home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats python -u examples/run_portfolio_real.py
PYTHONPATH=/home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats python -m pytest tests/ -q
PYTHONPATH=/home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats python -m ruff check backtest/ strategies/ utils/ tests/ examples/
PYTHONPATH=/home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats python -m mypy backtest/ strategies/ utils/
```
All must pass. Zero regressions. Do not commit unless explicitly requested.

### 3) DOCS & PROVENANCE
- Update `README.md` with the new `use_enriched_gates` default and gate enforcement notes.
- Add brief comments explaining causality/strict defaults.
- Keep full provenance; no fabrication.

## SINGLE MANDATORY OBJECTIVE (HEAVY WORK REQUIRED)
**Make the cointegration gate fail-closed by default in `CointegrationPairsStrategy` and keep it bulletproof.** Flip `use_enriched_gates` to `True`, harden the rolling hedge ratio against numerical issues without lookahead, add a causality test proving no future leakage, test structural-breaks/missing/None gating, and keep the suite green. This is the core of `cryptoquantstatarbstrats` — do the heavy lifting. No coasting.

## HARD CONSTRAINTS
- **REAL DATA ONLY** — isolated tests only with explicit `fabricated_data: true` if fabricating diagnostics
- **NO SHORTCUTS / NO FABRICATION** — omit+document with full provenance if unavailable
- **PRESERVE GREEN** — >=555 passed, 0 new failures
- **HEAVY MANDATE** — complete full campaign, no coasting
- **BOTTLENECK REMOVAL** — eliminate inefficiencies, explicitly route around 451
- **COINTEGRATION IS LAW** — prioritize above all else
- **UNBUFFERED** — use `python -u`, deterministic ordering
- **CAUSAL ONLY** — no lookahead in gates/signals
