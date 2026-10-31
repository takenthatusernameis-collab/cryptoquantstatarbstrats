# DURABLE HANDOFF | 2026-10-31T09:15:41Z | SINGLE MANDATORY NEXT TASK

## REPO IDENTITY (LAW)
- Repo: `cryptoquantstatarbstrats` — Crypto Quant Stat Arb Strategies
- Core: Crypto + Quant + Statistical Arbitrage. **COINTEGRATION/PAIRS TRADING IS THE CORE - EVERYTHING ELSE IS SUPPORTING**.
- Real data only: Binance public REST only. Synthetic/fabricated data strictly limited to isolated unit tests with explicit `fabricated_data: true`. No silent fabrication.
- Coasting = failure. Every action must produce checkable artifacts, tests, provenance, and logs.
- Heavy work mandatory. Do not coast. Network may be blocked (451) - adapt, don't fabricate.

## CURRENT STATE (VERIFIED)
- Branch: `main` (clean). Working tree clean.
- Green baseline: `ruff check` passes | `pytest tests/ -q` → **529 passed, 1 skipped** (network-independent baseline) | `mypy backtest/ strategies/ utils/` → success.
- Artifact: `reports/portfolio_real.json` exists (5481 lines).
- **CRITICAL**: `cointegration_diagnostics` exists but is **severely under-specified**. Most pairs only have `engle_granger.available: true` with notes pointing elsewhere, `johansen` often `"not_explicit_in_artifact"`, `rolling_stability`/`half_life_ou`/`structural_breaks` mostly `available: false`. `parameter_stability` and `tail_risk` exist but need enrichment to be publication-grade.
- Modules: `utils/cointegration.py` (comprehensive diagnostics functions exist), `strategies/pairs_trading.py` (uses them), `examples/run_portfolio_real.py` (builds portfolio_real.json). Leverage these - don't reinvent.

## BOTTLENECKS TO REMOVE (IMMEDIATE - BLOCKING PROGRESS)
1. **Cointegration schema incomplete (HIGHEST PRIORITY)** - `cointegration_diagnostics[pair]` must be expanded from the minimal form to full publication-grade schema. Current form is insufficient for rigorous validation.
2. **Missing time-series dependent diagnostics** - `rolling_stability`, `half_life_ou` (spread-based), `structural_breaks`, proper `johansen` with trace/max-eig + critical values, per-leg ADF/KPSS are missing or incomplete for most pairs.
3. **Network block (451)** - Cannot fetch fresh data. Must reconstruct spread/series from existing artifacts, cached data, or existing computed results. If truly un-reconstructible, emit `status: "blocked_or_insufficient_data"` with explicit `blocked_routes`, full provenance. **NEVER FABRICATE**.
4. **Parameter stability / tail risk gaps** - `tail_risk.portfolio` needs complete VaR/CVaR/CDaR at 95/99/99.9 with provenance. `parameter_stability` needs enrichment with stability scores/degradation/regime notes from existing walk-forward data. All bootstrap `n_simulations` must be >= 3000.
5. **No-fabrication enforcement** - Tests must fail if fabricated cointegration results appear without `fabricated_data: true` in isolated test context.

## INITIAL TASK MESSAGE FOR NEXT AGENTIC SESSION (TIMESTAMP: 2026-10-31T09:15:41Z)

START NOW. HEAVY WORK MANDATORY. DO NOT COAST. **THIS IS A COINTEGRATION RIGOR CAMPAIGN - THE CORE OF THIS REPO.**

### PRIMARY OBJECTIVE
Make cointegration diagnostics publication-grade for **EVERY pair** in `reports/portfolio_real.json`. Deepen Engle-Granger/Johansen, per-leg stationarity (ADF/KPSS), spread diagnostics (hedge ratio, ADF/KPSS on spread, half-life OU with bounds 1<hl<500, Hurst), rolling window stability, structural breaks, regime-conditional checks where computable, tighten gates, enrich parameter stability/tail risk, harden tests - all with full provenance. Real data only. Work around Binance 451 by using existing artifacts/provenance/reconstructible series.

### MANDATORY SEQUENCE (EXECUTE IN ORDER - NO SKIPPING)

#### 0) VERIFY GREEN (BLOCKING - FIX FIRST IF BROKEN)
```bash
export PATH=/home/runner/work/_temp/kilo-home/.local/bin:$PATH
PYTHONPATH=/home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats python -m ruff check backtest/ strategies/ utils/ tests/ examples/ && \
PYTHONPATH=/home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats python -m pytest tests/ -q && \
PYTHONPATH=/home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats python -m mypy backtest/ strategies/ utils/
```
If anything fails, fix it before proceeding. Preserve green baseline (>=529 passed, 0 new failures).

#### 1) INVENTORY & CONSTRAINT MAPPING (HEAVY - CREATE ARTIFACT)
- Read `reports/portfolio_real.json` completely. For **every pair**, enumerate all missing fields vs target schema below.
- Read `utils/cointegration.py` - understand all available functions (Engle-Granger, Johansen, ADF/KPSS, half-life/OU, rolling, breaks etc). Use them, don't duplicate.
- Read `strategies/pairs_trading.py` (`CointegrationPairsStrategy.get_cointegration_diagnostics`) and `examples/run_portfolio_real.py` - understand how diagnostics are computed/persisted.
- Read relevant tests for patterns.
- **Map reconstructibility**: What price/spread series can be reconstructed from existing artifacts (portfolio_real.json has per-pair data, walk-forward, etc.) vs what requires network? Explicitly log `blocked_routes` for anything requiring network under 451. Create a concrete plan (files to touch, functions to add, tests to add) before coding.

#### 2) ENRICH COINTEGRATION DIAGNOSTICS SCHEMA (CORE - MUST TOUCH EVERY PAIR)
For **EVERY pair** in `reports/portfolio_real.json`, produce `cointegration_diagnostics[pair]` with this publication-grade shape (omit+document only if truly unreconstructible):

```json
{
  "pair": ["LEG1", "LEG2"],
  "status": "computed_from_existing_results" | "blocked_or_insufficient_data",
  "engle_granger": { "available": bool, "stat": number|null, "pvalue": number|null, "critical_values": {...}|null, "pass/fail": bool|null, "method": "engle_granger"|null, "provenance": {...} },
  "johansen": { "available": bool, "trace_stat": [...]|null, "max_eig_stat": [...]|null, "cv_90": [...]|null, "cv_95": [...]|null, "cv_99": [...]|null, "rank": number|null, "pass/fail": bool|null, "provenance": {...} },
  "adf_leg1": { "available": bool, "stat": number|null, "pvalue": number|null, "critical_values": {...}|null, "stationary": bool|null, "provenance": {...} },
  "adf_leg2": { "available": bool, "stat": number|null, "pvalue": number|null, "critical_values": {...}|null, "stationary": bool|null, "provenance": {...} },
  "kpss_leg1": { "available": bool, "stat": number|null, "pvalue": number|null, "critical_values": {...}|null, "stationary": bool|null, "provenance": {...} },
  "kpss_leg2": { "available": bool, "stat": number|null, "pvalue": number|null, "critical_values": {...}|null, "stationary": bool|null, "provenance": {...} },
  "spread": { "hedge_ratio": number|null, "adf_spread": {...}|null, "kpss_spread": {...}|null, "half_life_ou": number|null, "hurst_exponent": number|null, "mr_favorable": bool|null, "provenance": {...} },
  "rolling_stability": { "windows": [int,...], "frac_significant": number|null, "stable": bool|null, "details": [...], "notes": string|null, "provenance": {...} },
  "structural_breaks": { "breaks": [{"date"/"index", "test", "pvalue", "rationale"}], "flagged": bool, "notes": string|null, "provenance": {...} },
  "gates": { "all_pass": bool|null, "eg_pass": bool|null, "johansen_pass": bool|null, "spread_mr_pass": bool|null, "hl_bounds_pass": bool|null, "leg_stationarity_ok": bool|null, "rolling_stable_ok": bool|null },
  "provenance": { "source": string, "real_data_only": true, "fabricated_data": false, "computed_at": "ISO8601", "inputs_hash"?: string, "blocked_routes"?: string[], "rationale"?: string }
}
```

**Rules**:
- If spread/series not reconstructible from artifacts in repo, set `status: "blocked_or_insufficient_data"`, include explicit `blocked_routes` + rationale, full provenance. **Never fabricate numbers**.
- Enforce half-life bounds: if computed, require `1 < half_life_ou < 500` and set `hl_bounds_pass` accordingly. Mean-reversion favored if `hurst_exponent < 0.5` when available.
- Use functions from `utils.cointegration` wherever possible. Extend them if missing capability, but keep deterministic and network-independent where feasible.
- Update `examples/run_portfolio_real.py` to compute/enrich and persist full diagnostics. Ensure `CointegrationPairsStrategy.get_cointegration_diagnostics` can produce this schema.
- Preserve all existing useful data; only add/enrich, don't delete without justification.

#### 3) ENRICH PARAMETER STABILITY & TAIL RISK (HEAVY)
- **parameter_stability**: For each pair (and portfolio-level if present), add/enrich with stability scores, degradation metrics, regime notes derived from existing walk-forward/multi-timeframe data. Include provenance.
- **tail_risk.portfolio**: Must be complete with VaR/CVaR/CDaR at 95/99/99.9. Add `regime_conditioned` block if computable from existing returns. Ensure `permutation_test` is present with full provenance (hypotheses, n_perm, p-values, method).
- **Bootstrap consistency**: Harmonize `bootstrap` blocks so `n_simulations >= 3000` everywhere. Fill missing values consistently.

#### 4) HARDEN, TEST, ENFORCE NO-FABRICATION (CRITICAL)
- Audit/harden `utils/cointegration.py` and `strategies/pairs_trading.py` for strict gates, bounds checking, logging, deterministic ordering.
- Add **network-independent** tests that:
  - Assert schema validity for enriched `cointegration_diagnostics` (all required keys present per pair)
  - Fail if fabricated cointegration results appear without `fabricated_data: true` in isolated test context
  - Validate half-life bounds (1<hl<500), EG/Johansen gate logic, rolling stability structure, structural breaks structure
  - Validate blocked case produces `status: "blocked_or_insufficient_data"` + `blocked_routes` + provenance
- Keep all existing tests passing. Target >=529 passed, 0 new failures.

#### 5) DOCS, REPRODUCIBILITY, PROVENANCE (MANDATORY)
- Update `README.md` with cointegration rigor summary, gates, reproduction commands, and note about network 451 handling.
- Ensure `reports/portfolio_real.json` has full provenance everywhere added/enriched (timestamps, sources, blocked_routes if any). Make it obvious this is real-data-first with no silent fabrication.

#### 6) VERIFY & DELIVER (MANDATORY - NO SHORTCUTS)
```bash
export PATH=/home/runner/work/_temp/kilo-home/.local/bin:$PATH
PYTHONPATH=/home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats python -u examples/run_portfolio_real.py   # preserve artifact; if network blocked, must still produce enriched schema with blocked_or_insufficient_data + provenance
PYTHONPATH=/home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats python -m pytest tests/ -q    # >=529 passed, 0 new failures
PYTHONPATH=/home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats python -m ruff check backtest/ strategies/ utils/ tests/ examples/
PYTHONPATH=/home/runner/work/cryptoquantstatarbstrats/cryptoquantstatarbstrats python -m mypy backtest/ strategies/ utils/
```
**All must pass. Zero regressions.** Do not commit unless explicitly requested.

## HARD CONSTRAINTS (NON-NEGOTIABLE)
- **REAL DATA ONLY** - no synthetic/fabricated data; isolated unit tests only with explicit `fabricated_data: true`
- **NO SHORTCUTS** - if unavailable, omit+document with full provenance (`blocked_or_insufficient_data`, `blocked_routes`)
- **PRESERVE GREEN** - zero regressions from current baseline
- **HEAVY MANDATE** - complete the full campaign; this is core functionality
- **BOTTLENECK REMOVAL** - eliminate inefficiencies, make logic network-independent where possible
- **IMPOSSIBLE TO COAST** - every step must produce checkable artifact/test/provenance
- **UNBUFFERED** - use `python -u`, `flush=True`
- **REPRODUCIBILITY** - fixed seeds, deterministic ordering, full config logged
- **COINTEGRATION IS LAW** - prioritize this above all else
