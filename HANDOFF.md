# DURABLE HANDOFF (2026-10-31T07:25:48Z) — SINGLE MANDATORY NEXT TASK: CRYPTO QUANT STAT ARB - COINTEGRATION RIGOR MAXIMIZATION (PHASE 4c)

## REPO IDENTITY (LAW)
- **REPO:** `cryptoquantstatarbstrats` — *Crypto Quant Stat Arb Strategies*
- **CORE PRIORITY (from repo name):** Crypto + Quant + Statistical Arbitrage. **Cointegration/pairs trading is THE CORE.** Everything must serve real-data cointegration rigor, falsifiability, cost-robustness, and regime-awareness.
- **MANDATE:** **REAL DATA ONLY** (Binance public REST). Synthetic/fabricated data strictly limited to isolated unit tests with explicit `fabricated_data: true` warnings. No silent fabrication.
- **COASTING = FAILURE.** Every action must produce checkable artifacts, tests, provenance, and logs.
- **HEAVY WORK MANDATORY. DO NOT COAST. IMPOSSIBLE TO COAST.**

## VERIFIED GREEN BASELINE (DO NOT REGRESS) — verified 2026-10-31T07:25:48Z
- **Branch:** `main` (clean), up to date with `origin/main`. Working tree clean except this HANDOFF refresh + `data/loader.py` hardening (uncommitted, do not commit unless asked).
- **Lint:** `python -m ruff check backtest/ strategies/ utils/ tests/ examples/` → **All checks passed!**
- **Tests:** `PYTHONPATH=. python -m pytest tests/ -q` → **529 passed, 1 skipped**
- **Type:** `python -m mypy backtest/ strategies/ utils/` → **Success: no issues found in 32 source files.**
- **Artifact:** `reports/portfolio_real.json` (real-only, committed at 2026-10-31 00:29:13Z) is **STALE**: `bootstrap_ci_portfolio_oos.n_simulations` = 2000 (need >=3000); `cointegration_diagnostics`, `parameter_stability`, `tail_risk`, `blocked_routes` are `null`/`{}`. Code in `examples/run_portfolio_real.py` already emits all blocks and 3000 sims, but Binance returns **451** so `load_binance_data` aborts before the artifact is written. Regeneration is pending network unblock — preserve the stale artifact, never regenerate from synthetic data.
- **Modules:** `utils/cointegration.py`, `strategies/pairs_trading.py` exist (audit/harden, not rewrite).
- **Network:** Binance public REST returns **451** (blocked). `data/loader.py` hardened this session: exhaustive per-attempt logging (host/endpoint/status/latency_ms/error), bounded retries + exponential backoff (cap 30s), permanently blocked hosts (451/403/404) skipped for remaining symbols, per-symbol isolation (exclude with rationale, never take down the whole request), raises only when ALL symbols fail with full detail. `run_portfolio_real.py` catches, logs, and returns early → artifact preserved, nothing fabricated.

## BOTTLENECKS — STATUS
1. **Network block (451):** **MITIGATED IN CODE.** `data/loader.py` now logs every host attempt, backs off, skips dead hosts, isolates per-symbol failures, and `run_portfolio_real.py` preserves the artifact when all routes are blocked. Still blocked live: all 5 Binance hosts return 451 → document in `blocked_routes`, skip live fetch, never fabricate.
2. **Bootstrap:** **CODE DONE (3000 sims, seed 12345 logged, block-bootstrap via `bootstrap_trade_returns`),** but committed artifact still shows 2000 — regenerate when unblocked. `cost_impact` sub-block hardcodes `n_simulations: 2000` in metadata while calling 3000 — harmonize.
3. **Missing artifacts:** **CODE DONE** — `cointegration_diagnostics`, `parameter_stability`, `tail_risk`, `blocked_routes` all present in `run_portfolio_real.py` artifact; committed copy is null/stale. Regenerate.
4. **Parallelization:** **DONE** — `max_workers = min(4, os.cpu_count() or 1)`, deterministic submission order, checkpoint/resume kept.
5. **Data quality:** inner-join on observed timestamps, no interpolation/backfill/fabrication; exclusions recorded in `universe_changes`/`exclusions_with_rationale`.
6. **Observability/determinism:** `flush=True` throughout, fixed seeds (12345, 12347, 54321), full provenance, checkpoint file `reports/.portfolio_real_checkpoint.json`.

## INITIAL TASK MESSAGE FOR NEXT AGENTIC SESSION (TIMESTAMP: 2026-10-31T07:25:48Z)

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
Fix immediately if broken. **Do not proceed until green.** Loader hardening from this session is already in `data/loader.py` (uncommitted) — keep it.

#### 1) BOTTLENECK: ARTIFACT REGENERATION UNDER 451 BLOCK
- Run `python -u examples/run_portfolio_real.py`. Expect 451 on all hosts → `main()` returns early, **preserve** `reports/portfolio_real.json`, confirm `blocked_routes` attempt logs are written.
- Harmonize `bootstrap_ci_portfolio_oos.cost_impact.n_simulations` (2000 metadata vs 3000 call) → make it 3000 everywhere.
- Add block-bootstrap option to `bootstrap_trade_returns` if absent; keep network-independent.

#### 2) DEEP COINTEGRATION RIGOR (CORE)
Audit/harden `utils/cointegration.py` and `strategies/pairs_trading.py`:
- **EG:** ADF/KPSS on legs and residuals, lag selection, strict thresholds; log fully.
- **Johansen:** trace/max-eigenvalue ranks/critical values/stats.
- **Rolling stability:** 90d/180d windows; require stability or penalize/exclude.
- **Half-life/OU:** bounds 1 < hl < 500; exclude non-mean-reverting/extreme.
- **Structural breaks:** CUSUM/Chow/rolling param stability; flag/exclude.
- **Spread quality:** ADF on spread, Hurst exponent, stationarity. Full per-pair logs + provenance.

#### 3) UNIVERSE EXPANSION WITH IRONCLAD GATES (REAL-ONLY)
Candidates: ARB, OP, NEAR, INJ, APT, SUI, TIA, SEI, BCH, ETC, ATOM, UNI, AAVE, LINK, LTC, AVAX, DOGE. Attempt real Binance spot 1h+4f 2026-04-01→2026-10-30 with ALL gates. Admit only if pass. Update PAIRS with justification. Record every inclusion/exclusion in `universe_changes`/`exclusions_with_rationale` with full attempt logs. If blocked (451) → document in `blocked_routes` and exclude with rationale.

#### 4) PARAMETER STABILITY & WALK-FORWARD
- >=16 splits per pair where feasible; IS/OOS degradation + stability scores.
- Regime-aware stability tests for top params.
- Sensitivity grid around optimal with stability metrics.
- Enrich `multi_timeframe_walk_forward` with per-pair breakdowns (1h/4h/1d, >=12 splits each).

#### 5) BOOTSTRAP >=3000 + TAIL RIGOR
- `bootstrap_ci_portfolio_oos.n_simulations` **>=3000**, fixed seed logged; add block-bootstrap option.
- Add `tail_risk`: VaR/CVaR/CDaR at 95%/99%/99.9%, expected shortfall, regime-conditioned.
- Regime-conditional bootstrap CIs, permutation tests vs zero, cost-impact across bootstrap.
- Network-independent.

#### 6) ARTIFACT ENRICHMENT (SCHEMA-COMPLETE, BACKWARDS COMPATIBLE)
Update `reports/portfolio_real.json` in-place when data is available:
- `cointegration_diagnostics` (per-pair EG/Johansen/rolling/hl/breaks/spread quality + provenance)
- `parameter_stability` (splits/regimes/sensitivity)
- `tail_risk` (VaR/CVaR/CDaR multiple levels, regime-conditioned)
- `blocked_routes` (host/endpoint/status/latency_ms/error/timestamps)
- `bootstrap_ci_portfolio_oos` >=3000 sims, seeds, block-bootstrap, regime-conditional CIs, permutation p-values
- Preserve all existing hardened fields; keep `real_data_only: true`, `fabricated_data: false`.

#### 7) TESTS + DOCS (IMPOSSIBLE TO COAST)
- Network-independent tests for cointegration gates, half-life bounds, stability, artifact schema extensions
- **Tests preventing fabricated cointegration results when data unavailable** (refuse to emit diagnostics when Binance blocked)
- Strengthen assertions for real-data-only + provenance completeness
- Update `README.md` with cointegration rigor, pair selection rationale, reproduction commands

#### 8) VERIFY & DELIVER (ZERO REGRESSIONS)
```bash
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
- **BOTTLENOCK REMOVAL** — eliminate inefficiencies immediately (loader hardening done; artifact regeneration is the live bottleneck).
- **IMPOSSIBLE TO COAST** — every step must produce checkable artifact/test/provenance.
- **UNBUFFERED** — `python -u`, `flush=True`.
- **REPRODUCIBILITY** — fixed seeds, deterministic ordering, full config logged.

**CAMPAIGN PHASE 4c COMPLETE ONLY WHEN ALL CRITERIA MET. START IMMEDIATELY.**
