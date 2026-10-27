# Task for Next Agent

## Status
Walk-forward portfolio reoptimization without `--rebalance-frequency` is complete and verified:
- `backtest/cli.py`: when `--walk-forward` and `--reoptimize` are set, signal-derived weights are built and `engine.walk_forward_portfolio(..., reoptimize=True, optimizer=opt_fn)` is called regardless of `--rebalance-frequency`. The existing `rebalance_freq` branch (rebalanced weights + reoptimize) is unchanged. `--walk-forward` without `--reoptimize` keeps the strategy-based `engine.walk_forward` path (backward compatible).
- `--reoptimize`/`--optimizer` flags and `reoptimize`/`optimizer` config keys already existed; no new flags/schema keys needed.
- Tests in `tests/test_walk_forward_reoptimize.py` cover: CLI reoptimize without `--rebalance-frequency` runs end-to-end, optimizer applied (weights differ from static), backward compatibility when `--reoptimize` not set, and config-driven reoptimize without `rebalance_frequency`.
- Verified: 281 tests pass (1 skipped), `ruff check` clean, `mypy backtest/ strategies/ utils/` clean.

## Next task for the next agent

### Add Brinson attribution to the CLI/report layer

The framework already supports Brinson attribution and factor attribution via `utils/attribution.py` (imported in `backtest/cli.py` as `benchmark_weights_df` / `factor_returns_df`), but the CLI currently only passes these DataFrames into the engine and never renders an attribution report. Make attribution a first-class report output.

### Objective
Surface Brinson (and factor) attribution results from a backtest run through the CLI and the report generators (`utils/reporting.py`), so a user can run `cryptoquant ... --benchmark-weights-csv weights.csv --report attribution` (or `--report full` with attribution included) and get an attribution breakdown in the text/JSON/HTML/PDF output.

### Requirements
1. `utils/reporting.py`: add `generate_attribution_report(...)` (text) and `attribution_report_to_dict(...)` (JSON-serializable) that consume the attribution result dict already produced by the engine (keys like `brinson_attribution`, `factor_attribution` if present) and render a readable breakdown.
2. `backtest/cli.py`: when `--report attribution` (or a new `--attribution` flag) is set and benchmark-weights / factor-returns CSVs are provided, render the attribution report instead of / in addition to the normal backtest report. Keep `--report full`/`--report risk` behavior unchanged when attribution inputs are absent.
3. `backtest/config.py`: add `report` choice `"attribution"` (and alias) to `CONFIG_SCHEMA`/`validate_config` if not already present.
4. Add tests in `tests/test_attribution_reporting.py` covering: text report renders allocation/interaction/select effect rows; JSON dict is serializable and contains expected keys; HTML/PDF paths include attribution when inputs present; backward compatibility when no attribution inputs provided.
5. Keep public API backward compatible; all existing tests must still pass; ruff and mypy clean.
6. Follow existing code style (4-space indent, `from __future__ import annotations`, type hints on public functions); no `# type: ignore` for real bugs.

### Verification
```bash
python3 -m pytest tests/ -q
python3 -m ruff check backtest/ data/ strategies/ utils/ tests/ examples/
python3 -m mypy backtest/ strategies/ utils/
```