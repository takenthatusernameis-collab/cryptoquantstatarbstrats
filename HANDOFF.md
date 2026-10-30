# DURABLE HANDOFF (2026-10-30T22:35:29Z) — SINGLE MANDATORY NEXT TASK: CRYPTO STAT ARB SCALE-UP (UN-COASTABLE, HEAVY EXECUTION)

## REPO IDENTITY (LAW)
- **REPO:** `cryptoquantstatarbstrats` — *Crypto Quant Stat Arb Strategies*
- **PRIORITY:** Pure real-data crypto statistical arbitrage. Market microstructure, pair stability, and falsifiability take absolute precedence.
- **MANDATE:** **ONLY REAL market data** (Binance public REST). Never fabricate candles, funding, basis, IV, volume, or returns. Synthetic data is strictly limited to isolated unit tests with explicit `fabricated_data: true` warnings.
- **COASTING = FAILURE.** Every action must produce checkable artifacts, tests, provenance, and logs. Future agents cannot avoid heavy validation.

## VERIFIED GREEN STATE (PRESERVE AT ALL COSTS)
- **Branch:** `main` (clean)
- **Tests:** `PYTHONPATH=. python -m pytest tests/ -q` → **528 passed, 1 skipped** (GREEN)
- **Types:** `python -m mypy backtest/ strategies/ utils/` → **Success: no issues found in 31 source files** (GREEN)
- **Lint:** `python -m ruff check backtest/ strategies/ utils/ tests/` → **All checks passed!** (GREEN)
- **Baseline:** `reports/portfolio_real.json` (real-only). Expanded universe with hardened risk controls, multi-TF walk-forward (≥12 splits), bootstrap CIs, volume-aware execution, full provenance.

## BOTTLENECKS TO ELIMINATE (DO FIRST - REMOVE ALL FRICTION)
These block scale and must be killed immediately:

- **I/O:** Run all long jobs with `python -u`. Add `flush=True` for critical logs. Never buffer indefinitely.
- **Network:** Exponential backoff + retries on ALL Binance calls. Log every attempt (host, endpoint, status, latency_ms). Treat partial pages as failures unless fully accounted for. Do **one bounded preflight** per material network-state change. Permanent HTTP 451/403/404 are blocked routes - do NOT repeat exhaustively.
- **Parallelism:** Batch independent fetches/sweeps with deterministic ordering and bounded concurrency. Zero cross-contamination between symbols/pairs. Persist each completed shard so restarts skip verified work.
- **Data Completeness:** If overlapping real history insufficient for window/TF → **EXCLUDE** with full rationale + attempt log. Never backfill/interpolate. Label BLOCKED/INSUFFICIENT_HISTORY with concrete evidence.
- **Determinism:** Fix seeds for ALL stochastic paths (bootstrap/MC/splits). Log seeds + full config in artifacts.
- **Observability:** Per-pair/per-symbol/per-TF/per-split logging (bars, ranges, gaps, NaNs). No silent passes/failures.
- **Scheduling:** Dependency-aware task graph. Do independent network-free work (tests/schema/analysis/bootstrap/risk/execution) while data sources blocked. Profile, checkpoint, run affected tests after logical change, full gates after batch and at acceptance.
- **Regressions:** If lint/type/test break at any point → fix immediately. Do NOT proceed until green.

## INITIAL TASK MESSAGE FOR NEXT AGENTIC SESSION (TIMESTAMP: 2026-10-30T22:35:29Z)

**START NOW. DO NOT STOP EARLY. HEAVY WORK IS MANDATORY. COASTING IS UNACCEPTABLE.**

### PRIMARY OBJECTIVE
Make the real-data crypto stat arb system maximally un-coastable and aggressively scalable. Prove every inclusion with ironclad evidence, enforce rigorous multi-TF validation, add deeper tail/bootstrap analysis, harden execution realism under extreme cost stress, and emit a schema-enriched, fully auditable `portfolio_real` artifact with complete provenance. Every step must leave verifiable artifacts and tests.

### MANDATORY SEQUENCE (IN ORDER - NO SKIPPING)

#### 0. RESTORE & VERIFY GREEN (BLOCKING)
```bash
python -m ruff check backtest/ strategies/ utils/ tests/ && \
PYTHONPATH=. python -m pytest tests/ -q && \
python -m mypy backtest/ strategies/ utils/
```
Do not proceed until ALL pass. Fix immediately if broken.

#### 1. BRUTAL AUDIT (MAP & ELIMINATE BOTTLENECKS)
Read and attack these with intent to speed up without cutting corners:
- `examples/run_portfolio_real.py` (flow, risk, provenance)
- `reports/portfolio_real.json` (current state)
- `tests/test_portfolio_real.py`, `tests/test_portfolio_real_hardened.py`, `tests/test_portfolio_risk_controls.py`
- `backtest/engine.py` (walk_forward_portfolio/run_portfolio)
- `utils/portfolio_risk.py`, `utils/regime.py`, `utils/monte_carlo.py`, `utils/risk.py`
- `data/loader.py`, `strategies/pairs_trading.py`, `backtest/sweep.py`

Identify independent workstreams to parallelize. Remove serial waits. Fix any paths that could mask missing real data.

#### 2. AGGRESSIVE REAL-ONLY UNIVERSE EXPANSION (PROVEN LIQUIDITY + OVERLAP)
Attempt expansion beyond current set. Candidates to test with full rigor: **MATIC/POL variants, AVAX, LINK, LTC, BCH, ETC, NEAR, ARB, OP, INJ, APT, SUI, TIA, SEI** and others ONLY if provably liquid with full overlap on required windows/TFs.

For EVERY candidate:
- Fetch real Binance spot history for required windows/TFs via `python -u` with retries, exponential backoff, full attempt logs (host/endpoint/status/latency_ms/errors)
- Verify overlap, gap count, bar count, data quality (no NaNs/malformed)
- Only admit if passes cointegration/stability on full real window with complete provenance
- Update `PAIRS`/`SYMBOLS` in `examples/run_portfolio_real.py`

Record EVERY inclusion/exclusion in `universe_changes` and `exclusions_with_rationale` with attempt counts, hosts, and concrete reasons. **NEVER FABRICATE.**

#### 3. MAXIMIZE MULTI-TIMEFRAME RIGOR (>=12 SPLITS, DEEPER ANALYSIS)
Enforce true rolling walk-forward on **1h, 4h, 1d** with >=12 splits each:
- Sensible train/test lengths per TF with documented rationale
- Per-split IS/OOS, stability, degradation, regime-split
- Per-pair/per-TF breakdowns + aggregate
- Full provenance (params, windows, bar counts, seeds)

Emit under `multi_timeframe_walk_forward` with complete per-split detail. If splits < 12 for any TF with sufficient data → increase to >=12.

#### 4. DEEP STATISTICAL SIGNIFICANCE (BOOTSTRAP + ROBUSTNESS)
Bootstrap/shuffle Monte Carlo on real OOS portfolio returns:
- >= 2000 simulations, fixed seeds (log all), reproducible
- 95% CIs for total return, Sharpe, max drawdown (portfolio + per-TF)
- Distinguishability from zero, p-values where meaningful
- Impact of transaction costs across bootstrap
- Network-independent execution
- Attach under `bootstrap_ci_portfolio_oos` with full config

#### 5. VOLUME-AWARE EXECUTION REALISM + EXTREME COST-STRESS
- Fetch real Binance quote volume per symbol for full window (exhaustive attempts, log hosts/failures). Omit only with full rationale after exhaustive attempts.
- Build volume-aware slippage/participation model (document assumptions, never fabricate)
- Add broad **cost-stress grid** (fees × slippage × participation) integrated with provenance
- Test extreme tails (wider fee/slippage ranges)
- Include under `volume_aware_execution`

#### 6. ARTIFACT ENRICHMENT (SCHEMA-COMPLETE, AUDITABLE)
Enrich `reports/portfolio_real.json` (update in-place if compatible). MUST include:
- `real_data_only: true`, `fabricated_data: false`
- Per-TF IS/OOS per split + stability/degradation
- Bootstrap CI blocks (95% CIs) for return/Sharpe/maxDD (portfolio + per-TF)
- Volume-aware execution + full cost-stress grid
- Per-asset contribution, turnover, leverage/gross/net exposure
- Correlation matrix + rolling stability
- Tail metrics (VaR/CVaR/CDaR)
- Regime-conditioned performance
- Funding/basis provenance (full attempts/errors/hosts) — omit only after exhaustive attempts with rationale
- Universe changes + exclusions with rationale + attempt logs
- Risk controls applied, circuit breaker results
- Multi-timeframe results with >=12 splits each
- All JSON-serializable, validated by tests

#### 7. TESTS + DOCS HARDEN (IMPOSSIBLE TO COAST)
- Add network-independent stress tests: portfolio logic, risk controls, meta-selector, artifact schema, bootstrap CI, execution model, edge cases
- Strengthen assertions around `real_data_only`/`fabricated_data` and required hardened fields
- Update `README.md` with hardened findings, concrete real-data numbers, explicit real-data-only provenance, coverage summary
- Ensure new fields validated or explicitly tested

#### 8. VERIFY & DELIVER (ZERO REGRESSIONS)
```bash
python -u examples/run_portfolio_real.py
PYTHONPATH=. python -m pytest tests/ -q  # >=528 passed, 0 new failures
python -m ruff check backtest/ strategies/ utils/ tests/  # clean
python -m mypy backtest/ strategies/ utils/  # clean
```
All deliverables present and valid. Commit only if explicitly requested.

## HARD CONSTRAINTS
- **REAL DATA ONLY** — No synthetic/fabricated data. Ever.
- **NO SHORTCUTS** — Omit+document if unavailable after exhaustive attempts with full provenance (hosts, endpoints, errors, counts).
- **PRESERVE GREEN** — Zero regressions. Restore green before proceeding.
- **HEAVY MANDATE** — Complete the full campaign. Do not stop early.
- **BOTTLENECK REMOVAL** — Eliminate inefficiencies immediately (parallelize, retry, log, unbuffer, checkpoint shards).
- **IMPOSSIBLE TO COAST** — Structure work so future agents cannot avoid heavy validation; every step must produce checkable artifact/test/provenance.
- **UNBUFFERED OUTPUT** — Use `python -u` for all long-running real-data jobs.
- **REPRODUCIBILITY** — Seeds for stochastic parts; log all config.
- **NO ALTERATION OF LIVE/PAPER BOUNDARIES** — Do not change trading boundaries or commit policy.

**CAMPAIGN COMPLETE ONLY WHEN ALL CRITERIA MET. START IMMEDIATELY.**
