# HANDOFF (SINGLE DURABLE HANDOFF)

TIMESTAMP: 2026-11-04T15:47:51Z
REPO: cryptoquantstatarbstrats
FOCUS: Crypto Quantitative Statistical Arbitrage Strategies

---

## INITIAL TASK MESSAGE (PASTE AS FIRST MESSAGE FOR NEXT AGENT)

```
You are picking up cryptoquantstatarbstrats. NO "investigate only" loops. DO HEAVY WORKING IMMEDIATELY.

OBJECTIVE: Unblock and deliver a working end-to-end crypto pairs statistical arbitrage pipeline (pair selection -> cointegration/spread construction -> z-score signals -> realistic backtest with costs) that produces concrete metrics from real code paths.

EXECUTE IN THIS EXACT ORDER (remove blockers, do not skip):

1. AUDIT & UNBLOCK IMPORTS (HARD BLOCKER)
   - Run `pip show pytest numpy pandas scipy statsmodels` and `pip list | head -60`.
   - Run `pytest -v 2>&1 | tail -120` and capture every ImportError/ModuleNotFoundError.
   - Fix deps/path issues using `requirements.txt`/`pyproject.toml`. Install missing deps or fix imports/relative paths. Do this before expanding scope.

2. MAP THE REAL DATA (BLOCKER)
   - Inspect `data/` for actual files and schema. Read any loaders/adapters in `data/` and `utils/`.
   - Trace how data flows into strategies/backtest. Fix adapters to match actual files - do not guess from README alone.

3. WIRE ONE STRATEGY END-TO-END (CORE)
   - Find the simplest viable strategy in `strategies/`. Trace its full call chain through `backtest/` to a runnable entrypoint (test, script, or example).
   - Make it execute against real data. Fix integration gaps (imports, class/function mismatches, missing args) until it runs.

4. HARDEN STAT-ARB MATH (CORE)
   - Ensure pair selection/cointegration (e.g. Engle-Granger), spread construction, z-score/thresholds, and position sizing are actually used.
   - If missing/incomplete, implement minimal correct glue. Add/fix tiny unit tests only if they unblock the core path.

5. ADD REALISM & PRODUCE PROOF (REQUIRED)
   - Wire transaction costs/slippage/capital constraints into the backtest path if absent.
   - Run the end-to-end backtest and output concrete metrics (trades, PnL, cumulative/period returns, Sharpe/vol or drawdown if available).
   - Run `pytest -v`. Fix failures blocking the core stat-arb path. Leave the repo in a runnable state.

RULES:
- Prioritize unblocking execution over documentation. Write code to fix failures.
- If multiple things appear blocked, fix the bottleneck first (imports -> data -> integration -> tests).
- Do not stop at "investigation". Make changes, run tests/backtests, iterate on failures.
- Stay laser-focused on pairs/trading spreads/cointegration per repo name (crypto stat arb).
- Commit nothing unless explicitly asked. Update THIS handoff only if you remove a NEW hard blocker not listed here.
- Success = modified code + a working end-to-end stat-arb backtest run with verifiable output/metrics.
```

---

## KNOWN STATE
- `README.md` present (reference only)
- Core dirs: `strategies/`, `backtest/`, `data/`, `utils/`, `tests/`, `scripts/`, `examples/`, `research_state/`
- Packaging: `pyproject.toml`, `requirements.txt`, `cryptoquantstatarbstrats.egg-info/` present
- Tests exist under `tests/` (heavy working expected)

## IMMEDIATE ACTIONS FOR NEXT AGENT
- [ ] `pytest -v` (capture full failures with tracebacks)
- [ ] `pip list` / check deps vs imports
- [ ] `ls -la data/` and read loaders in `data/`
- [ ] Find strategy entrypoints: `grep -rn "cointegrat\|pairs_trading\|zscore\|spread" strategies/ backtest/ | head -40`
- [ ] Trace one full path from strategy -> backtest -> data and make it runnable
- [ ] Run one concrete backtest producing metrics

## BOTTLENECK REMOVAL PRIORITY
1. **Imports/dependencies** - fix first (no code runs otherwise)
2. **Data loading/schema mismatch** - adapt to actual files in `data/`
3. **Strategy/backtest integration** - wire end-to-end
4. **Stat-arb core logic gaps** (cointegration/spread/signals) - only after 1-3
5. **Tests/costs/realism** - harden once core runs

## SUCCESS CRITERION
Next agent has executed heavy work: modified code to remove blockers, ran tests/backtests iteratively, and produced a working end-to-end crypto pairs stat-arb backtest run with concrete, verifiable metrics from real code paths.
