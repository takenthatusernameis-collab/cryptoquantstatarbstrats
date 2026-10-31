# DURABLE HANDOFF | 2026-10-31T17:07:45Z | SINGLE MANDATORY NEXT TASK

## REPO IDENTITY (LAW) — PRIORITIZE BY REPO NAME
- Repo: `cryptoquantstatarbstrats` — **Crypto Quant Stat Arb Strategies**.
- **CORE = COINTEGRATION/PAIRS TRADING.** This is the primary edge. All other work (regime, tail risk, portfolio construction) MUST serve cointegration rigor. Prioritize cointegration diagnostics above everything else.
- Real data only: Binance public REST only. Synthetic/fabricated data strictly limited to isolated unit tests with explicit `fabricated_data: true`. No silent fabrication anywhere.
- **NETWORK (unblocked via www.binance.com).** `api.binance.com` (and `api1/2/3`, `fapi.binance.com`) returns HTTP 451 and is never relied upon as a primary path. The loader's host chain tries `www.binance.com` first. Where a series still cannot be reconstructed, mark `status: "blocked_or_insufficient_data"`, populate `blocked_routes[]`, add detailed rationale + full provenance, and MOVE ON. Never fabricate.
- **Coasting = failure.** Every action must produce checkable artifacts, tests, provenance, and logs. No speculative "maybe later" without concrete next steps.

## CURRENT VERIFIED STATE (2026-10-31T17:07:45Z)
- Branch: `main` (clean). Working tree clean.
- **GREEN BASELINE (must remain):** `ruff check backtest/ strategies/ utils/ tests/ examples/` → all checks passed | `pytest tests/ -q` → **546 passed, 1 skipped** | `mypy backtest/ strategies/ utils/` → Success, no issues found.
- Artifact: `reports/portfolio_real.json` (`real_data_only: true`, `fabricated_data: false`, `n_bars: 5112`).
- `cointegration_diagnostics`: publication-grade target schema for all 17 pairs (EG/Johansen with cv90/95/99+rank, per-leg ADF/KPSS, spread hedge ratio/ADF/KPSS, half-life OU with 1<hl<500, Hurst, mr_favorable, rolling stability windows/details, structural breaks, 7-gate set, full provenance). POL/BTC passes EG+Johansen+spread_mr+hl_bounds but rolling_stability fails (all_pass False). BTC/SOL/ADA/ETH/DOT/ETH show honest hl>500 failures (never clamped). `pair_metrics` preserved.
- `parameter_stability`: per-pair entries have `top_params`, `pair_metrics`, `degradation`, `regime_notes`, `provenance`; `portfolio_level` has provenance. All real-data only.
- `tail_risk`: `portfolio` VaR/CVaR/CDaR present; `regime_conditioned` filled from real `detect_regimes` with provenance; `permutation_test` has n_permutations >= 3000.
- Tests added: `tests/test_cointegration_diagnostics_schema.py`, `tests/test_tail_risk_parameter_stability.py` — all passing. README updated with parameter_stability/tail_risk docs.
- Modules: `utils/cointegration.py` (target schema builders, blocked_schema_diagnostics), `strategies/pairs_trading.py::get_cointegration_diagnostics` + enriched gates operationalized, `examples/run_portfolio_real.py` (passes enriched_diagnostics with use_enriched_gates=True).
- **COMPLETED:** Enriched cointegration diagnostics are operationalized in `CointegrationPairsStrategy.generate_signals()` — gates (eg_pass, johansen_pass, spread_mr_pass, hl_bounds_pass, rolling_stable_ok, leg_stationarity_ok) enforced causally using trailing data only. Uses cached `self.enriched_diagnostics` as static pair-level gate; per-bar `target_schema_diagnostics` fallback retained only when no cached diagnostics are provided.

## CRITICAL BOTTLENECKS TO REMOVE (THIS CAMPAIGN)
1. **ZERO strategy enriched-gate tests.** `tests/test_strategies.py` has **no tests** for `use_enriched_gates`/`strict_enriched_gates` enforcement. Gate correctness is unproven — this is the heaviest, highest-leverage work.
2. **`strict_enriched_gates=False` default.** `CoinintegrationPairsStrategy.__init__` defaults `strict_enriched_gates=False`; `examples/run_portfolio_real.py:555` passes `strict_enriched_gates=False`. Gates can silently pass when diagnostics are missing/None/flagged. **Make strict the default.**
3. **Need network-independent enforcement tests.** Tests must use fabricated diagnostics only when explicitly flagged `fabricated_data: true` (isolated unit tests). Never touch real network paths.
4. **Preserve causal behavior.** Enriched gates must not use lookahead. Cached diagnostics are pair-level screens computed on history — enforce causally per bar as implemented.
5. **Preserve green.** Keep `ruff` clean, `pytest >= 546 passed / 0 new failures`, `mypy` clean.

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
- Read `strategies/pairs_trading.py` fully — understand cached enriched gate path, fallback path, strict behavior, and where gates short-circuit entries.
- Read `tests/test_strategies.py` — see existing patterns (fixtures, data shapes) to add tests cleanly.
- Read `examples/run_portfolio_real.py` around line ~550-560 — see how enriched_diagnostics passed.
- Read `utils/cointegration.py` — understand gate keys and schema.

### 2) HARDEN ENFORCEMENT + ADD TESTS (HEAVY WORK — CORE MISSION)
**Make enriched-gate enforcement provably correct.** Cointegration is LAW.
- **Add tests for strategy enriched-gates operationalization** (network-independent, isolated; if using fabricated diagnostics mark `fabricated_data: true` in test context only as appropriate):
  - `use_enriched_gates=True` + cached `enriched_diagnostics` with `all_pass=False` (or any gate False) → no entries taken (all positions zero when gates block). Verify opposing legs not emitted.
  - `use_enriched_gates=True` + `strict_enriched_gates=True` + missing/None gate values → entries blocked.
  - `use_enriched_gates=True` + passing cached diagnostics → valid entries still occur (not over-blocked).
  - `structural_breaks.flagged=True` blocks entries under strict mode; behavior under non-strict per implementation must be explicit and tested.
  - Causal only: gates use cached pair-level diagnostics (no lookahead). Ensure tests don't rely on future data.
- **Make `strict_enriched_gates=True` the default** in `CointegrationPairsStrategy.__init__`.
- **Update `examples/run_portfolio_real.py`** to use `strict_enriched_gates=True` (and keep passing cached enriched_diagnostics).
- **Add/adjust tests** so regressions are caught. Ensure `tests/test_strategies.py` gains coverage for the above. Keep tests deterministic.
- **Maintain green:** `pytest tests/ -q` >= 546 passed, 0 new failures. `ruff` clean. `mypy` clean.

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
- Update `README.md` to document cached enriched-diagnostics gate path and that `strict_enriched_gates` defaults to `True` (fail-closed when diagnostics missing/invalid).
- Ensure code comments/logging reflect strict-by-default behavior.
- Keep provenance intact (no fabrication).

## SINGLE MANDATORY OBJECTIVE (HEAVY WORK REQUIRED)
**Harden the operationalized enriched cointegration diagnostics in the live strategy.** Add network-independent tests proving `CointegrationPairsStrategy` enforces cached enriched gates correctly (block/allow), make `strict_enriched_gates=True` the default, update the portfolio runner accordingly, and keep the suite green. This is the core of `cryptoquantstatarbstrats` — do the heavy lifting. No coasting.

## HARD CONSTRAINTS
- **REAL DATA ONLY** — isolated tests only with explicit `fabricated_data: true` if fabricating diagnostics
- **NO SHORTCUTS / NO FABRICATION** — omit+document with full provenance if unavailable
- **PRESERVE GREEN** — >=546 passed, 0 new failures
- **HEAVY MANDATE** — complete full campaign, no coasting
- **BOTTLENECK REMOVAL** — eliminate inefficiencies, explicitly route around 451
- **COINTEGRATION IS LAW** — prioritize above all else
- **UNBUFFERED** — use `python -u`, deterministic ordering
- **CAUSAL ONLY** — no lookahead in gates/signals
