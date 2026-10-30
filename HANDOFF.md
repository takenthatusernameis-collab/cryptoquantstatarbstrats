# Durable Handoff (2026-10-30T04:52:48Z)

## Repo
cryptoquantstatarbstrats - Crypto Quant Stat Arb Strategies (stat-arb research on crypto). Repo name prioritizes real-market validation on real public Binance spot candles. No API key required; no fabricated data for validation.

## Current verified state (green)
- Branch: main, clean, up to date with origin/main
- Tests: `PYTHONPATH=. python -m pytest tests/ -q` -> 505 passed, 1 skipped, 86 warnings
- Lint: `python -m ruff check backtest/ strategies/ utils/ tests/` -> All checks passed
- Types: `python -m mypy backtest/ strategies/ utils/` -> Success: no issues found in 31 source files
- Dev deps: install with `python -m pip install -e ".[dev]"` before running verification locally

## Completed (from previous agents)
- Walk-forward sweep `replay_best` support (CLI/config/sweep)
- Real-market pairs validation complete for BTC/ETH, ETH/SOL, BTC/SOL on Binance spot 1h (2026-04-01 to 2026-10-28)
- Mean reversion real-market validation complete for BTC, ETH, SOL (same window) via `examples/run_mean_reversion_real.py`
- Pairs transaction-cost sensitivity sweep added to `reports/pairs_real_market.json` (BTC/ETH, fees × slippage grid)
- Fixed benchmark bug in `backtest/engine.run_with_benchmark` (pair symbols only)
- README updated with Real-market validation (pairs + mean reversion) and cost-sensitivity notes
- Expanded pairs artifact: `reports/pairs_real_market_expanded.json` (JSON-serializable)
- Regime robustness artifact: `reports/regime_robustness_real.json` (JSON-serializable)
- Execution realism beyond BTC/ETH: `reports/cost_sensitivity_real.json` exists with ETH/SOL pair fee × slippage grid (JSON-serializable), produced by `examples/run_cost_sensitivity_real.py`
- Mean reversion SOL cost-sensitivity: `reports/cost_sensitivity_real_mean_reversion.json` with fee × slippage grid, degradation vs base (JSON-serializable)
- Portfolio pairs cost-sensitivity: `reports/cost_sensitivity_real_portfolio.json` (JSON-serializable) aggregating top-ranked combos across BTC/ETH, ETH/SOL, BTC/SOL; tested by `tests/test_cost_sensitivity_real_portfolio.py`
- Extended regime/cost-stress slices present in `reports/regime_robustness_real.json`; tested by `tests/test_regime_robustness_real_extended.py`
- Bottlenecks removed (stalled branch deleted; env/module issues fixed)

## MANDATORY NEXT CAMPAIGN (heavy work - do not defer)
Focus: end-to-end real-data paper-trading simulation with execution realism and Monte Carlo robustness on real Binance spot candles (no fabricated candles), harden robustness reporting, and close any remaining gaps without regressing green tests.

### Objectives
1. **Real-data paper trading**
   - Run the paper-trading pipeline on real Binance spot 1h candles (BTC/ETH, ETH/SOL, BTC/SOL, 2026-04-01 to 2026-10-28) using `DataLoader.load_binance_data()`, feeding the top-ranked pairs combos.
   - Produce a JSON-serializable artifact in `reports/` (e.g. `reports/paper_trading_real.json`) with equity curve summary, fills, slippage, fees, and drawdown.
2. **Execution realism**
   - Extend VWAP/TWAP/LOB execution models to the real-data paper-trading run; quantify impact vs naive fills.
   - Produce a JSON-serializable artifact (e.g. `reports/execution_realism_real.json`).
3. **Monte Carlo robustness**
   - Run Monte Carlo resampling on real-data returns; report confidence intervals for total return, Sharpe, max drawdown.
   - Produce a JSON-serializable artifact (e.g. `reports/monte_carlo_real.json`).
4. **Tests & docs**
   - Add network-independent tests validating new artifacts (existence, JSON-serializable, required schema keys) mirroring existing test patterns.
   - Update README with new findings/artifacts.
   - Keep all verification green.

### Success criteria (must all pass)
- [ ] Real-data paper-trading artifact in `reports/` (JSON-serializable)
- [ ] Real-data execution-realism artifact in `reports/` (JSON-serializable)
- [ ] Real-data Monte Carlo artifact in `reports/` (JSON-serializable)
- [ ] README documents new findings/artifacts
- [ ] New network-independent tests for new artifacts pass
- [ ] `PYTHONPATH=. python -m pytest tests/ -q` passes (>=505 passed, 0 new failures)
- [ ] `python -m ruff check backtest/ strategies/ utils/ tests/` clean
- [ ] `python -m mypy backtest/ strategies/ utils/` clean

### Commands to verify
```bash
PYTHONPATH=. python -m pytest tests/ -q
python -m ruff check backtest/ strategies/ utils/ tests/
python -m mypy backtest/ strategies/ utils/
```

### Notes
- This repo's core is crypto stat-arb validation on real data. Prioritize heavy validation work.
- Follow existing patterns (CLI/config/sweep/engine/DataLoader). No fabricated IV/candles.
- If blocked, remove bottlenecks (env/network/mocking) without cutting corners on "real data" requirement.
- Do not exit until all success criteria met.

## INITIAL TASK MESSAGE FOR NEXT AGENTIC WORK SESSION (2026-10-30T04:52:48Z)

**REPO:** cryptoquantstatarbstrats (Crypto Quant Stat Arb Strategies)
**PRIORITIZATION:** Per repo name, core mission is crypto statistical-arbitrage validation on REAL market data (public Binance spot candles, no API key, no fabricated data). Current state is GREEN (505 passed, 1 skipped; ruff/mypy clean). All prior campaigns complete: pairs+mean reversion on real Binance 1h (2026-04-01 to 2026-10-28), expanded pairs, regime robustness, ETH/SOL pairs cost-sensitivity, SOL mean reversion cost-sensitivity, portfolio pairs cost-sensitivity, extended regime/cost-stress slices all present and tested.

**MANDATORY HEAVY WORK (do not defer):** Extend execution realism to end-to-end real-data paper trading, execution-cost realism, and Monte Carlo robustness on real Binance spot data. Remove bottlenecks immediately. No fabricated data. Do heavy validation.

### OBJECTIVE
1. Run real-data paper-trading pipeline on real Binance spot 1h candles (BTC/ETH, ETH/SOL, BTC/SOL, 2026-04-01 to 2026-10-28) feeding top-ranked pairs combos; produce `reports/paper_trading_real.json` (JSON-serializable) with equity curve summary, fills, slippage, fees, drawdown.
2. Extend VWAP/TWAP/LOB execution models to the real-data paper-trading run; quantify impact vs naive fills; produce `reports/execution_realism_real.json` (JSON-serializable).
3. Run Monte Carlo resampling on real-data returns; report confidence intervals for total return, Sharpe, max drawdown; produce `reports/monte_carlo_real.json` (JSON-serializable).
4. Document findings in README and add network-independent tests mirroring existing patterns.
5. Verify everything stays green.

### REQUIRED ACTIONS (execute in order; do not skip)
1. **Paper trading:** Produce `reports/paper_trading_real.json` (JSON-serializable) using real data only.
2. **Execution realism:** Produce `reports/execution_realism_real.json` (JSON-serializable) with VWAP/TWAP/LOB impact vs naive.
3. **Monte Carlo:** Produce `reports/monte_carlo_real.json` (JSON-serializable) with confidence intervals.
4. **Docs:** Update README to document new findings/artifacts.
5. **Tests:** Add network-independent tests for new artifacts (existence, JSON-serializable, required keys).
6. **Verify:** Run full test/lint/typecheck and fix any issues without reverting green main.

### SUCCESS CRITERIA (all must hold; none optional)
- [ ] Real-data paper-trading artifact in `reports/` (JSON-serializable)
- [ ] Real-data execution-realism artifact in `reports/` (JSON-serializable)
- [ ] Real-data Monte Carlo artifact in `reports/` (JSON-serializable)
- [ ] README documents new findings/artifacts
- [ ] New network-independent tests for new artifacts pass
- [ ] `PYTHONPATH=. python -m pytest tests/ -q` passes (>=505 passed, 0 new failures)
- [ ] `python -m ruff check backtest/ strategies/ utils/ tests/` clean
- [ ] `python -m mypy backtest/ strategies/ utils/` clean

### VERIFICATION
```bash
PYTHONPATH=. python -m pytest tests/ -q
python -m ruff check backtest/ strategies/ utils/ tests/
python -m mypy backtest/ strategies/ utils/
```

### CONSTRAINTS / NOTES
- Follow existing patterns (CLI/config/sweep/engine/DataLoader). No fabricated IV/candles.
- Keep changes minimal and consistent with codebase style.
- If tests hang/fail due to env, fix or isolate; do not revert green main.
- Document any new files/changes clearly.
- Do not exit until all success criteria met.
