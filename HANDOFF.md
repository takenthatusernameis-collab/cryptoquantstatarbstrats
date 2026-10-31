# DURABLE HANDOFF | 2026-10-31T14:08:22Z | SINGLE MANDATORY NEXT TASK

## REPO IDENTITY (LAW) — PRIORITIZE BY REPO NAME
- Repo: `cryptoquantstatarbstrats` — **Crypto Quant Stat Arb Strategies**.
- **CORE = COINTEGRATION/PAIRS TRADING.** This is the primary edge. All other work (regime, tail risk, portfolio construction) MUST serve cointegration rigor. Prioritize cointegration diagnostics above everything else.
- Real data only: Binance public REST only. Synthetic/fabricated data strictly limited to isolated unit tests with explicit `fabricated_data: true`. No silent fabrication anywhere.
- **NETWORK (unblocked via www.binance.com).** `api.binance.com` (and `api1/2/3`, `fapi.binance.com`) returns HTTP 451 and is never relied upon as a primary path. The loader's host chain tries `www.binance.com` first. Where a series still cannot be reconstructed, mark `status: "blocked_or_insufficient_data"`, populate `blocked_routes[]`, add detailed rationale + full provenance, and MOVE ON. Never fabricate.
- **Coasting = failure.** Every action must produce checkable artifacts, tests, provenance, and logs. No speculative "maybe later" without concrete next steps.

## CURRENT VERIFIED STATE (2026-10-31T14:08:22Z)
- Branch: `main` (clean). Working tree clean.
- **GREEN BASELINE (verified):** `ruff check` passes | `pytest tests/ -q` → **546 passed, 1 skipped** | `mypy backtest/ strategies/ utils/` → clean.
- Artifact: `reports/portfolio_real.json` (`real_data_only: true`, `fabricated_data: false`, `n_bars: 5112`).
- `cointegration_diagnostics`: **publication-grade target schema for all 17 pairs** (EG/Johansen with cv90/95/99+rank, per-leg ADF/KPSS, spread hedge ratio/ADF/KPSS, half-life OU with 1<hl<500, Hurst, mr_favorable, rolling stability windows/details, structural breaks, 7-gate set, full provenance). POL/BTC passes EG+Johansen+spread_mr+hl_bounds but rolling_stability fails (all_pass False). BTC/SOL/ADA/ETH/DOT/ETH show honest hl>500 failures (never clamped). `pair_metrics` preserved.
- `parameter_stability`: per-pair entries have `top_params`, `pair_metrics`, `degradation`, `regime_notes`, `provenance`; `portfolio_level` has provenance. All real-data only.
- `tail_risk`: `portfolio` VaR/CVaR/CDaR present; `regime_conditioned` **filled from real detect_regimes** with provenance; `permutation_test` has **n_permutations >= 3000**.
- Tests added: `tests/test_cointegration_diagnostics_schema.py`, `tests/test_tail_risk_parameter_stability.py` — all passing. README updated with parameter_stability/tail_risk docs.
- Modules: `utils/cointegration.py` (target schema builders, blocked_schema_diagnostics), `strategies/pairs_trading.py::get_cointegration_diagnostics`, `examples/run_portfolio_real.py`.

## BOTTLENECK REMOVAL (APPLY THIS SESSION)
1. **Network 451** — Route around via `www.binance.com` / reuse cached/artifacts. Use `blocked_or_insufficient_data` + `blocked_routes` + full provenance if unreconstructible. Never retry blocked hosts.
2. **hl > 500** — Honest failure only; never clamp/fabricate. Document rationale.
3. **Single focus** — One agent completes the campaign end-to-end. No parallel drift.
4. **Preserve green** — Keep `ruff` clean, `pytest >= 546 passed / 0 new failures`, `mypy` clean. Run gates after meaningful changes.
5. **Eliminate inefficiencies** — If a path is blocked/slow/unnecessary, fix or route around explicitly with documentation.

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
- Read `strategies/pairs_trading.py` fully. Current strategy uses EG p-value gate + rolling hedge ratio; enriched diagnostics (Johansen rank, rolling stability, structural breaks, hl_bounds) are not yet operationalized.
- Read `utils/cointegration.py` target schema builders.
- Read `examples/run_portfolio_real.py` to understand how diagnostics flow.

### 2) OPERATIONALIZE ENRICHED COINTEGRATION DIAGNOSTICS (HEAVY WORK - CORE MISSION)
**Make the trading logic actually use the publication-grade diagnostics.** Cointegration is LAW - diagnostics must drive decisions.
- **Enhance `CointegrationPairsStrategy`** to load/use enriched cointegration diagnostics (from artifact or computed via `target_schema_diagnostics` on real data). Prefer real diagnostics over ad-hoc checks.
- **Strengthen gates**: incorporate Johansen rank>=1, spread MR (ADF spread p<0.05), hl_bounds (1<hl<500), rolling stability (frac_significant/rolling_stable), structural breaks (no break / flagged handling). Be strict but honest - never fabricate; if data insufficient for a gate, treat as fail with rationale.
- **Preserve causal behavior**: all checks must use trailing data only (no lookahead). Rolling hedge ratio must remain causal.
- **Hedge ratio discipline**: keep existing guardrails (positive hedge ratio, explicit per-asset weights). Don't regress.
- **Integrate into screening**: update `examples/run_portfolio_real.py` pair selection to use the enriched gates (or record gate pass/fail). Ensure `pair_diagnostics` attached to artifact remain publication-grade with full provenance.
- **Deterministic, real-data only**: no synthetic data; isolated tests only with explicit `fabricated_data: true`.

### 3) HARDEN TESTS & PREVENT REGRESSIONS
- Add/update tests for strategy operationalization of enriched gates (network-independent). Ensure tests fail if gates are bypassed incorrectly or if fabrication occurs.
- Keep existing schema tests passing. Add tests for causal behavior if needed.
- Maintain >=546 passed, 0 new failures.

### 4) DOCS & PROVENANCE
- Update `README.md` to document operationalized cointegration gates (Johansen/rolling stability/hl_bounds/structural breaks) and how they constrain entries.
- Ensure all new code paths have full provenance/logging.

### 5) VERIFY & DELIVER (MANDATORY)
```bash
export PATH=/home/runner/work/_temp/kilo-home/.local/bin:$PATH
PYTHONPATH=/home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats python -u examples/run_portfolio_real.py
PYTHONPATH=/home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats python -m pytest tests/ -q
PYTHONPATH=/home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats python -m ruff check backtest/ strategies/ utils/ tests/ examples/
PYTHONPATH=/home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats python -m mypy backtest/ strategies/ utils/
```
All must pass. Zero regressions. Do not commit unless explicitly requested.

## SINGLE MANDATORY OBJECTIVE (HEAVY WORK REQUIRED)
**Operationalize the enriched publication-grade cointegration diagnostics in the live strategy.** The artifact now has full diagnostics for all 17 pairs - make `CointegrationPairsStrategy` actually enforce Johansen, spread mean-reversion/hl_bounds (1<hl<500), rolling stability, and structural break discipline using only trailing/real data. Keep behavior causal, preserve green baseline, never fabricate, and document everything with provenance. This is the core of cryptoquantstatarbstrats - do the heavy lifting.

## HARD CONSTRAINTS
- **REAL DATA ONLY** — isolated tests only with explicit `fabricated_data: true`
- **NO SHORTCUTS / NO FABRICATION** — omit+document with full provenance if unavailable
- **PRESERVE GREEN** — >=546 passed, 0 new failures
- **HEAVY MANDATE** — complete full campaign, no coasting
- **BOTTLENECK REMOVAL** — eliminate inefficiencies, explicitly route around 451
- **COINTEGRATION IS LAW** — prioritize above all else
- **UNBUFFERED** — use `python -u`, deterministic ordering
- **CAUSAL ONLY** — no lookahead in gates/signals
