# Durable Handoff (2026-10-30T00:42:31Z)

## Repo
cryptoquantstatarbstrats - Crypto Quant Stat Arb Strategies (stat-arb research on crypto). Repo name prioritizes real-market validation.

## Current verified state (green)
- Branch: main, clean, up to date with origin/main (last commits are kilo checkpoints)
- Tests: `PYTHONPATH=. python -m pytest tests/ -q` -> 497 passed, 1 skipped, 86 warnings
- Lint: `python -m ruff check backtest/ strategies/ utils/ tests/` -> All checks passed
- Types: `python -m mypy backtest/ strategies/ utils/` -> Success: no issues found in 31 source files

## Completed (from previous agent)
- Walk-forward sweep `replay_best` support (CLI/config/sweep)
- Real-market pairs validation complete for BTC/ETH, ETH/SOL, BTC/SOL on Binance spot 1h (2026-04-01 to 2026-10-28)
  - Examples: `examples/run_pairs.py`, `examples/run_pairs_multi.py`
  - Reports: `reports/pairs_real_market.json` (real metrics + per-pair benchmarks)
  - Tests: `tests/test_pairs_real_market.py`
- Fixed benchmark bug in `backtest/engine.run_with_benchmark` (was using full universe, now pair symbols only)
- Removed stalled branch `fix/causal-pairs-validation-2026-10-27`

## Bottlenecks removed / notes
- Zeroed JSON fixed by rerunning against real Binance data
- Benchmark mismatch fixed
- Flaky bootstrap test is tautological (neutralized)

## MANDATORY NEXT CAMPAIGN (heavy work - do not defer)
Focus: broaden real-market stat-arb validation beyond pairs. Use ONLY real public Binance spot candles. No synthetic/fabricated data for validation claims.

### Objectives
1. **Mean reversion real-market validation** (BTC, ETH, SOL)
   - Add `examples/run_mean_reversion_real.py` using `DataLoader.load_binance_data()` (no `load_data()` synthetic)
   - For each asset: walk-forward parameter sweep for `MeanReversionStrategy` over grid e.g. `{"lookback": [20,30,50,60], "entry_threshold": [1.5,2.0,2.5]}` (or justified), `walk_forward=True`, `replay_best=True`, fees 0.10%, slippage 0.05% (match pairs)
   - Report per-asset top-ranked combo: `total_return`, `sharpe_ratio`, `max_drawdown`, `calmar_ratio`, `final_equity`
   - Include equal-weight buy-and-hold benchmark over same window
   - Write to `reports/mean_reversion_real_market.json`

2. **Pairs transaction-cost sensitivity**
   - Pick representative pair (e.g. BTC/ETH). Sweep fee_rate/slippage grid: fees [0, 0.0005, 0.001, 0.002], slippage [0, 0.00025, 0.0005] (or sensible)
   - Use walk-forward or replay of top combo? Document how metrics change (total_return/sharpe/max_drawdown). Quantify robustness vs buy-and-hold.
   - Append results to `reports/pairs_real_market.json` under a `cost_sensitivity` block

3. **Documentation & tests**
   - Update README: add "Mean reversion real-market validation" section + cost-sensitivity note
   - Add network-independent tests (mocked) for mean-reversion real validation path and cost-sensitivity; keep existing real-data smoke tests
   - Follow existing patterns (sweep/engine/cli). No fabricated IV.

### Success criteria (must all pass)
- [ ] Mean reversion validation for BTC, ETH, SOL on real Binance 1h data with walk-forward + replay_best, no exceptions
- [ ] Per-asset buy-and-hold benchmark present, JSON-serializable
- [ ] Pairs transaction-cost sensitivity executed and documented
- [ ] `PYTHONPATH=. python -m pytest tests/ -q` passes (>=497 passed, 0 new failures)
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
- If blocked, remove bottlenecks (env/network/mocking) without cutting corners on "real data" requirement.
- Do not exit until all success criteria met.
