# DURABLE HANDOFF (2026-10-31T00:37:20Z) — SINGLE MANDATORY NEXT TASK: CRYPTO STAT ARB SCALE-UP v2 (UN-COASTABLE, HEAVY EXECUTION)

## REPO IDENTITY (LAW)
- **REPO:** `cryptoquantstatarbstrats` — *Crypto Quant Stat Arb Strategies*
- **PRIORITY:** Pure real-data crypto statistical arbitrage. Market microstructure, pair stability, and falsifiability take absolute precedence.
- **MANDATE:** **ONLY REAL market data** (Binance public REST). Never fabricate candles, funding, basis, IV, volume, or returns. Synthetic data is strictly limited to isolated unit tests with explicit `fabricated_data: true` warnings.
- **COASTING = FAILURE.** Every action must produce checkable artifacts, tests, provenance, and logs. Future agents cannot avoid heavy validation.

## VERIFIED GREEN STATE (PRESERVE AT ALL COSTS)
- **Branch:** `main` (clean)
- **Tests:** `PYTHONPATH=. python -m pytest tests/ -q` → **529 passed, 1 skipped** (GREEN) — +1 since last handoff
- **Types:** `python -m mypy backtest/ strategies/ utils/` → **Success: no issues found in 31 source files** (GREEN)
- **Lint:** `python -m ruff check backtest/ strategies/ utils/ tests/` → **All checks passed!** (GREEN)
- **Baseline:** `reports/portfolio_real.json` (real-only). Hardened risk controls, multi-TF walk-forward (≥12 splits), bootstrap CIs, volume-aware execution, full provenance. Current universe includes 11 symbols across 17 pairs (BTC/ETH/SOL/BNB/ADA/XRP/DOT/POL/AVAX/LINK/LTC).

## BOTTLENECKS TO ELIMINATE (DO FIRST - REMOVE ALL FRICTION)
Kill these immediately to maximize throughput without cutting corners:

- **I/O:** Run all long jobs with `python -u`. Add `flush=True` for critical logs. Never buffer indefinitely.
- **Network:** Exponential backoff + retries on ALL Binance calls. Log every attempt (host, endpoint, status, latency_ms, error class). Treat partial pages as failures unless fully accounted for. Do **one bounded preflight** per material network-state change. Permanent HTTP 451/403/404 are blocked routes — do NOT repeat exhaustively.
- **Parallelism:** Batch independent fetches/sweeps with deterministic ordering and bounded concurrency (semaphore). Zero cross-contamination between symbols/pairs. Persist each completed shard (checkpoint) so restarts skip verified work. Use dependency graph to parallelize independent workstreams.
- **Data Completeness:** If overlapping real history insufficient for window/TF → **EXCLUDE** with full rationale + attempt log. Never backfill/interpolate. Label BLOCKED/INSUFFICIENT_HISTORY with concrete evidence (gap counts, bar counts, first/last timestamps).
- **Determinism:** Fix seeds for ALL stochastic paths (bootstrap/MC/splits/selection). Log seeds + full config in artifacts with hashes where feasible.
- **Observability:** Per-pair/per-symbol/per-TF/per-split logging (bars, ranges, gaps, NaNs, duplicates). Structured logs to files + console. No silent passes/failures.
- **Scheduling:** Dependency-aware task graph. Do independent network-free work (tests/schema/analysis/bootstrap/risk/execution/validation) while data sources blocked. Profile hot paths, checkpoint shards, run affected tests after logical change, full gates after batch and at acceptance.
- **Regressions:** If lint/type/test break at any point → fix immediately. Do NOT proceed until green. Treat any new warnings as potential issues to resolve.

## INITIAL TASK MESSAGE FOR NEXT AGENTIC SESSION (TIMESTAMP: 2026-10-31T00:37:20Z)

**START NOW. DO NOT STOP EARLY. HEAVY WORK IS MANDATORY. COASTING IS UNACCEPTABLE.**

### PRIMARY OBJECTIVE
Aggressively scale and harden the real-data crypto stat arb system to be maximally un-coastable. Prove every inclusion with ironclad evidence, enforce rigorous multi-TF validation (>=12 splits), add deeper tail/bootstrap/stress analysis, harden execution realism under extreme cost stress, and emit a schema-enriched, fully auditable `portfolio_real` artifact with complete provenance. Every step must leave verifiable artifacts, tests, and logs.

### MANDATORY SEQUENCE (IN ORDER - NO SKIPPING)

#### 0. RESTORE & VERIFY GREEN (BLOCKING)
```bash
python -m ruff check backtest/ strategies/ utils/ tests/ && \
PYTHONPATH=. python -m pytest tests/ -q && \
python -m mypy backtest/ strategies/ utils/
```
Do not proceed until ALL pass (currently 529 passed, 1 skipped). Fix immediately if broken.

#### 1. BRUTAL AUDIT (MAP & ELIMINATE BOTTLENECKS)
Read and attack with intent to speed up without cutting corners:
- `examples/run_portfolio_real.py` (flow, risk, provenance, parallelization)
- `reports/portfolio_real.json` (current state, schema gaps)
- `tests/test_portfolio_real.py`, `tests/test_portfolio_real_hardened.py`, `tests/test_portfolio_risk_controls.py`
- `backtest/engine.py` (walk_forward_portfolio/run_portfolio), `backtest/sweep.py`
- `utils/portfolio_risk.py`, `utils/regime.py`, `utils/monte_carlo.py`, `utils/risk.py`
- `data/loader.py`, `strategies/pairs_trading.py`

Identify independent workstreams to parallelize. Remove serial waits, add checkpointing, fix paths that could mask missing real data. Log bottlenecks found + fixes applied.

#### 2. AGGRESSIVE REAL-ONLY UNIVERSE EXPANSION (PROVEN LIQUIDITY + OVERLAP)
Attempt expansion beyond current 11 symbols. Priority candidates with full rigor: **ARB, OP, NEAR, INJ, APT, SUI, TIA, SEI, BCH, ETC, MATIC/POL variants, ATOM, UNI, AAVE** and others ONLY if provably liquid with full overlap.

For EVERY candidate symbol/pair:
- Fetch real Binance spot history for required windows/TFs via `python -u` with retries, exponential backoff, full attempt logs (host/endpoint/status/latency_ms/errors/timestamps)
- Verify overlap, gap count, bar count, duplicates, NaNs/malformed data
- Only admit if passes cointegration/stability on full real window with complete provenance
- Update `PAIRS`/`SYMBOLS` in `examples/run_portfolio_real.py` with justification

Record EVERY inclusion/exclusion in `universe_changes` and `exclusions_with_rationale` with attempt counts, hosts/endpoints, and concrete reasons. **NEVER FABRICATE.** Target meaningful expansion while maintaining strict quality gates.

#### 3. MAXIMIZE MULTI-TIMEFRAME RIGOR (>=12 SPLITS, DEEPER ANALYSIS)
Enforce true rolling walk-forward on **1h, 4h, 1d** with >=12 splits each:
- Sensible train/test lengths per TF with documented rationale (no arbitrary inflation)
- Per-split IS/OOS, stability, degradation, regime-split, turnover/leverage
- Per-pair/per-TF/per-split breakdowns + aggregate
- Full provenance (params, windows, bar counts, seeds, data hashes)
- If splits < 12 for any TF with sufficient data → increase to >=12 with justification

Emit under `multi_timeframe_walk_forward` with complete per-split detail and summary statistics.

#### 4. DEEP STATISTICAL SIGNIFICANCE (BOOTSTRAP + ROBUSTNESS)
Bootstrap/shuffle Monte Carlo on real OOS portfolio returns:
- >= 3000 simulations (increase from baseline), fixed seeds (log all), fully reproducible
- 95% CIs for total return, Sharpe, max drawdown, CAGR, Calmar (portfolio + per-TF)
- Distinguishability from zero, p-values where meaningful
- Block bootstrap by regime/time where sensible
- Impact of transaction costs across bootstrap grid
- Network-independent execution with full config
- Attach under `bootstrap_ci_portfolio_oos` with full provenance

#### 5. VOLUME-AWARE EXECUTION REALISM + EXTREME COST-STRESS
- Fetch real Binance quote volume/turnover per symbol for full window (exhaustive attempts, log hosts/failures/endpoints). Omit only with full rationale after exhaustive attempts.
- Build/extend volume-aware slippage/participation model (document assumptions, market impact heuristics grounded in real data, never fabricate)
- Add broad **cost-stress grid** (fees × slippage × participation) integrated with provenance; test extreme tails
- Include execution diagnostics (turnover, capacity constraints, hit-rate sensitivity)
- Include under `volume_aware_execution` with full attempt logs

#### 6. TAILS, CORRELATIONS, REGIMES & CIRCUIT BREAKERS
- Enrich tail metrics (VaR/CVaR/CDaR) at multiple confidence levels with methodology
- Correlation matrix + rolling correlation stability (regime-aware)
- Regime-conditioned performance with clear regime definitions
- Strengthen circuit breaker coverage and log all trips/blocks with reasons
- Per-asset contribution, gross/net/leverage, concentration metrics
- Funding/basis provenance (full attempts/errors/hosts) — omit only after exhaustive attempts with rationale

#### 7. ARTIFACT ENRICHMENT (SCHEMA-COMPLETE, AUDITABLE)
Enrich `reports/portfolio_real.json` (update in-place if compatible). MUST include:
- `real_data_only: true`, `fabricated_data: false`
- Expanded universe with `universe_changes` and `exclusions_with_rationale` (full attempt logs)
- Per-TF IS/OOS per split + stability/degradation
- `multi_timeframe_walk_forward` with >=12 splits each
- `bootstrap_ci_portfolio_oos` with >=3000 sims, 95% CIs, seeds, config
- `volume_aware_execution` + full cost-stress grid + provenance
- Per-asset contribution, turnover, leverage/gross/net exposure, concentration
- Correlation matrix + rolling stability
- Tail metrics (VaR/CVaR/CDaR) + regime-conditioned performance
- Funding/basis provenance (or explicit omission rationale)
- Risk controls applied, circuit breaker results (with logs)
- All JSON-serializable, schema-validated by tests

#### 8. TESTS + DOCS HARDEN (IMPOSSIBLE TO COAST)
- Add network-independent stress tests: portfolio logic, risk controls, meta-selector, artifact schema, bootstrap CI, execution model, edge cases, data quality gates
- Strengthen assertions around `real_data_only`/`fabricated_data` and all required hardened fields
- Update `README.md` with hardened findings, concrete real-data numbers, explicit real-data-only provenance, coverage summary, reproduction commands
- Ensure new fields validated or explicitly tested; add negative tests for exclusion paths

#### 9. VERIFY & DELIVER (ZERO REGRESSIONS)
```bash
python -u examples/run_portfolio_real.py
PYTHONPATH=. python -m pytest tests/ -q  # >=529 passed, 0 new failures
python -m ruff check backtest/ strategies/ utils/ tests/  # clean
python -m mypy backtest/ strategies/ utils/  # clean
```
All deliverables present and valid. Do not commit unless explicitly requested.

## HARD CONSTRAINTS
- **REAL DATA ONLY** — No synthetic/fabricated data. Ever. Only isolated unit tests may use fabricated data with explicit `fabricated_data: true` warnings.
- **NO SHORTCUTS** — Omit+document if unavailable after exhaustive attempts with full provenance (hosts, endpoints, errors, counts, timestamps).
- **PRESERVE GREEN** — Zero regressions. Restore green before proceeding.
- **HEAVY MANDATE** — Complete the full campaign. Do not stop early.
- **BOTTLENECK REMOVAL** — Eliminate inefficiencies immediately (parallelize, retry, log, unbuffer, checkpoint shards, dependency graph).
- **IMPOSSIBLE TO COAST** — Structure work so future agents cannot avoid heavy validation; every step must produce checkable artifact/test/provenance.
- **UNBUFFERED OUTPUT** — Use `python -u` for all long-running real-data jobs. Add `flush=True` for critical logs.
- **REPRODUCIBILITY** — Seeds for stochastic parts; log all config. Deterministic ordering.
- **NO ALTERATION OF LIVE/PAPER BOUNDARIES** — Do not change trading boundaries or commit policy.

**CAMPAIGN COMPLETE ONLY WHEN ALL CRITERIA MET. START IMMEDIATELY.**
