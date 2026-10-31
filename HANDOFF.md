# DURABLE HANDOFF | 2026-10-31T16:39:43Z | SINGLE MANDATORY NEXT TASK

## REPO IDENTITY (LAW) — PRIORITIZE BY REPO NAME
- Repo: `cryptoquantstatarbstrats` — **Crypto Quant Stat Arb Strategies**.
- **CORE = COINTEGRATION/PAIRS TRADING.** This is the primary edge. All other work (regime, tail risk, portfolio construction) MUST serve cointegration rigor. Prioritize cointegration diagnostics above everything else.
- Real data only: Binance public REST only. Synthetic/fabricated data strictly limited to isolated unit tests with explicit `fabricated_data: true`. No silent fabrication anywhere.
- **NETWORK (unblocked via www.binance.com).** `api.binance.com` (and `api1/2/3`, `fapi.binance.com`) returns HTTP 451 and is never relied upon as a primary path. The loader's host chain tries `www.binance.com` first. Where a series still cannot be reconstructed, mark `status: "blocked_or_insufficient_data"`, populate `blocked_routes[]`, add detailed rationale + full provenance, and MOVE ON. Never fabricate.
- **Coasting = failure.** Every action must produce checkable artifacts, tests, provenance, and logs. No speculative "maybe later" without concrete next steps.

## CURRENT VERIFIED STATE (2026-10-31T16:39:43Z)
- Branch: `main` (clean). Working tree clean.
- **GREEN BASELINE (verified):** `ruff check` passes | `pytest tests/ -q` → **546 passed, 1 skipped** | `mypy backtest/ strategies/ utils/` → clean.
- Artifact: `reports/portfolio_real.json` (`real_data_only: true`, `fabricated_data: false`, `n_bars: 5112`).
- `cointegration_diagnostics`: **publication-grade target schema for all 17 pairs** (EG/Johansen with cv90/95/99+rank, per-leg ADF/KPSS, spread hedge ratio/ADF/KPSS, half-life OU with 1<hl<500, Hurst, mr_favorable, rolling stability windows/details, structural breaks, 7-gate set, full provenance). POL/BTC passes EG+Johansen+spread_mr+hl_bounds but rolling_stability fails (all_pass False). BTC/SOL/ADA/ETH/DOT/ETH show honest hl>500 failures (never clamped). `pair_metrics` preserved.
- `parameter_stability`: per-pair entries have `top_params`, `pair_metrics`, `degradation`, `regime_notes`, `provenance`; `portfolio_level` has provenance. All real-data only.
- `tail_risk`: `portfolio` VaR/CVaR/CDaR present; `regime_conditioned` **filled from real detect_regimes** with provenance; `permutation_test` has **n_permutations >= 3000**.
- Tests added: `tests/test_cointegration_diagnostics_schema.py`, `tests/test_tail_risk_parameter_stability.py` — all passing. README updated with parameter_stability/tail_risk docs.
- Modules: `utils/cointegration.py` (target schema builders, blocked_schema_diagnostics), `strategies/pairs_trading.py::get_cointegration_diagnostics` + enriched gates operationalized, `examples/run_portfolio_real.py` (passes enriched_diagnostics with use_enriched_gates=True).
- **COMPLETED:** Enriched cointegration diagnostics are operationalized in `CointegrationPairsStrategy.generate_signals()` — gates (eg_pass, johansen_pass, spread_mr_pass, hl_bounds_pass, rolling_stable_ok, leg_stationarity_ok) enforced causally using trailing data only.
- **BOTTLENECK REMOVED:** `generate_signals()` previously recomputed `target_schema_diagnostics` (EG+Johansen+ADF+KPSS+half-life+Hurst+rolling+breaks) on **every bar** — O(n) expensive per-bar recomputation. Now uses cached `self.enriched_diagnostics` (passed from `run_portfolio_real.py`) as a static pair-level gate; per-bar `target_schema_diagnostics` fallback retained only when no cached diagnostics are provided.

## BOTTLENECK REMOVAL (APPLY THIS SESSION)
1. **Network 451** — Route around via `www.binance.com` / reuse cached/artifacts. Use `blocked_or_insufficient_data` + `blocked_routes` + full provenance if unreconstructible. Never retry blocked hosts.
2. **hl > 500** — Honest failure only; never clamp/fabricate. Document rationale.
3. **Per-bar diagnostic recomputation (REMOVED)** — `strategies/pairs_trading.py:192-273` now uses cached `self.enriched_diagnostics` gates instead of recomputing `target_schema_diagnostics` per-bar. Fallback per-bar path retained only when `enriched_diagnostics` is None.
4. **Single focus** — One agent completes the campaign end-to-end. No parallel drift.
5. **Preserve green** — Keep `ruff` clean, `pytest >= 546 passed / 0 new failures`, `mypy` clean. Run gates after meaningful changes.
6. **Eliminate inefficiencies** — If a path is blocked/slow/unnecessary, fix or route around explicitly with documentation.

## NEXT SESSION START POINT (INITIAL TASK MESSAGE — EXECUTE IN ORDER, NO DRIFT)

### 0) VERIFY GREEN (MANDATORY)
```bash
export PATH=/home/runner/work/_temp/kilo-home/.local/bin:$PATH
PYTHONPATH=/home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats python -m ruff check backtest/ strategies/ utils/ tests/ examples/ && \
PYTHONPATH=/home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats python -m pytest tests/ -q && \
PYTHONPATH=/home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats python -m mypy backtest/ strategies/ utils/
```
Must remain green. If broken, fix first.

### 1) INVENTORY
- Read `reports/portfolio_real.json` (cointegration_diagnostics all 17, parameter_stability, tail_risk). Confirm schema matches tests.
- Read `strategies/pairs_trading.py` fully — enriched gates now use cached `self.enriched_diagnostics` (static pair-level gate), per-bar fallback retained only when None.
- Read `utils/cointegration.py` target schema builders (`target_schema_diagnostics`, `blocked_schema_diagnostics`).
- Read `examples/run_portfolio_real.py` — already passes `enriched_diagnostics` with `use_enriched_gates=True`, `strict_enriched_gates=False`.
- Read `tests/test_strategies.py` — no test yet for strategy enriched-gates operationalization.

### 2) HARDEN STRATEGY ENRICHED GATES (HEAVY WORK - CORE MISSION)
**Make enriched-gate enforcement testable and strict.** Cointegration is LAW — diagnostics must drive decisions and be proven by tests.
- **Add tests for strategy enriched-gates operationalization** (network-independent, isolated tests only):
  - Test that `use_enriched_gates=True` with `enriched_diagnostics` having `all_pass=False` blocks all entries (no long/short).
  - Test that `use_enriched_gates=True` with `strict_enriched_gates=True` blocks entries when any gate is None/missing.
  - Test that `use_enriched_gates=True` with passing cached diagnostics does not incorrectly block valid entries.
  - Test that structural_breaks.flagged=True blocks entries under strict mode.
  - Test causal behavior: enriched gates must not use lookahead (cached diagnostics computed on full history are a pair-level screen, not per-bar lookahead).
- **Make `strict_enriched_gates=True` the default behavior** in `CointegrationPairsStrategy.__init__` (or at minimum document why it is not). Update `run_portfolio_real.py` accordingly if behavior changes.
- **Ensure tests fail if gates are bypassed incorrectly or if fabrication occurs.**
- Maintain >=546 passed, 0 new failures.

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
- Ensure `README.md` documents the cached enriched-diagnostics gate path and how `strict_enriched_gates` constrains entries.
- Ensure all code paths have full provenance/logging.

## SINGLE MANDATORY OBJECTIVE (HEAVY WORK REQUIRED)
**Harden the operationalized enriched cointegration diagnostics in the live strategy.** `CointegrationPairsStrategy` now enforces Johansen, spread mean-reversion/hl_bounds (1<hl<500), rolling stability, and structural break discipline using cached `enriched_diagnostics` — add network-independent tests proving the gates block/allow entries correctly, make strict mode the default, and keep green. This is the core of cryptoquantstatarbstrats — do the heavy lifting.

## HARD CONSTRAINTS
- **REAL DATA ONLY** — isolated tests only with explicit `fabricated_data: true`
- **NO SHORTCUTS / NO FABRICATION** — omit+document with full provenance if unavailable
- **PRESERVE GREEN** — >=546 passed, 0 new failures
- **HEAVY MANDATE** — complete full campaign, no coasting
- **BOTTLENECK REMOVAL** — eliminate inefficiencies, explicitly route around 451
- **COINTEGRATION IS LAW** — prioritize above all else
- **UNBUFFERED** — use `python -u`, deterministic ordering
- **CAUSAL ONLY** — no lookahead in gates/signals
