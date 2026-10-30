# Durable Handoff (2026-10-30T03:40:51Z)

## Repo
cryptoquantstatarbstrats - Crypto Quant Stat Arb Strategies (stat-arb research on crypto). Repo name prioritizes real-market validation on real public Binance spot candles. No API key required; no fabricated data for validation.

## Current verified state (green)
- Branch: main, clean, up to date with origin/main
- Tests: `PYTHONPATH=. python -m pytest tests/ -q` -> 503 passed, 1 skipped, 86 warnings
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
- Bottlenecks removed (stalled branch deleted; env/module issues fixed)

## MANDATORY NEXT CAMPAIGN (heavy work - do not defer)
Focus: extend execution realism to a multi-asset portfolio setting on real Binance spot data (no fabricated candles), harden robustness reporting, and close any remaining gaps without regressing green tests.

### Objectives
1. **Portfolio cost-sensitivity (pairs)**
   - Extend transaction-cost sensitivity to a portfolio of pairs using real Binance spot 1h candles (BTC/ETH, ETH/SOL, BTC/SOL) over 2026-04-01 to 2026-10-28.
   - Model fee × slippage grids per pair and/or portfolio-level; quantify degradation vs base (zero-cost/current) across realistic cost regimes.
   - Produce a JSON-serializable artifact in `reports/` (e.g. `reports/cost_sensitivity_real_portfolio.json`) following existing patterns.
2. **Robustness under regime/cost stress**
   - Build on `reports/regime_robustness_real.json` to add explicit cost-stress slices for both pairs and mean reversion where feasible (or extend that artifact) with JSON-serializable outputs.
   - Document findings in README with concrete numbers.
3. **Tests & docs**
   - Add network-independent tests validating any new artifacts (existence, JSON-serializable, required schema keys) mirroring existing test patterns.
   - Update README with new findings/artifacts.
   - Keep all verification green.

### Success criteria (must all pass)
- [ ] Portfolio pairs cost-sensitivity artifact in `reports/` (JSON-serializable) with fee × slippage grids for relevant pairs/portfolio
- [ ] README documents portfolio/extended cost-stress findings
- [ ] New network-independent tests for new artifacts pass
- [ ] `PYTHONPATH=. python -m pytest tests/ -q` passes (>=503 passed, 0 new failures)
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

## INITIAL TASK MESSAGE FOR NEXT AGENTIC WORK SESSION (2026-10-30T03:40:51Z)

**REPO:** cryptoquantstatarbstrats (Crypto Quant Stat Arb Strategies)
**PRIORITIZATION:** Per repo name, core mission is crypto statistical-arbitrage validation on REAL market data (public Binance spot candles, no API key, no fabricated data). Current state is GREEN (503 passed, 1 skipped; ruff/mypy clean). All prior campaigns complete: pairs+mean reversion on real Binance 1h (2026-04-01 to 2026-10-28), expanded pairs, regime robustness, ETH/SOL pairs cost-sensitivity, and SOL mean reversion cost-sensitivity all present and tested.

**MANDATORY HEAVY WORK (do not defer):** Extend execution realism to a multi-asset portfolio setting on real Binance spot data. Remove bottlenecks immediately. No fabricated data. Do heavy validation.

### OBJECTIVE
1. Add portfolio-level transaction-cost sensitivity for pairs across BTC/ETH, ETH/SOL, BTC/SOL using `DataLoader.load_binance_data()` (real public Binance spot 1h, 2026-04-01 to 2026-10-28). Model fee × slippage grids; quantify degradation vs base (zero-cost/current) replay at portfolio level.
2. Extend robustness reporting (build on `reports/regime_robustness_real.json`) with cost-stress slices where feasible; keep outputs JSON-serializable.
3. Document findings in README and add network-independent tests mirroring existing patterns.
4. Verify everything stays green.

### REQUIRED ACTIONS (execute in order; do not skip)
1. **Portfolio cost-sensitivity:** Create/extend to produce `reports/cost_sensitivity_real_portfolio.json` (JSON-serializable) with portfolio-level metrics under fee × slippage grids using real data only.
2. **Robustness extension:** Add cost-stress slices to robustness reporting (update `reports/regime_robustness_real.json` or add a complementary JSON-serializable artifact) with clear schema.
3. **Docs:** Update README to document portfolio cost-sensitivity and any new robustness findings.
4. **Tests:** Add network-independent tests for new artifacts (existence, JSON-serializable, required keys).
5. **Verify:** Run full test/lint/typecheck and fix any issues without reverting green main.

### SUCCESS CRITERIA (all must hold; none optional)
- [ ] Portfolio pairs cost-sensitivity artifact in `reports/` (JSON-serializable) with fee × slippage grids
- [ ] README documents portfolio/extended cost-stress findings
- [ ] New network-independent tests for new artifacts pass
- [ ] `PYTHONPATH=. python -m pytest tests/ -q` passes (>=503 passed, 0 new failures)
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
