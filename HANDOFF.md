# DURABLE HANDOFF (2026-10-31T07:24:18Z) — SINGLE MANDATORY NEXT TASK: CRYPTO QUANT STAT ARB - COINTEGRATION RIGOR MAXIMIZATION (PHASE 4c)

## REPO IDENTITY (LAW)
- **REPO:** `cryptoquantstatarbstrats` — *Crypto Quant Stat Arb Strategies*
- **CORE PRIORITY (from repo name):** Crypto + Quant + Statistical Arbitrage. **Cointegration/pairs trading is THE CORE.** Everything must serve real-data cointegration rigor, falsifiability, cost-robustness, and regime-awareness.
- **MANDATE:** **REAL DATA ONLY** (Binance public REST). Synthetic/fabricated data strictly limited to isolated unit tests with explicit `fabricated_data: true` warnings. No silent fabrication.
- **COASTING = FAILURE.** Every action must produce checkable artifacts, tests, provenance, and logs.
- **HEAVY WORK MANDATORY. DO NOT COAST. IMPOSSIBLE TO COAST.**

## VERIFIED GREEN BASELINE (DO NOT REGRESS) — verified 2026-10-31T06:36:44Z
- **Branch:** `main` (clean), up to date with `origin/main`. Working tree clean.
- **Lint:** `python -m ruff check backtest/ strategies/ utils/ tests/ examples/` → **All checks passed!**
- **Tests:** `PYTHONPATH=. python -m pytest tests/ -q` → **529 passed, 1 skipped**
- **Type:** `python -m mypy backtest/ strategies/ utils/` → **Success: no issues found in 32 source files.**
- **Artifact:** `reports/portfolio_real.json` (real-only). Missing required blocks: `cointegration_diagnostics`, `parameter_stability`, `tail_risk`, `blocked_routes`. `bootstrap_ci_portfolio_oos.n_simulations` = 2000 (need >=3000).
- **Modules:** `utils/cointegration.py`, `strategies/pairs_trading.py` exist (audit/harden, not rewrite).
- **Network:** Binance public REST returns **451** (blocked). Log all attempts; bounded backoff; preserve artifact; never fabricate.

## BOTTLENECKS TO ELIMINATE (IMMEDIATE)
1. **Network block (451):** Exhaustive logging (host/endpoint/status/latency_ms/error), bounded exponential backoff, skip live fetch if blocked, document in `blocked_routes`.
2. **Bootstrap:** Raise from 2000 → **>=3000** with fixed seed logged; add block-bootstrap for dependence; network-independent.
3. **Missing artifacts:** Add `cointegration_diagnostics`, `parameter_stability`, `tail_risk` (VaR/CVaR/CDaR 95%/99%/99.9%), `blocked_routes` - schema-complete, backwards compatible.
4. **Parallelization:** `examples/run_portfolio_real.py` uses `ProcessPoolExecutor` with `max_workers=min(4, len(_pairs_to_screen))` → change to `max_workers=min(4, os.cpu_count())`, deterministic ordering, keep checkpoint/resume.
5. **Data quality:** Strict gates (overlap/gaps/dupes/NaNs) → exclude with full rationale + attempt log; no interpolation/backfill/fabrication.
6. **Observability/determinism:** Unbuffered (`python -u`, `flush=True`), fixed seeds, full provenance, structured logs.

## INITIAL TASK MESSAGE FOR NEXT AGENTIC SESSION (TIMESTAMP: 2026-10-31T07:24:18Z)

**START NOW. HEAVY WORK MANDATORY. DO NOT COAST. IMPOSSIBLE TO COAST.**

### PRIMARY OBJECTIVE
Make this crypto stat arb system **publication-grade on cointegration rigor**. Deepen Engle-Granger/Johansen, rolling stability, half-life/OU, structural breaks, regime-conditional cointegration, parameter stability, walk-forward robustness, tail risk, and cost-aware falsification. **Real data only.** Binance 451 known - preserve committed artifact, log blocked routes, run network-independent tests, never fabricate.

### MANDATORY SEQUENCE (IN ORDER, NO SHORTCUTS)

#### 0) RESTORE & VERIFY GREEN (BLOCKING)
```bash
export PATH=/home/runner/work/_temp/kilo-home/.local/bin:$PATH
python -m ruff check backtest/ strategies/ utils/ tests/ examples/ && \
PYTHONPATH=. python -m pytest tests/ -q && \
python -m mypy backtest/ strategies/ utils/
```
Fix immediately if broken. **Do not proceed until green.**

#### 1) ELIMINATE BOTTLENECKS (PRIORITY - DO FIRST)
- **Parallelization:** Harden `examples/run_portfolio_real.py`: `max_workers = min(4, os.cpu_count())` (deterministic order). Keep checkpoint/resume. Add timing/provenance logs.
- **Logging:** Ensure unbuffered everywhere for long runs (`python -u`, `flush=True`). Remove hidden sleeps/polling.
- **Network discipline:** For any Binance attempt log `(host, endpoint, status, latency_ms, error, ts)`. Bounded exponential backoff. On 451/blocks → record in `blocked_routes`, skip live fetch, never fabricate.

#### 2) DEEP COINTEGRATION RIGOR (CORE)
Audit/harden `utils/cointegration.py` and `strategies/pairs_trading.py`:
- **EG:** ADF/KPSS on legs and residuals, lag selection, strict thresholds; log fully.
- **Johansen:** trace/max-eigenvalue if feasible, ranks/critical values/stats.
- **Rolling stability:** 90d/180d windows; require stability or penalize/exclude.
- **Half-life/OU:** bounds 1 < hl < 500; exclude non-mean-reverting/extreme.
- **Structural breaks:** CUSUM/Chow/rolling param stability; flag/exclude.
- **Spread quality:** ADF on spread, Hurst/exponent, stationarity. Full per-pair logs + provenance.

#### 3) UNIVERSE EXPANSION WITH IRONCLAD GATES (REAL-ONLY)
Candidates: ARB, OP, NEAR, INJ, APT, SUI, TIA, SEI, BCH, ETC, ATOM, UNI, AAVE, LINK, LTC, AVAX, DOGE. Attempt real Binance spot 1h+4h 2026-04-01→2026-10-30 with ALL gates. Admit only if pass. Update PAIRS with justification. Record every inclusion/exclusion in `universe_changes`/`exclusions_with_rationale` with full attempt logs. If blocked (451) → document in `blocked_routes` and exclude with rationale.

#### 4) PARAMETER STABILITY & WALK-FORWARD
- >=16 splits per pair where feasible; IS/OOS degradation + stability scores.
- Regime-aware stability tests for top params.
- Sensitivity grid around optimal with stability metrics.
- Enrich `multi_timeframe_walk_forward` with per-pair breakdowns.

#### 5) BOOTSTRAP >=3000 + TAIL RIGOR
- Raise `bootstrap_ci_portfolio_oos.n_simulations` to **>=3000**, fixed seed logged; add block-bootstrap option.
- Add `tail_risk`: VaR/CVaR/CDaR at 95%/99%/99.9%, expected shortfall, regime-conditioned.
- Regime-conditional bootstrap CIs, permutation tests vs zero, cost-impact across bootstrap.
- Network-independent.

#### 6) ARTIFACT ENRICHMENT (SCHEMA-COMPLETE, BACKWARDS COMPATIBLE)
Update `reports/portfolio_real.json` in-place:
- `cointegration_diagnostics` (per-pair EG/Johansen/rolling/hl/breaks/spread quality + provenance)
- `parameter_stability` (splits/regimes/sensitivity)
- `tail_risk` (VaR/CVaR/CDaR multiple levels, regime-conditioned)
- `blocked_routes` (host/endpoint/status/latency_ms/error/timestamps)
- Ensure `bootstrap_ci_portfolio_oos` >=3000 sims, seeds, block-bootstrap if added, regime-conditional CIs, permutation p-values
- Preserve all existing hardened fields; keep `real_data_only: true`, `fabricated_data: false`.

#### 7) TESTS + DOCS (IMPOSSIBLE TO COAST)
- Network-independent tests for cointegration gates, half-life bounds, stability, artifact schema extensions
- Tests preventing fabricated cointegration results when data unavailable
- Strengthen assertions for real-data-only + provenance completeness
- Update `README.md` with cointegration rigor, pair selection rationale, reproduction commands

#### 8) VERIFY & DELIVER (ZERO REGRESSIONS)
```bash
export PATH=/home/runner/work/_temp/kilo-home/.local/bin:$PATH
python -u examples/run_portfolio_real.py   # skip if blocked; preserve artifact
PYTHONPATH=. python -m pytest tests/ -q    # >=529 passed, 0 new failures
python -m ruff check backtest/ strategies/ utils/ tests/ examples/  # clean
python -m mypy backtest/ strategies/ utils/  # clean
```
All deliverables present/valid. Do not commit unless explicitly requested.

## HARD CONSTRAINTS
- **REAL DATA ONLY** — no synthetic/fabricated data; isolated unit tests only with explicit `fabricated_data: true`.
- **NO SHORTCUTS** — omit+document if unavailable with full provenance.
- **PRESERVE GREEN** — zero regressions.
- **HEAVY MANDATE** — complete full campaign.
- **BOTTLENECK REMOVAL** — eliminate inefficiencies immediately.
- **IMPOSSIBLE TO COAST** — every step must produce checkable artifact/test/provenance.
- **UNBUFFERED** — `python -u`, `flush=True`.
- **REPRODUCIBILITY** — fixed seeds, deterministic ordering, full config logged.

**CAMPAIGN PHASE 4c COMPLETE ONLY WHEN ALL CRITERIA MET. START IMMEDIATELY.**
