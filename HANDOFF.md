# DURABLE HANDOFF (2026-10-31T03:29:42Z) — SINGLE MANDATORY NEXT TASK: CRYPTO QUANT STAT ARB - COINTEGRATION RIGOR & PUBLICATION-GRADE (PHASE 4)

## REPO IDENTITY (LAW)
- **REPO:** `cryptoquantstatarbstrats` — *Crypto Quant Stat Arb Strategies*
- **CORE PRIORITY (from repo name):** Crypto + Quant + Statistical Arbitrage. **Cointegration/pairs trading is THE CORE.** Everything must serve real-data cointegration rigor, falsifiability, cost-robustness, and regime-awareness over optics.
- **MANDATE:** **REAL DATA ONLY** (Binance public REST). Synthetic/fabricated data strictly limited to isolated unit tests with explicit `fabricated_data: true` warnings. No silent fabrication.
- **COASTING = FAILURE.** Every action must produce checkable artifacts, tests, provenance, and logs.
- **HEAVY WORK MANDATORY. DO NOT COAST. IMPOSSIBLE TO COAST.**

## VERIFIED GREEN BASELINE (DO NOT REGRESS) — verified 2026-10-31T03:29:42Z
- **Branch:** `main` (clean), up to date with `origin/main`.
- **Lint:** `python -m ruff check backtest/ strategies/ utils/ tests/ examples/` → **All checks passed!**
- **Tests:** `PYTHONPATH=. python -m pytest tests/ -q` → **529 passed, 1 skipped** (77 warnings, none failing).
- **Type:** `python -m mypy backtest/ strategies/ utils/` → **Success: no issues found in 31 source files.**
- **Artifact:** `reports/portfolio_real.json` (real-only, committed). Hardened with multi-TF walk-forward (>=12 splits), bootstrap CI (2000 sims), volume-aware execution with attempt logs, regime meta-selector, risk controls/circuit breakers, cost-stress grid. **Preserve as provenance. Never fabricate.** Missing: `cointegration_diagnostics`; bootstrap at 2000 (needs >=3000).
- **Network:** Binance public REST returns **HTTP 451** in parts; www.binance.com paths work for some endpoints. Treat as blocked routes, log exhaustively, preserve committed artifact.

## BOTTLENECKS TO ELIMINATE (ACTIVE)
- **NETWORK BLOCK (ACTIVE):** 451/403 on Binance routes. Log host/endpoint/status/latency_ms/error per attempt. Bounded exponential backoff. **Do NOT** spam retries. Preserve committed artifact; never fabricate.
- **SERIAL SWEEPS (PRIORITY):** Pairwise parameter sweeps are sequential in `examples/run_portfolio_real.py`. Parallelize with bounded concurrency (ProcessPoolExecutor/threading with semaphore) while keeping deterministic ordering and checkpointing.
- **I/O/STREAMING:** Use `python -u`, `flush=True` for critical logs.
- **DATA QUALITY GATES:** Insufficient overlap/gaps/dupes/NaNs → **EXCLUDE** with full rationale + attempt log. No interpolation/backfill/fabrication.
- **DETERMINISM/OBSERVABILITY:** Fixed seeds logged, structured per-pair/per-symbol/per-TF logs, full provenance (params/windows/bars/seeds/hashes).
- **REGRESSION DISCIPLINE:** Lint/type/test break → fix immediately before proceeding.

## INITIAL TASK MESSAGE FOR NEXT AGENTIC SESSION (TIMESTAMP: 2026-10-31T03:29:42Z)

**START NOW. HEAVY WORK MANDATORY. DO NOT COAST. IMPOSSIBLE TO COAST.**

### PRIMARY OBJECTIVE
Make this crypto stat arb system **publication-grade on cointegration rigor**. Go deeper on Engle-Granger/Johansen robustness, parameter stability, structural breaks, regime-conditional cointegration, and out-of-sample falsification. Prove the edge survives strict costs/tails/regimes. **Real data only. Binance 451 is known - preserve committed artifact, run network-independent tests, never fabricate, log blocked routes exhaustively.**

### MANDATORY SEQUENCE (IN ORDER, NO SHORTCUTS)

#### 0) RESTORE & VERIFY GREEN (BLOCKING)
```bash
export PATH=/home/runner/work/_temp/kilo-home/.local/bin:$PATH
python -m ruff check backtest/ strategies/ utils/ tests/ examples/ && \
PYTHONPATH=. python -m pytest tests/ -q && \
python -m mypy backtest/ strategies/ utils/
```
Fix immediately if broken. **Do not proceed until green.**

#### 1) BOTTLENECK ELIMINATION - PARALLELIZE & OPTIMIZE (PRIORITY)
- Parallelize pairwise sweeps in `examples/run_portfolio_real.py` with bounded concurrency (e.g., `max_workers=min(4, os.cpu_count())`) preserving deterministic order of results.
- Add per-pair checkpoints/resume for sweeps (extend existing checkpoint mechanism).
- Ensure unbuffered logging everywhere for long runs.
- Remove any hidden sleeps/polling. Log before/after timing with evidence.
- Keep full provenance of parallel execution (worker counts, wall times).

#### 2) DEEP COINTEGRATION RIGOR (CORE - HEAVY WORK)
Audit and harden `strategies/pairs_trading.py` and related utils:
- **Engle-Granger**: unit root tests (ADF/KPSS) on legs and residuals, lag selection, strict p-value thresholds, avoid spurious matches.
- **Johansen** trace/max-eigenvalue where feasible (real data only). Log ranks, critical values, trace stats.
- **Stability**: rolling cointegration (e.g., 90d/180d windows) - require stability across windows or penalize/exclude.
- **Half-life / mean reversion**: estimate half-life of residual OU process; enforce reasonable bounds, exclude if non-mean-reverting or extreme.
- **Structural breaks**: check for breaks (CUSUM/Chow or simple rolling parameter stability). Flag/exclude unstable pairs.
- **Spread quality**: ADF p-value on spread, Hurst/exponent, stationarity diagnostics. Full logs per pair.
- Update pair selection to use these gates. Record every test result in provenance.

#### 3) EXPAND COINTEGRATION UNIVERSE WITH IRONCLAD GATES (REAL-ONLY)
Candidates to test (prioritize liquid majors/high-quality): ARB, OP, NEAR, INJ, APT, SUI, TIA, SEI, BCH, ETC, ATOM, UNI, AAVE, LINK, LTC, AVAX, DOGE (careful).
For each candidate pair: exhaustively attempt real Binance spot 1h+4h 2026-04-01→2026-10-30. Require ALL gates to pass (unit roots consistent, cointegration p<0.05 or Johansen rank>=1 with justification, rolling stability, reasonable half-life, no structural breaks).
**Only admit if all pass.** Update `PAIRS` in `examples/run_portfolio_real.py` with justification. Record EVERY inclusion/exclusion in `universe_changes`/`exclusions_with_rationale` with attempt counts/hosts/endpoints/status/latency_ms/timestamps/reasons. If blocked (451), document blocked route and exclude with rationale - never fabricate.

#### 4) PARAMETER STABILITY & WALK-FORWARD HARDENING
- Per-pair walk-forward with more splits where data allows (>=16 splits where feasible). Show IS/OOS degradation per pair.
- Parameter stability across regimes/time - test top params hold across different market regimes.
- Add sensitivity analysis (grid around optimal) with stability metrics.
- Enrich `multi_timeframe_walk_forward` with per-pair breakdowns and stability scores.

#### 5) BOOTSTRAP TO >=3000 SIMS + TAIL RIGOR
- Increase bootstrap to **>=3000 simulations** (fixed seeds logged). Add block bootstrap option for time-series dependence.
- Richer tail metrics: VaR/CVaR/CDaR at 95%/99%/99.9%, expected shortfall profiles.
- Regime-conditional bootstrap CIs.
- Distinguishability from zero with permutation tests. Cost-impact across bootstrap (already present, strengthen).
- Network-independent.

#### 6) ARTIFACT ENRICHMENT (SCHEMA-COMPLETE, BACKWARDS COMPATIBLE)
Enrich `reports/portfolio_real.json` in-place if compatible. MUST include:
- `cointegration_diagnostics`: per-pair (ADF on legs/residuals, Johansen if run, rolling stability, half-life, structural breaks, spread quality) with full provenance
- `universe_changes` + `exclusions_with_rationale` (full attempt logs with hosts/endpoints/status/latency_ms)
- `parameter_stability`: per-pair stability across splits/regimes
- `multi_timeframe_walk_forward` with >=12 splits each + per-pair breakdowns where feasible
- `bootstrap_ci_portfolio_oos` with >=3000 sims, 95%/99% CIs, seeds, block-bootstrap if added, regime-conditional CIs, permutation p-values
- `volume_aware_execution` + full cost-stress grid + blocked_routes if applicable
- `tail_risk`: VaR/CVaR/CDaR at multiple levels + regime-conditioned
- All existing hardened fields preserved

#### 7) TESTS + DOCS HARDEN (IMPOSSIBLE TO COAST)
- Add network-independent tests for cointegration gates (ADF/Johansen logic, half-life bounds, stability checks)
- Test parameter stability metrics and artifact schema extensions
- Strengthen assertions around real-data-only and provenance completeness
- Update `README.md` with cointegration rigor findings, pair selection rationale, reproduction commands
- Add tests preventing fabricated cointegration results when data unavailable

#### 8) VERIFY & DELIVER (ZERO REGRESSIONS)
```bash
export PATH=/home/runner/work/_temp/kilo-home/.local/bin:$PATH
python -u examples/run_portfolio_real.py   # only if Binance access restored; else skip live fetch, preserve committed artifact
PYTHONPATH=. python -m pytest tests/ -q    # >=529 passed, 0 new failures
python -m ruff check backtest/ strategies/ utils/ tests/ examples/  # clean
python -m mypy backtest/ strategies/ utils/  # clean
```
All deliverables present and valid. Do not commit unless explicitly requested.

## HARD CONSTRAINTS
- **REAL DATA ONLY** — No synthetic/fabricated data. Ever. Only isolated unit tests may use fabricated data with explicit `fabricated_data: true` warnings.
- **NO SHORTCUTS** — Omit+document if unavailable after exhaustive attempts with full provenance.
- **PRESERVE GREEN** — Zero regressions. Restore green before proceeding.
- **HEAVY MANDATE** — Complete the full campaign. Do not stop early.
- **BOTTLENECK REMOVAL** — Eliminate inefficiencies immediately (parallelize, retry with backoff, log, unbuffer, checkpoint shards).
- **IMPOSSIBLE TO COAST** — Structure work so future agents cannot avoid heavy validation; every step must produce checkable artifact/test/provenance.
- **UNBUFFERED OUTPUT** — Use `python -u` for all long-running real-data jobs. Add `flush=True` for critical logs.
- **REPRODUCIBILITY** — Seeds for stochastic parts; log all config. Deterministic ordering.

**CAMPAIGN PHASE 4 COMPLETE ONLY WHEN ALL CRITERIA MET. START IMMEDIATELY.**
