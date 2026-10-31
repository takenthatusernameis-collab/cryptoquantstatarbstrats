# DURABLE HANDOFF (2026-10-31T01:23:21Z) — SINGLE MANDATORY NEXT TASK: CRYPTO QUANT STAT ARB - UNIVERSE EXPANSION + PRODUCTION HARDENING

## REPO IDENTITY (LAW)
- **REPO:** `cryptoquantstatarbstrats` — *Crypto Quant Stat Arb Strategies*
- **PRIORITY:** Pure real-data crypto statistical arbitrage. Cointegration, pair stability, liquidity/overlap, and falsifiability > backtested optics.
- **MANDATE:** **ONLY REAL market data** (Binance public REST). Synthetic/fabricated data is strictly limited to isolated unit tests with explicit `fabricated_data: true` warnings.
- **COASTING = FAILURE.** Every action must produce checkable artifacts, tests, provenance, and logs. Future agents cannot avoid heavy validation.

## VERIFIED GREEN BASELINE (DO NOT REGRESS)
- **Branch:** `main` (clean)
- **Tests:** `PYTHONPATH=. python -m pytest tests/ -q` → **529 passed, 1 skipped**
- **Types:** `python -m mypy backtest/ strategies/ utils/` → **Success: no issues found in 31 source files**
- **Lint:** `python -m ruff check backtest/ strategies/ utils/ tests/` → **All checks passed!**
- **Artifact:** `reports/portfolio_real.json` (real-only). 11 symbols, 17 pairs, 1h 2026-04-01→2026-10-30 (5112 bars).

## BOTTLENECKS TO KILL (REMOVE FRICTION NOW)
- **I/O:** Use `python -u`, `flush=True` for critical logs. Never block on unbuffered output.
- **Network:** Exponential backoff + retries on all Binance calls. Log attempt (host/endpoint/status/latency_ms/error). Treat partial pages as failures unless fully accounted for. One bounded preflight per material change. Permanent 451/403/404 = blocked route (do not spam).
- **Parallelism:** Bounded concurrency (semaphore), deterministic ordering, per-shard checkpoints, resume-safe. Parallelize independent network-free work while blocked.
- **Data completeness:** Insufficient overlap/gaps → **EXCLUDE** with full rationale + attempt log. Never interpolate/backfill/fabricate.
- **Determinism:** Fix seeds for stochastic paths (bootstrap/MC/splits/selection). Log seeds/config/hashes.
- **Observability:** Per-pair/per-symbol/per-TF/per-split logs (bars/ranges/gaps/NaNs/dupes). Structured file+console logs.
- **Regression discipline:** Lint/type/test break → fix immediately before proceeding.

## INITIAL TASK MESSAGE FOR NEXT AGENTIC SESSION (TIMESTAMP: 2026-10-31T01:23:21Z)

**START NOW. HEAVY WORK MANDATORY. DO NOT COAST.**

### PRIMARY OBJECTIVE
Scale and harden the real-data crypto stat arb system to production-grade. Expand the tradable universe with ironclad proof, deepen multi-TF rigor, add rigorous bootstrap significance, harden volume-aware execution + extreme cost stress, enrich tails/correlations/regimes/circuit breakers, and make the artifact schema-complete and auditably testable. Every step must leave verifiable artifacts, tests, and provenance.

### MANDATORY SEQUENCE (IN ORDER)

#### 0) RESTORE & VERIFY GREEN (BLOCKING)
```bash
python -m ruff check backtest/ strategies/ utils/ tests/ && \
PYTHONPATH=. python -m pytest tests/ -q && \
python -m mypy backtest/ strategies/ utils/
```
Fix immediately if broken.

#### 1) BRUTAL AUDIT (PARALLELIZE & FIX)
Read with intent:
- `examples/run_portfolio_real.py`, `reports/portfolio_real.json`
- `tests/test_portfolio_real*.py`, `tests/test_portfolio_risk_controls.py`
- `backtest/engine.py`, `backtest/sweep.py`
- `utils/portfolio_risk.py`, `utils/regime.py`, `utils/monte_carlo.py`, `utils/risk.py`
- `data/loader.py`, `strategies/pairs_trading.py`

Build a dependency graph, identify independent streams, add/checkpointing, remove serial waits. Log bottlenecks + fixes.

#### 2) AGGRESSIVE REAL-ONLY UNIVERSE EXPANSION (PROVEN LIQUIDITY + OVERLAP)
Candidates (validate all): **ARB, OP, NEAR, INJ, APT, SUI, TIA, SEI, BCH, ETC, ATOM, UNI, AAVE, LINK, LTC, AVAX** (+ others only if provable).

For each candidate symbol/pair: fetch real Binance spot history for needed windows/TFs via `python -u` with retries/backoff/full attempt logs (host/endpoint/status/latency_ms/errors/timestamps). Verify overlap/gaps/bar counts/dupes/NaNs. Run cointegration/stability on real window with provenance. Admit only if ALL gates pass. Update `PAIRS`/`SYMBOLS` in `examples/run_portfolio_real.py` with justification.

Record EVERY inclusion/exclusion in `universe_changes` and `exclusions_with_rationale` with attempt counts, hosts/endpoints, concrete reasons.

#### 3) MULTI-TIMEFRAME RIGOR (>=12 SPLITS)
Enforce rolling walk-forward on **1h, 4h, 1d** with >=12 splits each. Document train/test rationale, per-split IS/OOS/stability/degradation/regime/turnover/leverage, per-pair/per-TF breakdowns, full provenance (params/windows/bars/seeds/hashes). Increase to >=12 if data allows with justification. Emit as `multi_timeframe_walk_forward`.

#### 4) DEEP STATISTICAL SIGNIFICANCE (BOOTSTRAP)
Bootstrap/shuffle MC on real OOS portfolio returns: >=3000 sims, fixed seeds (logged), reproducible. 95% CIs for total return/Sharpe/maxDD/CAGR/Calmar (portfolio + per-TF). Distinguishability from zero, p-values where meaningful. Block bootstrap by regime/time if sensible. Cost grid impact. Network-independent. Attach as `bootstrap_ci_portfolio_oos` with full provenance.

#### 5) VOLUME-AWARE EXECUTION + EXTREME COST-STRESS
Fetch real Binance quote volume/turnover for full window (exhaustive attempts, log hosts/failures/endpoints). Omit only with full rationale. Extend volume-aware slippage/participation model (assumptions + market impact heuristics grounded in real data; no fabrication). Add broad cost-stress grid (fees × slippage × participation), execution diagnostics (turnover/capacity/hit-rate), attach as `volume_aware_execution` with full attempt logs.

#### 6) TAILS, CORRELATIONS, REGIMES & CIRCUIT BREAKERS
Enrich VaR/CVaR/CDaR at multiple confidence levels + methodology. Correlation matrix + rolling correlation stability (regime-aware). Regime-conditioned performance with clear definitions. Strengthen circuit breakers, log all trips/blocks. Per-asset contribution, gross/net/leverage, concentration. Funding/basis provenance (or explicit omission rationale).

#### 7) ARTIFACT ENRICHMENT (SCHEMA-COMPLETE)
Enrich `reports/portfolio_real.json` in-place if compatible. MUST include:
- `real_data_only: true`, `fabricated_data: false`
- Expanded universe + `universe_changes` + `exclusions_with_rationale` (full attempt logs)
- Per-TF IS/OOS per split + stability/degradation
- `multi_timeframe_walk_forward` with >=12 splits each
- `bootstrap_ci_portfolio_oos` with >=3000 sims, 95% CIs, seeds, config
- `volume_aware_execution` + full cost-stress grid + provenance
- Per-asset contribution, turnover, leverage/gross/net exposure, concentration
- Correlation matrix + rolling stability
- Tail metrics (VaR/CVaR/CDaR) + regime-conditioned performance
- Funding/basis provenance (or explicit omission rationale)
- Risk controls applied, circuit breaker results (with logs)
- JSON-serializable, schema-validated by tests

#### 8) TESTS + DOCS HARDEN (IMPOSSIBLE TO COAST)
- Add network-independent stress tests: portfolio logic, risk controls, meta-selector, artifact schema, bootstrap CI, execution model, edge cases, data quality gates
- Strengthen assertions around `real_data_only`/`fabricated_data` and required hardened fields
- Update `README.md` with hardened findings, concrete real-data numbers, explicit real-data-only provenance, coverage summary, reproduction commands
- Add negative tests for exclusion paths

#### 9) VERIFY & DELIVER (ZERO REGRESSIONS)
```bash
python -u examples/run_portfolio_real.py
PYTHONPATH=. python -m pytest tests/ -q  # >=529 passed, 0 new failures
python -m ruff check backtest/ strategies/ utils/ tests/  # clean
python -m mypy backtest/ strategies/ utils/  # clean
```
All deliverables present and valid. Do not commit unless explicitly requested.

## HARD CONSTRAINTS
- **REAL DATA ONLY** — No synthetic/fabricated data. Ever. Only isolated unit tests may use fabricated data with explicit `fabricated_data: true` warnings.
- **NO SHORTCUTS** — Omit+document if unavailable after exhaustive attempts with full provenance (hosts/endpoints/errors/counts/timestamps).
- **PRESERVE GREEN** — Zero regressions. Restore green before proceeding.
- **HEAVY MANDATE** — Complete the full campaign. Do not stop early.
- **BOTTLENECK REMOVAL** — Eliminate inefficiencies immediately (parallelize, retry, log, unbuffer, checkpoint shards, dependency graph).
- **IMPOSSIBLE TO COAST** — Structure work so future agents cannot avoid heavy validation; every step must produce checkable artifact/test/provenance.
- **UNBUFFERED OUTPUT** — Use `python -u` for all long-running real-data jobs. Add `flush=True` for critical logs.
- **REPRODUCIBILITY** — Seeds for stochastic parts; log all config. Deterministic ordering.
- **NO ALTERATION OF LIVE/PAPER BOUNDARIES** — Do not change trading boundaries or commit policy.

**CAMPAIGN COMPLETE ONLY WHEN ALL CRITERIA MET. START IMMEDIATELY.**
