# DURABLE HANDOFF | 2026-10-31T08:23:32Z | SINGLE MANDATORY NEXT TASK

## REPO IDENTITY (LAW)
- Repo: `cryptoquantstatarbstrats` — Crypto Quant Stat Arb Strategies
- Core: Crypto + Quant + Statistical Arbitrage. **Cointegration/pairs trading IS THE CORE**.
- Real data only: Binance public REST only. Synthetic/fabricated data strictly limited to isolated unit tests with explicit `fabricated_data: true`. No silent fabrication.
- Coasting = failure. Every action must produce checkable artifacts, tests, provenance, and logs.
- Heavy work mandatory. Do not coast.

## CURRENT STATE (VERIFIED)
- Branch: `main` (clean). Working tree clean.
- Green baseline: `ruff check` passes | `pytest tests/ -q` → **529 passed, 1 skipped** (network-independent baseline) | `mypy backtest/ strategies/ utils/` → success.
- Artifact: `reports/portfolio_real.json` exists (5481 lines).
- Cointegration diagnostics present but **incomplete** (see below). Network blocked externally (451) in places.
- Modules: `utils/cointegration.py` (comprehensive diagnostics exist), `strategies/pairs_trading.py` (uses them), `examples/run_portfolio_real.py` (builds portfolio_real.json).

## BOTTLENECKS TO REMOVE (IMMEDIATE)
1. **Cointegration rigor incomplete** - `cointegration_diagnostics[pair]` is minimal (mostly `available:false`/notes). Must be enriched to publication-grade per-pair schema.
2. **Network block (451)** - Enrichment must work from existing artifacts/provenance and reconstructible series when available; if not reconstructible, emit `status: "blocked_or_insufficient_data"` with full `blocked_routes` + provenance. Never fabricate.
3. **Parameter stability / tail risk gaps** - Ensure `bootstrap.n_simulations >= 3000` everywhere, `tail_risk.portfolio` complete (VaR/CVaR/CDaR 95/99/99.9), `permutation_test` present, `parameter_stability` enriched.
4. **No-fabrication enforcement** - Harden tests to fail if fabricated cointegration results appear without `fabricated_data: true` in isolated test context.

## INITIAL TASK MESSAGE FOR NEXT AGENTIC SESSION (TIMESTAMP: 2026-10-31T08:23:32Z)

START NOW. HEAVY WORK MANDATORY. DO NOT COAST.

### PRIMARY OBJECTIVE
Make the system publication-grade on **cointegration rigor** (the core). Deepen Engle-Granger/Johansen, rolling stability, half-life/OU bounds, structural breaks, regime-conditional cointegration, parameter stability, walk-forward robustness, tail risk, and cost-aware falsification. Real data only. Binance 451 known - preserve artifacts, log blocked routes, compute from existing data/provenance when network blocked, never fabricate.

### MANDATORY SEQUENCE (IN ORDER)

#### 0) VERIFY GREEN (BLOCKING)
```bash
export PATH=/home/runner/work/_temp/kilo-home/.local/bin:$PATH
PYTHONPATH=/home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats python -m ruff check backtest/ strategies/ utils/ tests/ examples/ && \
PYTHONPATH=/home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats python -m pytest tests/ -q && \
PYTHONPATH=/home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats python -m mypy backtest/ strategies/ utils/
```
Fix immediately if broken. Do not proceed.

#### 1) INVENTORY & TARGET (HEAVY)
- Read `reports/portfolio_real.json` fully. For each pair, list missing required fields.
- Inspect `utils/cointegration.py`, `strategies/pairs_trading.py`, `examples/run_portfolio_real.py`, `tests/` for enrichment patterns and provenance schema.
- Map what series are reconstructible from existing artifacts/checkpoints vs what requires network fetch (respect 451). Create an explicit plan with artifacts/tests to produce.

#### 2) DEEPEN COINTEGRATION DIAGNOSTICS (CORE - MUST TOUCH)
Modify or extend code so that for **every pair** in `reports/portfolio_real.json`, `cointegration_diagnostics[pair]` contains:
- `engle_granger`: {available, score/stat, pvalue, critical_values, pass/fail, method, provenance}
- `johansen`: {available, trace_stat, max_eig_stat, cv_90/95/99, rank, pass/fail, provenance}
- `adf_leg1`, `adf_leg2`, `kpss_leg1`, `kpss_leg2`: per-leg stationarity with stats/pvals/critical_values/gates
- `spread`: {hedge_ratio, adf_spread, kpss_spread, half_life_ou (1<hl<500, MR required), hurst_exponent (<0.5 favors MR), provenance}
- `rolling_stability`: {windows:[...], frac_significant, stable(bool), notes, provenance}
- `structural_breaks`: {breaks:[{date/index, test, pvalue, rationale}], flagged(bool), provenance}
- `gates`: {all_pass, eg_pass, johansen_pass, spread_mr_pass, hl_bounds_pass, leg_stationarity_ok, rolling_stable_ok, ...}
- `provenance`: {source, real_data_only:true, fabricated_data:false, computed_at (ISO8601), inputs_hash or rationale}

If spread/series not reconstructible from artifact/data available in repo, set `status: "blocked_or_insufficient_data"`, include explicit `blocked_routes`/rationale, full provenance. Use functions from `utils.cointegration`. Never fabricate numbers.

**Action**: Enrich `examples/run_portfolio_real.py` to compute/persist full diagnostics (prefer using cached/reconstructible data; if network needed and blocked, log and fall back to blocked_or_insufficient_data with provenance). Also ensure `CointegrationPairsStrategy.get_cointegration_diagnostics` can produce this schema.

#### 3) ENRICH PARAMETER STABILITY & TAIL RISK
- Enrich `parameter_stability` per-pair with stability scores, degradation metrics, regime notes from existing walk-forward data.
- Ensure `tail_risk.portfolio` complete: VaR/CVaR/CDaR at 95/99/99.9; add `regime_conditioned` if computable from existing returns; ensure `permutation_test` present with provenance.
- Harmonize all bootstrap `n_simulations` >= 3000 across blocks (set/fill consistently).

#### 4) HARDEN & ADD NETWORK-INDEPENDENT TESTS
- Audit/harden `utils/cointegration.py`, `strategies/pairs_trading.py` for strict gates, bounds, logging, deterministic behavior.
- Add tests (network-independent) asserting schema validity for enriched blocks and that no fabricated cointegration results are emitted when data unavailable - must use `blocked_or_insufficient_data` + provenance.
- Add tests for half-life bounds (1<hl<500), EG/Johansen gates, rolling stability, structural breaks.
- Keep >=529 passed, 0 new failures.

#### 5) DOCS & REPRODUCIBILITY
- Update `README.md` with cointegration rigor summary, gates, reproduction commands.
- Ensure full provenance in `reports/portfolio_real.json` (timestamps, sources, blocked_routes if any).

#### 6) VERIFY & DELIVER (MANDATORY)
```bash
export PATH=/home/runner/work/_temp/kilo-home/.local/bin:$PATH
PYTHONPATH=/home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats python -u examples/run_portfolio_real.py   # preserve artifact if blocked
PYTHONPATH=/home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats python -m pytest tests/ -q    # >=529 passed, 0 new failures
PYTHONPATH=/home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats python -m ruff check backtest/ strategies/ utils/ tests/ examples/
PYTHONPATH=/home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats python -m mypy backtest/ strategies/ utils/
```
All must pass. Zero regressions. Do not commit unless explicitly requested.

## HARD CONSTRAINTS
- REAL DATA ONLY - no synthetic/fabricated data; isolated unit tests only with explicit `fabricated_data: true`
- NO SHORTCUTS - omit+document if unavailable with full provenance
- PRESERVE GREEN - zero regressions
- HEAVY MANDATE - complete full campaign
- BOTTLENECK REMOVAL - eliminate inefficiencies; make logic network-independent where possible
- IMPOSSIBLE TO COAST - every step must produce checkable artifact/test/provenance
- UNBUFFERED - `python -u`, `flush=True`
- REPRODUCIBILITY - fixed seeds, deterministic ordering, full config logged
