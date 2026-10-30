# DURABLE HANDOFF (2026-10-30T19:33:02Z) — SINGLE MANDATORY NEXT TASK: CRYPTO QUANT STAT ARB MULTI-TIMEFRAME TRUE OOS + UNIVERSE SCALE-UP + RIGOR ENFORCEMENT

## REPO NAME IS THE LAW
- **REPO:** `cryptoquantstatarbstrats` — *Crypto Quant Stat Arb Strategies*
- **PRIORITY (BY NAME):** Crypto statistical arbitrage, real market microstructure, and falsifiability above all. If a change does not directly harden real-data stat arb validation/provenance/execution realism, it is waste.
- **ABSOLUTE MANDATE:** Research, build, harden, and relentlessly validate crypto statistical-arbitrage strategies using **ONLY REAL market data** (Binance public REST/klines/funding/basis where available). Never fabricate candles/IV/funding/basis.
- **COASTING IS FORBIDDEN.** Every session must produce measurable increases in real-data validation rigor (more splits, more pairs with proof, tighter CIs, better cost realism, stronger provenance).
- **HEAVY WORK ONLY.** Future agents cannot avoid doing heavy work — every step must produce checkable artifacts/tests/provenance.

## VERIFIED GREEN STATE (PRESERVE AT ALL COSTS)
- **Branch:** `main` (clean)
- **Tests:** `PYTHONPATH=. python -m pytest tests/ -q` → **527 passed, 1 skipped** (GREEN)
- **Types:** `python -m mypy backtest/ strategies/ utils/` → **Success: no issues found in 31 source files** (GREEN)
- **Lint:** `python -m ruff check backtest/ strategies/ utils/ tests/` → **All checks passed!** (GREEN)
- **Real data only:** `DataLoader.load_binance_data()` uses public Binance REST (network verified). Synthetic only for unit tests with explicit warnings.
- **Current baseline artifact:** `reports/portfolio_real.json` (real-only). Portfolio currently -4.54% total return, Sharpe -2.05, max DD -6.40% on 5108 hourly bars (2026-04-01 to 2026-10-30) across 10 pairs/6 symbols.

## BOTTLENECK ELIMINATION (DO FIRST, REMOVE ALL BLOCKERS)
**Treat these as mandatory fixes if they appear. Do not work around them.**

- **Unbuffered I/O:** Use `python -u` for ALL long real-data jobs (fetches, sweeps, walk-forward, portfolio rebuilds).
- **Progress & observability:** Add explicit per-pair/per-symbol/per-split logging (counts, ranges, host, failures). Print fetch progress and timing. No silent loops.
- **Parallelize safely:** Batch independent pair fetches/sweeps where deterministic and network-safe. Avoid cross-contaminating shared state.
- **Network resilience:** Retry with exponential backoff on public Binance endpoints. Log EVERY attempt/failure/host. Do not fail-fast without full attempt trail.
- **Data completeness:** If a candidate pair/symbol lacks sufficient overlapping real history for the requested window/TF, EXCLUDE with full rationale + attempt log (never backfill/fabricate).
- **Determinism:** Set seeds where stochastic (bootstrap/MC). All stochastic results must be reproducible and logged.
- **Zero regressions:** Fix any lint/type/test break IMMEDIATELY before moving forward.
- **No shortcut affordances:** If tempted to hardcode/synthesize/mask missing data, stop and document exhaustive attempts instead.

## INITIAL TASK MESSAGE FOR NEXT AGENTIC SESSION (TIMESTAMP: 2026-10-30T19:33:02Z)

**START IMMEDIATELY. DO NOT STOP EARLY. HEAVY WORK IS THE ONLY ACCEPTABLE OUTCOME.**

### PRIMARY OBJECTIVE
Aggressively expand the real-data universe, enforce **true multi-timeframe walk-forward rigor (>= 12 rolling splits per TF)**, add **bootstrap significance with 95% CIs**, implement **volume-aware execution realism + cost-stress grids**, and harden **ironclad provenance**. Make overfit substantially harder and impossible to coast. Every action must leave behind checkable artifacts/tests.

### MANDATORY SEQUENCE (IN ORDER, NO SKIPPING)

#### 0. UNBLOCK / RESTORE GREEN (BLOCKING)
```bash
python -m ruff check backtest/ strategies/ utils/ tests/ && \
PYTHONPATH=. python -m pytest tests/ -q && \
python -m mypy backtest/ strategies/ utils/
```
Do not proceed until ALL green. If not green, fix before anything else.

#### 1. BRUTALLY HONEST AUDIT (MAP BOTTLENECKS)
Read and audit:
- `examples/run_portfolio_real.py` (current flow, risk controls, provenance blocks)
- `reports/portfolio_real.json` (baseline)
- `tests/test_portfolio_real.py`, `tests/test_portfolio_risk_controls.py`
- `backtest/engine.py` (walk_forward_portfolio/run_portfolio)
- `utils/portfolio_risk.py`, `utils/regime.py`
- `data/loader.py`, `strategies/pairs_trading.py`
- `backtest/sweep.py`

Fix bottlenecks on contact. Eliminate any logic that could mask missing real data.

#### 2. UNIVERSE EXPANSION (REAL-ONLY, PROVEN)
Aggressively attempt: **BNB/USDT-quoted majors + DOT, MATIC, AVAX, LINK, LTC, BCH, ETC** (and others only if liquid with full overlap). For EVERY candidate:
- Fetch real Binance spot history for full requested window per TF as needed
- Verify overlap, bar count, data quality
- Only include if passes cointegration/stability on full real window with full provenance

Update `PAIRS`/`SYMBOLS` in `examples/run_portfolio_real.py`. Explicitly list **EVERY** inclusion/exclusion with rationale + attempt counts/hosts in `universe_changes` and `exclusions_with_rationale`. **Never fabricate.**

#### 3. MULTI-TIMEFRAME WALK-FORWARD RIGOR (>=12 SPLITS EACH)
Enforce true rolling walk-forward on **1h, 4h, 1d** with:
- >= 12 rolling splits per TF (increase from current if <12)
- Sensible train/test lengths per TF (adapt to bars; document choices)
- Per-split IS/OOS returns, stability, degradation, regime-split
- Aggregate stats + per-pair/per-TF breakdowns
- Full provenance (params, windows, counts)

Emit to artifact under `multi_timeframe_walk_forward` with complete per-split detail where feasible.

#### 4. STATISTICAL SIGNIFICANCE (BOOTSTRAP CI)
Bootstrap/shuffle Monte Carlo on **real OOS portfolio returns**:
- >= 2000 simulations, fixed seed, reproducible
- Report **95% CIs** for total return, Sharpe, max drawdown (per TF + portfolio)
- Test distinguishability from zero; state impact of transaction costs
- Network-independent; document method
- Attach under `bootstrap_ci_portfolio_oos` with full config

#### 5. VOLUME-AWARE EXECUTION REALISM + COST-STRESS
- Fetch real Binance quote volume per symbol for full window (exhaustive attempts, log hosts/failures)
- Build volume-aware slippage/participation model (document assumptions; no fabrication)
- Add broad **cost-stress grid** (fee × slippage × participation) integrated with provenance
- Include volume-aware grid in artifact under `volume_aware_execution`

#### 6. ARTIFACT ENRICHMENT (COMPREHENSIVE, SCHEMA-VALID)
Enrich `reports/portfolio_real.json` (or write `reports/portfolio_real_expanded.json` if schema drift, but prefer in-place update with backward compatibility). Must include:
- `real_data_only: true`, `fabricated_data: false`
- Per-TF IS/OOS per split + stability/degradation
- Bootstrap CI blocks (95% CIs) for return/Sharpe/maxDD
- Volume-aware execution + full cost-stress grid
- Per-asset contribution, turnover, leverage/gross/net exposure
- Correlation matrix + stability (rolling)
- Tail metrics (VaR/CVaR/CDaR)
- Regime-conditioned performance
- Funding/basis provenance (full attempts/errors/hosts) — omit only after exhaustive attempts with rationale
- Universe changes + exclusions with rationale + attempt logs
- Risk controls applied, circuit breaker results
- Multi-timeframe results with >=12 splits each
- JSON-serializable, tests still pass

#### 7. TESTS + DOCS HARDEN (MAKE IT IMPOSSIBLE TO COAST)
- Add network-independent stress tests for portfolio logic, risk controls, meta-selector, artifact schema, bootstrap CI, execution model, edge cases
- Update `README.md` with hardened findings, concrete real-data numbers, explicit real-data-only provenance, coverage summary
- Ensure new fields are validated or tests updated
- Strengthen assertions around real-data-only flags

#### 8. VERIFY & DELIVER (ZERO REGRESSIONS)
```bash
python -u examples/run_portfolio_real.py
PYTHONPATH=. python -m pytest tests/ -q  # >=527 passed, 0 new failures
python -m ruff check backtest/ strategies/ utils/ tests/  # clean
python -m mypy backtest/ strategies/ utils/  # clean
```
All deliverables present/valid. Commit only if explicitly requested.

### HARD CONSTRAINTS
- **REAL DATA ONLY** — No synthetic/fabricated data. Ever.
- **NO SHORTCUTS** — Omit+document if unavailable after exhaustive attempts with full provenance (hosts, errors, counts).
- **PRESERVE GREEN** — Zero regressions. Restore green before proceeding.
- **HEAVY MANDATE** — Complete full campaign. Do not stop early.
- **BOTTLENECK REMOVAL** — Eliminate inefficiencies immediately (parallelize, retry, log, unbuffer).
- **IMPOSSIBLE TO COAST** — Structure so future agents cannot avoid heavy validation; every step produces a checkable artifact/test/provenance.
- **UNBUFFERED OUTPUT** — Use `python -u` for all long-running real-data jobs.
- **REPRODUCIBILITY** — Seeds for stochastic parts; log all config.

**CAMPAIGN COMPLETE ONLY WHEN ALL CRITERIA MET. START IMMEDIATELY.**