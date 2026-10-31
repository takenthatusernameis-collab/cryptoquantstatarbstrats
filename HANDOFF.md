# DURABLE HANDOFF (2026-10-31T03:25:09Z) — SINGLE MANDATORY NEXT TASK: CRYPTO QUANT STAT ARB - BATTLE-TESTED & PUBLICATION-GRADE (PHASE 3)

## REPO IDENTITY (LAW)
- **REPO:** `cryptoquantstatarbstrats` — *Crypto Quant Stat Arb Strategies*
- **CORE PRIORITY (from repo name):** Crypto + Quant + Statistical Arbitrage. **Cointegration/pairs trading is THE CORE.** Everything must serve real-data cointegration rigor, falsifiability, cost-robustness, and regime-awareness over optics.
- **MANDATE:** **REAL DATA ONLY** (Binance public REST). Synthetic/fabricated data strictly limited to isolated unit tests with explicit `fabricated_data: true` warnings. No silent fabrication.
- **COASTING = FAILURE.** Every action must produce checkable artifacts, tests, provenance, and logs.
- **HEAVY WORK MANDATORY. DO NOT COAST. IMPOSSIBLE TO COAST.**

## VERIFIED GREEN BASELINE (DO NOT REGRESS) — verified 2026-10-31T03:25:09Z
- **Branch:** `main` (clean), up to date with `origin/main`.
- **Lint:** `python -m ruff check backtest/ strategies/ utils/ tests/ examples/` → **All checks passed!**
- **Tests:** `PYTHONPATH=. python -m pytest tests/ -q` → **529 passed, 1 skipped** (77 warnings, none failing).
- **Type:** `python -m mypy backtest/ strategies/ utils/` → **Success: no issues found in 31 source files.**
- **Artifact:** `reports/portfolio_real.json` (real-only, committed). Contains hardened blocks: multi-TF walk-forward (1h/4h/1d), bootstrap CI (>=2000 sims), volume-aware execution with attempt logs, regime meta-selector, risk controls/circuit breakers, cost-stress grid. **Preserve as provenance. Never fabricate.**
- **Network:** Binance public REST returns **HTTP 451** in this environment (known). Treat as blocked routes, log exhaustively, preserve committed artifact.

## BOTTLENECKS IDENTIFIED & REMEDIATED (PRE-EMPTIVE)
- **NETWORK BLOCK (ACTIVE):** 451/403 on Binance routes. Log host/endpoint/status/latency_ms/error per attempt. Bounded exponential backoff. **Do NOT** spam retries. Preserve committed artifact; never fabricate.
- **I/O/STREAMING:** Use `python -u`, `flush=True` for critical logs.
- **PARALLELISM:** Bounded concurrency (semaphore), deterministic ordering, per-shard checkpoints/resume-safe.
- **DATA QUALITY GATES:** Insufficient overlap/gaps/dupes/NaNs → **EXCLUDE** with full rationale + attempt log. No interpolation/backfill/fabrication.
- **DETERMINISM/OBSERVABILITY:** Fixed seeds logged, structured per-pair/per-symbol/per-TF logs, full provenance (params/windows/bars/seeds/hashes).
- **REGRESSION DISCIPLINE:** Lint/type/test break → fix immediately before proceeding.
- **AGENT TOOLING:** Edit operations must use correct schema (filePath/oldString/newString). Avoid invalid tool calls.

## INITIAL TASK MESSAGE FOR NEXT AGENTIC SESSION (TIMESTAMP: 2026-10-31T03:25:09Z)

**START NOW. HEAVY WORK MANDATORY. DO NOT COAST. IMPOSSIBLE TO COAST.**

### PRIMARY OBJECTIVE
Make this crypto stat arb system **battle-tested and publication-grade**. Close every remaining gap with ironclad provenance. Prove robustness to costs/regimes/tails. Make future agents unable to avoid heavy validation. **Real data only. Binance 451 is known - preserve committed artifact, run network-independent tests, never fabricate, log blocked routes exhaustively.**

### MANDATORY SEQUENCE (IN ORDER, NO SHORTCUTS)

#### 0) RESTORE & VERIFY GREEN (BLOCKING)
```bash
export PATH=/home/runner/work/_temp/kilo-home/.local/bin:$PATH
python -m ruff check backtest/ strategies/ utils/ tests/ examples/ && \
PYTHONPATH=. python -m pytest tests/ -q && \
python -m mypy backtest/ strategies/ utils/
```
Fix immediately if broken. **Do not proceed until green.** (Already green as of 2026-10-31T03:25:09Z — confirm before proceeding.)

#### 1) BRUTAL AUDIT + BOTTLENECK ELIMINATION (PARALLELIZE)
Read with intent (build dependency graph, parallelize independent work):
- `examples/run_portfolio_real.py`, `reports/portfolio_real.json`
- `tests/test_portfolio_real*.py`, `tests/test_portfolio_risk_controls.py`
- `backtest/engine.py`, `backtest/sweep.py`, `backtest/metrics.py`
- `utils/portfolio_risk.py`, `utils/regime.py`, `utils/monte_carlo.py`, `utils/risk.py`
- `data/loader.py`, `strategies/pairs_trading.py`

Actions:
- Eliminate serial waits, add bounded concurrency where safe/deterministic
- Add/checkpointing for long runs, unbuffered logging
- Log every bottleneck found + fix applied with before/after evidence
- Remove hidden sleeps/polling

#### 2) REAL-ONLY UNIVERSE EXPANSION WITH IRONCLAD PROVENANCE (COINTEGRATION-FIRST)
Candidates (prioritize liquid majors + high-quality alts): ARB, OP, NEAR, INJ, APT, SUI, TIA, SEI, BCH, ETC, ATOM, UNI, AAVE, LINK, LTC, AVAX, DOGE (careful), MATIC/POL already present.
For each: attempt real Binance spot 1h + 4h for 2026-04-01→2026-10-30 via `python -u` with bounded retries/backoff. Verify overlap/gaps/bar counts/dupes/NaNs. Require cointegration on real window (Engle-Granger) with stability checks.
**Only admit if ALL gates pass.** Update `PAIRS`/`SYMBOLS` in `examples/run_portfolio_real.py` with justification.
Record EVERY inclusion/exclusion in `universe_changes` and `exclusions_with_rationale` with attempt counts, hosts/endpoints, status/latency_ms, timestamps, concrete reasons. **If blocked (451), document blocked route and exclude with rationale — never fabricate.**

#### 3) MULTI-TIMEFRAME RIGOR (>=12 SPLITS, HARDENED) — PRIORITY
Enforce rolling walk-forward on **1h, 4h, 1d** with **>=12 splits each**. Per split: IS/OOS returns/Sharpe/maxDD, stability/degradation, regime, turnover, leverage. If <12 splits possible, justify with hard data constraints (bars/gaps). Emit enriched `multi_timeframe_walk_forward` with full provenance (params/windows/bars/seeds/hashes). Ensure per-pair/per-TF breakdowns where feasible.

#### 4) DEEP STATISTICAL SIGNIFICANCE (BOOTSTRAP HARDENED) — PRIORITY
Bootstrap/shuffle MC on real OOS portfolio returns: **>=3000 sims** (increase from 2000 if feasible without unacceptable slowdown), fixed seeds logged, reproducible. 95%/99% CIs for total return/Sharpe/maxDD/CAGR/Calmar (portfolio + per-TF). Distinguishability from zero (p-values), risk-of-ruin. Cost grid impact baked in. Network-independent. Attach as `bootstrap_ci_portfolio_oos` with full provenance.

#### 5) VOLUME-AWARE EXECUTION + EXTREME COST-STRESS
Fetch real Binance quote volume/turnover for full window with exhaustive attempts (log hosts/endpoints/status/errors/latency_ms/counts). Omit only with full rationale. Harden volume-aware slippage/participation + market impact heuristics grounded in real data; **no fabrication**. Extend cost-stress grid to extremes (fees/slippage/participation) with execution diagnostics (turnover/capacity/hit-rate/impact). If blocked (451), record `volume_fetch_status: blocked` + `blocked_routes` + attempt logs; do **not** zero-fill/fabricate. Attach as `volume_aware_execution`.

#### 6) TAILS, CORRELATIONS, REGIMES & CIRCUIT BREAKERS (HARDENED)
Enrich VaR/CVaR/CDaR at multiple confidence levels + methodology. Rolling correlation matrix + stability by regime. Regime-conditioned performance with explicit definitions. Strengthen circuit breakers (test paths), log all trips/blocks. Per-asset contribution, gross/net/leverage, concentration (HHI). Funding/basis provenance or explicit omission rationale (must reflect actual attempts).

#### 7) ARTIFACT ENRICHMENT (SCHEMA-COMPLETE, BACKWARDS COMPATIBLE)
Enrich `reports/portfolio_real.json` in-place if compatible. **MUST** include:
- `real_data_only: true`, `fabricated_data: false`
- Expanded universe + `universe_changes` + `exclusions_with_rationale` (full attempt logs)
- Per-TF IS/OOS per split + stability/degradation
- `multi_timeframe_walk_forward` with >=12 splits each + provenance
- `bootstrap_ci_portfolio_oos` with >=3000 sims, 95%/99% CIs, seeds, config, distinguishability_from_zero, cost_impact
- `volume_aware_execution` + full cost-stress grid + provenance + blocked_routes if applicable
- Per-asset contribution, turnover, leverage/gross/net exposure, concentration
- Correlation matrix + rolling stability by regime
- Tail metrics (VaR/CVaR/CDaR) + regime-conditioned performance
- Funding/basis provenance (or explicit omission rationale with attempts)
- Risk controls applied, circuit breaker results (with logs)
- JSON-serializable, schema-validated by tests

#### 8) TESTS + DOCS HARDEN (IMPOSSIBLE TO COAST)
- Add network-independent stress tests: portfolio logic, risk controls, meta-selector, artifact schema, bootstrap CI (>=3000), execution model, edge cases, data quality gates
- Strengthen assertions around `real_data_only`/`fabricated_data` and required hardened fields
- Update `README.md` with hardened findings, concrete real-data numbers, explicit real-data-only provenance, coverage summary, reproduction commands
- Add negative tests for exclusion paths
- **Add a test asserting the committed artifact is not regenerated with fabricated data when Binance is blocked (451): real_volume_attempts logged, blocked_routes present if applicable, no silent zero-fill.**

#### 9) VERIFY & DELIVER (ZERO REGRESSIONS)
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
- **NO SHORTCUTS** — Omit+document if unavailable after exhaustive attempts with full provenance (hosts/endpoints/errors/counts/timestamps/latency_ms).
- **PRESERVE GREEN** — Zero regressions. Restore green before proceeding.
- **HEAVY MANDATE** — Complete the full campaign. Do not stop early.
- **BOTTLENECK REMOVAL** — Eliminate inefficiencies immediately (parallelize, retry with backoff, log, unbuffer, checkpoint shards, dependency graph). Binance 451 = blocked route; preserve committed artifact, never fabricate.
- **IMPOSSIBLE TO COAST** — Structure work so future agents cannot avoid heavy validation; every step must produce checkable artifact/test/provenance.
- **UNBUFFERED OUTPUT** — Use `python -u` for all long-running real-data jobs. Add `flush=True` for critical logs.
- **REPRODUCIBILITY** — Seeds for stochastic parts; log all config. Deterministic ordering.
- **NO ALTERATION OF LIVE/PAPER BOUNDARIES** — Do not change trading boundaries or commit policy.

**CAMPAIGN PHASE 3 COMPLETE ONLY WHEN ALL CRITERIA MET. START IMMEDIATELY.**
