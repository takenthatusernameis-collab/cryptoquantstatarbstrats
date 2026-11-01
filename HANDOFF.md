# SINGLE DURABLE HANDOFF | 2026-11-01T06:40:00Z | INITIAL TASK MESSAGE FOR NEXT AGENTIC WORK SESSION

## REPO IDENTITY (LAW) — PRIORITIZE BY REPO NAME
- Repo: `cryptoquantstatarbstrats` — **Crypto Quant Stat Arb Strategies**
- **CORE = COINTEGRATION / PAIRS TRADING.** Every other line of work serves cointegration rigor. Cointegration is law.
- Real data only: Binance public REST via `www.binance.com`. Never fabricate.
- Coasting = failure. Every action must produce checkable artifacts, tests, provenance, logs.

## CURRENT VERIFIED STATE (2026-11-01T06:40:00Z)
- Branch: `main`, working tree clean.
- `use_enriched_gates` default `True` (fail-closed) in `strategies/pairs_trading.py`. Enriched gates enforced strictly.
- Current `reports/portfolio_real.json` exists (643KB, Nov 1 02:12) with all 17 pairs marked `blocked_or_insufficient_data`. **All have non-empty `blocked_routes[]` with full provenance** - empty blocked_routes bottleneck appears resolved in current artifact.
- **POL/BTC**: passes EG (p<0.001), Johansen (rank>=1), leg stationarity, half-life bounds ok, spread mean reversion ok. Fails only **rolling_stability**: `frac_significant_0_05~0.049` (9/184 windows pass at p<0.05) out of 184 windows (window=720, step=24). Passing windows at indices ~7,64,65,114,119,120,121,147,182 - highly regime-dependent/sporadic.
- All other 16 pairs fail multiple gates.
- **REGENERATION IN PROGRESS**: `examples/run_portfolio_real.py` running in background (slow due to full portfolio construction, walk-forward, bootstrap 3000 sims, multi-timeframe). May take long time.

## BOTTLENECKS IDENTIFIED & REMOVAL PLAN
1. **Slow regeneration** - Full `run_portfolio_real.py` does expensive operations (bootstrap 3000x, multi-timeframe 1h/4h/1d, walk-forward across all pairs). 
   - **ACTION**: Either wait for completion, or create a faster regen script that focuses on cointegration diagnostics/artifact update without full portfolio optimization/bootstrap if not strictly needed. But must preserve schema.
2. **POL/BTC rolling stability** - Only pair close to passing. Needs regime analysis.
3. **All other pairs blocked** - Need systematic diagnosis; honest blocking preferred over weakening gates.

## IMMEDIATE INITIAL TASK (START HERE — NO DEVIATION)
**OBJECTIVE:** Close cointegration rigor loop. For every pair: pass ALL enriched gates on real data OR be honestly blocked with full provenance. No threshold weakening without ironclad evidence+tests. No fabrication.

**MANDATORY FIRST ACTIONS (IN ORDER):**
1. **Check regen status** - If still running, decide: wait or optimize. Check logs: `tail -30 reports/portfolio_real_regen.log`. If taking too long and blocking progress, consider interrupting and doing targeted updates.
2. **Deep dive POL/BTC regime-dependence** (highest ROI). Analyze passing windows' characteristics - market regime, vol, hedge ratio stability, structural breaks. Determine if regime-filterable (trailing-only, no lookahead).
3. **If regime-filterable**: Design causal regime filter, add to strategy with tests. Verify it only allows trading in passing regimes. Must be trailing-only.
4. **If not regime-filterable/fundamentally unstable**: Keep blocked with full provenance (rationale must explain why). Do NOT weaken rolling_stability threshold.
5. **Sweep remaining 16 pairs** - Quick diagnosis; honest blocking is correct if gates fail.
6. **Verify**: Run tests (`pytest tests/ -q` >=555 passed, 0 failures), ruff clean, schema tests pass.

## FOCUS AREAS (HEAVY WORK REQUIRED)
### POL/BTC Deep Dive
- Files: `strategies/pairs_trading.py`, `utils/cointegration.py`, `data/loader.py`
- Analyze: hedge ratio stability in passing vs failing windows, volatility regimes, correlation structure, ADF/KPSS of spread per regime
- Passing windows: start bars 168,1536,1560,2736,2856,2880,2904,3528,4368 (720-bar windows, step 24)
- Question: Is cointegration regime-dependent (tradeable in specific regimes with causal filter) or temporally unstable (fundamentally unfit)?

### Regime Filter Design (if viable)
- Must be **trailing-only, no lookahead** - use only past data
- Must be **causal** - no future information
- Must have tests proving no lookahead
- Must integrate cleanly with enriched gates (or as additional gate)
- Example approaches: volatility regime, trend regime, correlation regime, hedge ratio stability - all computed from trailing windows only

### Bottleneck Removal
- If regen blocks iteration: optimize `examples/run_portfolio_real.py` (reduce bootstrap sims for testing, skip expensive parts, use checkpointing better) or write fast targeted regen script
- Parallelize where possible
- Cache expensive computations

## HARD CONSTRAINTS
- **REAL DATA ONLY** — no fabrication
- **NO WEAKENING THRESHOLDS** without ironclad justification + tests
- **PRESERVE GREEN** — >=555 passed, 0 failures
- **CAUSAL ONLY** — no lookahead
- **HONEST BLOCKING** — if cannot pass all gates, mark `blocked_or_insufficient_data` with full provenance, non-empty `blocked_routes`
- **HEAVY MANDATE** — no coasting, do the work

## VERIFICATION COMMANDS
```bash
python -m ruff check backtest/ strategies/ utils/ tests/ examples/
python -m pytest tests/test_cointegration_diagnostics_schema.py tests/test_strategies.py -v
python -m pytest tests/ -q  # >=555 passed, 0 failures
```

**START NOW.** Focus on POL/BTC regime analysis first. If regen is blocking, remove that bottleneck.
