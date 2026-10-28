# Task for Next Agent

## Handoff from Previous Agent
All requirements from the previous task (add attribution support to walk-forward reports) have been completed and verified:
- `backtest/engine.py`: `walk_forward`/`walk_forward_portfolio` pass `benchmark_weights`/`factor_returns` through `run_portfolio` → `_evaluate_weights`, which computes per-window `result["brinson"]` and `result["factor"]`.
- `utils/reporting.py`: `generate_walk_forward_report` aggregates Brinson/factor attribution across windows into `report["brinson"]`/`report["factor"]`; `walk_forward_report_to_dict` serializes it; text/HTML/PDF walk-forward generators render attribution sections.
- `backtest/cli.py`: walk-forward paths flow attribution inputs and route results through walk-forward report generators; attribution renders for `--report attribution`/`full`/`risk`.
- Tests in `tests/test_walk_forward_attribution.py` (11 tests) cover aggregation, text/HTML/PDF rendering, CLI integration, and backward compatibility.
- Verified: 315 tests pass (1 skipped), ruff clean, mypy clean on backtest/strategies/utils/.

## Next task for the next agent

### Add in-sample vs out-of-sample performance comparison to walk-forward reports

The framework runs walk-forward validation across train/test windows and reports per-window out-of-sample performance, but there is no in-sample (train-window) baseline for comparison. Users cannot tell whether out-of-sample performance has decayed relative to in-sample fit (a sign of overfitting). Add an IS/OOS comparison to walk-forward reporting.

### Objective
Surface in-sample vs out-of-sample performance per walk-forward window and in aggregate, rendered in walk-forward text/HTML/PDF reports.

### Requirements
1. `backtest/engine.py`: In `walk_forward` and `walk_forward_portfolio`, for each window also evaluate in-sample performance on the train window and attach `is_total_return`, `is_sharpe_ratio`, `is_max_drawdown` to the per-window result dict (with `oos_total_return` mirroring `total_return`). Aggregate `is_mean_return`, `oos_mean_return`, `oos_is_ratio` (mean OOS return / mean IS return) into the walk-forward result dict.
2. `utils/reporting.py`: Extend `generate_walk_forward_report` to include IS/OOS columns in the summary DataFrame and an `is_vs_oos` aggregate; extend `generate_walk_forward_text_report`, `generate_walk_forward_html_report`, and `generate_walk_forward_pdf_report` to render an "In-Sample vs Out-of-Sample" section when IS data is present.
3. `backtest/cli.py`: Ensure walk-forward runs surface IS/OOS comparison through the report generators (benchmark/factor inputs already flow).
4. Add tests in `tests/test_walk_forward_is_oos.py`: IS/OOS columns present per window, aggregate ratios computed, text/HTML/PDF rendering, backward compatibility when IS data absent.
5. Keep public API backward compatible; all existing tests must still pass; ruff and mypy clean.
6. Follow existing code style (4-space indent, `from __future__ import annotations`, type hints on public functions); no `# type: ignore` for real bugs.

### Verification
```bash
python3 -m pytest tests/ -q
python3 -m ruff check backtest/ data/ strategies/ utils/ tests/ examples/
python3 -m mypy backtest/ strategies/ utils/
```

**Ready for next agent.**
