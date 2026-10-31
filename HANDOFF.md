# DURABLE HANDOFF | 2026-10-31T07:44:06Z | SINGLE MANDATORY NEXT TASK

## REPO IDENTITY (LAW)
- **Repo:** `cryptoquantstatarbstrats` — Crypto Quant Stat Arb Strategies
- **Core:** Crypto + Quant + Statistical Arbitrage. **Cointegration/pairs trading IS THE CORE.** Everything must serve real-data cointegration rigor, falsifiability, cost-robustness, and regime-awareness.
- **Real data only:** Binance public REST only. Synthetic/fabricated data strictly limited to isolated unit tests with explicit `fabricated_data: true`. No silent fabrication.
- **Coasting = failure.** Every action must produce checkable artifacts, tests, provenance, and logs.
- **Heavy work mandatory. Do not coast.**

## CURRENT STATE (VERIFIED)
- **Branch:** `main` (clean), up to date with `origin/main`. Working tree clean.
- **Green baseline:** `ruff check` all passed | `pytest tests/ -q` → **529 passed, 1 skipped** | `mypy backtest/ strategies/ utils/` → **Success, 32 source files**
- **Committed artifact:** `reports/portfolio_real.json` exists (committed 2026-10-31 00:29:13Z). Portfolio results computed from real data previously; currently **stale/incomplete** for enrichment fields.
- **Key issue:** Binance public REST returns **451** (blocked). `data/loader.py` hardened with exhaustive per-attempt logging, bounded retries+backoff, permanent blocked-host skip, per-symbol isolation, early return with full provenance. `examples/run_portfolio_real.py` preserves artifact on failure.
- **Known gaps in artifact:** `cointegration_diagnostics: {}`, `parameter_stability: {}`, `tail_risk.portfolio` partial, `bootstrap_ci_portfolio_oos.distinguishability_from_zero.n_simulations` is **2000** (must be >=3000), some bootstrap sub-blocks show 2000. `blocked_routes` present with 451 entries.

## BOTTLENECKS TO REMOVE (IMMEDIATE)
1. **Network block (451)** - External; cannot unblock. **Fix:** make all enrichment logic network-independent. Compute `cointegration_diagnostics`, `parameter_stability`, `tail_risk` from existing `data`/results when present; if data unavailable, populate with structured `blocked` entries + full provenance (never fabricate). Loader already does this.
2. **Artifact schema completeness** - Enrich in-place without breaking existing fields. Ensure all blocks present and consistent (all n_simulations >=3000 where bootstrap used).
3. **Inconsistent simulation counts** - Harmonize `distinguishability_from_zero.n_simulations` to match (>=3000), ensure `cost_impact.n_simulations` consistent.
4. **Empty enrichment blocks** - Populate `cointegration_diagnostics`, `parameter_stability` with real computations from available data/provenance.

## INITIAL TASK MESSAGE FOR NEXT AGENTIC SESSION (TIMESTAMP: 2026-10-31T07:44:06Z)

**START NOW. HEAVY WORK MANDATORY. DO NOT COAST.**

### PRIMARY OBJECTIVE
Make the system publication-grade on **cointegration rigor**. Deepen Engle-Granger/Johansen, rolling stability, half-life/OU bounds, structural breaks, regime-conditional cointegration, parameter stability, walk-forward robustness, tail risk, and cost-aware falsification. **Real data only.** Binance 451 is known - preserve artifacts, log blocked routes, compute from existing data/provenance when network blocked, never fabricate.

### MANDATORY SEQUENCE (IN ORDER)

#### 0) VERIFY GREEN (BLOCKING)
```bash
export PATH=/home/runner/work/_temp/kilo-home/.local/bin:$PATH
python -m ruff check backtest/ strategies/ utils/ tests/ examples/ && \
PYTHONPATH=. python -m pytest tests/ -q && \
python -m mypy backtest/ strategies/ utils/
```
Fix immediately if broken. Do not proceed.

#### 1) REMOVE BOTTLENECKS - ARTIFACT CONSISTENCY & ENRICHMENT
- Harmonize all bootstrap simulation counts to >=3000: fix `bootstrap_ci_portfolio_oos.distinguishability_from_zero.n_simulations` to 3000 (or derive from actual array length). Ensure consistency across blocks.
- Enrich `reports/portfolio_real.json` in-place (backwards compatible) with network-independent computations using existing portfolio/pair data:
  - `cointegration_diagnostics`: per-pair EG/Johansen/ADF on spread/residuals, rolling stability (where feasible), half-life/OU bounds, Hurst, structural break flags. Use available pair results/provenance; if insufficient data, structured entries with `status: "blocked_or_insufficient_data"` + rationale.
  - `parameter_stability`: from existing walk-forward/multi-timeframe results - splits, degradation, stability scores per pair/portfolio.
  - `tail_risk`: ensure complete VaR/CVaR/CDaR at 95/99/99.9, regime-conditioned if possible, permutation test present. Fill gaps from existing returns.
- Preserve `real_data_only: true`, `fabricated_data: false`. Never fabricate values.

#### 2) HARDEN COINTEGRATION MODULES (CORE)
Audit/harden `utils/cointegration.py` and `strategies/pairs_trading.py`:
- EG: ADF/KPSS on legs and residuals, lag selection, strict logging
- Johansen: trace/max-eigenvalue ranks/critical values
- Rolling stability windows, half-life bounds (1 < hl < 500), OU checks
- Structural breaks (CUSUM/Chow/rolling), Hurst, spread quality
- Per-pair provenance, deterministic behavior

#### 3) TESTS FOR RIGOR & NO-FABRICATION
- Add network-independent tests for cointegration gates, half-life bounds, stability checks
- Add tests ensuring enrichment blocks are schema-valid and never emit fabricated cointegration results when data unavailable (must log blocked/insufficient with provenance)
- Strengthen real-data-only assertions
- Keep all existing tests passing (>=529 passed)

#### 4) DOCS & REPRODUCIBILITY
- Update `README.md` with cointegration rigor summary, gates, reproduction commands
- Ensure provenance complete in artifacts

#### 5) VERIFY & DELIVER
```bash
python -u examples/run_portfolio_real.py   # skip/regenerate if unblocked; must preserve artifact if blocked
PYTHONPATH=. python -m pytest tests/ -q    # >=529 passed, 0 new failures
python -m ruff check backtest/ strategies/ utils/ tests/ examples/  # clean
python -m mypy backtest/ strategies/ utils/  # clean
```
All criteria met, zero regressions. Do not commit unless explicitly requested.

## HARD CONSTRAINTS
- **REAL DATA ONLY** - no synthetic/fabricated data; isolated unit tests only with explicit `fabricated_data: true`
- **NO SHORTCUTS** - omit+document if unavailable with full provenance
- **PRESERVE GREEN** - zero regressions
- **HEAVY MANDATE** - complete full campaign
- **BOTTLENECK REMOVAL** - eliminate inefficiencies; make logic network-independent
- **IMPOSSIBLE TO COAST** - every step must produce checkable artifact/test/provenance
- **UNBUFFERED** - `python -u`, `flush=True`
- **REPRODUCIBILITY** - fixed seeds, deterministic ordering, full config logged
