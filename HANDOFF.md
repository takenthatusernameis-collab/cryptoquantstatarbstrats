# DURABLE HANDOFF | 2026-10-31T08:18:15Z | SINGLE MANDATORY NEXT TASK

## REPO IDENTITY (LAW)
- **Repo:** `cryptoquantstatarbstrats` — Crypto Quant Stat Arb Strategies
- **Core:** Crypto + Quant + Statistical Arbitrage. **Cointegration/pairs trading IS THE CORE.** Everything must serve real-data cointegration rigor, falsifiability, cost-robustness, and regime-awareness.
- **Real data only:** Binance public REST only. Synthetic/fabricated data strictly limited to isolated unit tests with explicit `fabricated_data: true`. No silent fabrication.
- **Coasting = failure.** Every action must produce checkable artifacts, tests, provenance, and logs.
- **Heavy work mandatory. Do not coast.**

## CURRENT STATE (VERIFIED)
- **Branch:** `main` (clean), up to date with `origin/main`. Working tree clean.
- **Green baseline:** `ruff check` all passed (installed) | `pytest tests/ -q` → **529 passed, 1 skipped** | `mypy backtest/ strategies/ utils/` → **to verify**
- **Artifact:** `reports/portfolio_real.json` present. Cointegration diagnostics/parameter stability/tail risk already populated from existing results; bootstrap n_sim are 3000. Binance REST returning 451 (blocked) as noted in `blocked_routes`.
- **Modules:** `utils/cointegration.py` comprehensive; `strategies/pairs_trading.py` exists. Network access blocked externally - must remain network-independent.

## BOTTLENECKS TO REMOVE (IMMEDIATE)
1. **Network block (451)** - External. Compute from existing data/provenance when network blocked; never fabricate. Preserve artifacts on failure.
2. **Deepen cointegration rigor** - Enrich per-pair diagnostics with explicit EG/Johansen/ADF/KPSS on spread/legs, half-life/OU with bounds, Hurst, rolling stability, structural breaks, and concrete pass/fail gates with provenance.
3. **Harmonize & complete artifact fields** - Ensure all enrichment blocks consistent, n_sim >=3000 everywhere used, tail_risk complete, and regimes/parameter stability have no gaps.
4. **Tighten no-fabrication enforcement** - Add/strengthen tests preventing fabricated cointegration results when data insufficient; require structured `blocked_or_insufficient_data` with rationale.

## INITIAL TASK MESSAGE FOR NEXT AGENTIC SESSION (TIMESTAMP: 2026-10-31T08:18:15Z)

**START NOW. HEAVY WORK MANDATORY. DO NOT COAST.**

### PRIMARY OBJECTIVE
Make the system publication-grade on **cointegration rigor**. Deepen Engle-Granger/Johansen, rolling stability, half-life/OU bounds, structural breaks, regime-conditional cointegration, parameter stability, walk-forward robustness, tail risk, and cost-aware falsification. **Real data only.** Binance 451 is known - preserve artifacts, log blocked routes, compute from existing data/provenance when network blocked, never fabricate.

### MANDATORY SEQUENCE (IN ORDER)

#### 0) VERIFY GREEN (BLOCKING)
```bash
export PATH=/home/runner/work/_temp/kilo-home/.local/bin:$PATH
PYTHONPATH=/home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats python -m ruff check backtest/ strategies/ utils/ tests/ examples/ && \
PYTHONPATH=/home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats python -m pytest tests/ -q && \
PYTHONPATH=/home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats python -m mypy backtest/ strategies/ utils/
```
Fix immediately if broken. Do not proceed.

#### 1) DEEPEN COINTEGRATION DIAGNOSTICS (CORE)
- For every pair in `reports/portfolio_real.json`, compute/enrich `cointegration_diagnostics[pair]` with:
  - `engle_granger`: score/pvalue/critical values + pass/fail
  - `johansen`: trace/max-eig stats/ranks/critical values + pass/fail
  - `adf_leg1/adf_leg2`, `kpss_leg1/kpss_leg2`
  - `spread`: hedge ratio, `adf_spread`, `kpss_spread`, `half_life_ou` (require 1 < hl < 500 and mean-reverting), `hurst_exponent` (<0.5 favors MR)
  - `rolling_stability`: windows/frac_significant/stable flag
  - `structural_breaks`: breaks flagged with rationale
  - `gates`: all_pass + per-gate booleans
  - `provenance`: source, real_data_only, fabricated_data=false, timestamps
- If spread/series not reconstructible from artifact, use structured `status: "blocked_or_insufficient_data"` with explicit rationale and provenance (no fabrication). Use `utils.cointegration` functions.

#### 2) ENRICH PARAMETER STABILITY & TAIL RISK
- Strengthen `parameter_stability` with per-pair stability scores, degradation metrics, and regime notes from existing walk-forward data.
- Ensure `tail_risk.portfolio` complete (VaR/CVaR/CDaR at 95/99/99.9), add `regime_conditioned` if computable from existing returns, `permutation_test` present with provenance.
- Harmonize all bootstrap `n_simulations` >=3000 across blocks.

#### 3) HARDEN MODULES & TESTS (NO-FABRICATION)
- Audit/harden `utils/cointegration.py` and `strategies/pairs_trading.py` for strict gates, bounds, logging, deterministic behavior.
- Add network-independent tests ensuring enrichment blocks are schema-valid and never emit fabricated cointegration results when data unavailable (must use `blocked_or_insufficient_data` + provenance).
- Add tests for half-life bounds (1<hl<500), EG/Johansen gates, rolling stability, structural breaks.
- Keep all existing tests passing (>=529 passed).

#### 4) DOCS & REPRODUCIBILITY
- Update `README.md` with cointegration rigor summary, gates, reproduction commands.
- Ensure full provenance in `reports/portfolio_real.json`.

#### 5) VERIFY & DELIVER
```bash
export PATH=/home/runner/work/_temp/kilo-home/.local/bin:$PATH
PYTHONPATH=/home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats python -u examples/run_portfolio_real.py   # preserve artifact if blocked
PYTHONPATH=/home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats python -m pytest tests/ -q    # >=529 passed, 0 new failures
PYTHONPATH=/home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats python -m ruff check backtest/ strategies/ utils/ tests/ examples/
PYTHONPATH=/home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats python -m mypy backtest/ strategies/ utils/
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
