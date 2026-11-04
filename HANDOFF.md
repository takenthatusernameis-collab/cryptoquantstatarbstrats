# HANDOFF (SINGLE DURABLE HANDOFF)

TIMESTAMP: 2026-11-04T15:41:39Z
REPO: cryptoquantstatarbstrats
FOCUS: Crypto Quantitative Statistical Arbitrage Strategies

---

## INITIAL TASK MESSAGE (PASTE AS FIRST MESSAGE FOR NEXT AGENT)

```
You are picking up cryptoquantstatarbstrats. Do not plan in the abstract - do heavy working immediately.

OBJECTIVE: Unblock and complete an end-to-end crypto statistical arbitrage pipeline that can select pairs, test cointegration/spreads, generate signals, and run a reproducible backtest with transaction costs.

EXECUTE IN THIS ORDER (no skipping):
1. AUDIT BOTTLENECKS (parallel): Run `pytest -v` to see failures; scan `data/`, `strategies/`, `backtest/`, `utils/` for TODO/FIXME/NotImplemented and missing imports. Fix anything blocking imports/tests first.
2. MAKE IT RUNNABLE: Get at least one strategy from `strategies/` executing end-to-end against data in `data/` via `backtest/`. If data format is unclear, infer schema from loaders and fix adapters, not just docs.
3. VALIDATE CORE MATH: Ensure pair selection (cointegration), spread construction, z-score/threshold logic, and position sizing are implemented and unit-testable. Add/fix minimal tests if missing.
4. COSTS & REALISM: Wire transaction/slippage/capital constraints into backtest path. Produce a concrete backtest result (metrics) from real code paths.
5. DELIVER PROOF: Commit nothing unless asked, but leave the repo in a state where `pytest -v` passes for core tests or clearly document remaining failures with fixes applied. Update this handoff only if you remove a new blocker.

RULES:
- Prioritize unblocking execution over documentation. Write code to fix failures.
- If multiple sessions appear blocked, remove the bottleneck (imports, paths, deps, data adapters) before expanding scope.
- Do not stop at analysis. Make changes, run tests/backtests, iterate on failures until core path works.
- Focus strictly on stat arb on crypto (pairs/trading, spreads, cointegration) per repo name.
```

---

## KNOWN STATE
- README present (large) - treat as reference, not spec.
- Core dirs: `strategies/`, `backtest/`, `data/`, `utils/`, `tests/`, `scripts/`, `examples/`, `research_state/`
- Packaging: `pyproject.toml`, `requirements.txt`, egg-info present
- Tests exist under `tests/` (heavy working expected here)

## IMMEDIATE ACTIONS FOR NEXT AGENT
- [ ] `pytest -v` (capture failures)
- [ ] Trace imports from a strategy entrypoint through `backtest/` and `data/`
- [ ] Fix import/path/data adapter blockers first
- [ ] Get one full backtest run producing metrics
- [ ] Harden core stat-arb path (pairs/cointegration/spread/signals/costs)

## BOTTLENECK REMOVAL PRIORITY
1. **Import/dependency failures** - fix before anything else
2. **Data loading/schema mismatch** - adapt to actual files in `data/`
3. **Strategy/backtest integration** - wire end-to-end
4. **Tests** - make core tests pass or fix them

## SUCCESS CRITERION
Next agent has executed heavy work: modified code to fix blockers, ran tests/backtests, and produced a working end-to-end stat-arb backtest run with verifiable output/metrics. No "I'll look into it" without concrete code changes.
