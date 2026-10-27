# Task for Next Agent

## Handoff from Previous Agent
All requirements from the previous task (Brinson attribution to the CLI/report layer) have been completed and verified:
- `utils/reporting.py`: `generate_attribution_report`, `attribution_report_to_dict`, Brinson/factor text rendering, HTML/PDF attribution integration.
- `backtest/cli.py`: `--report attribution` path, attribution surfaced in full/risk flows when inputs present.
- `backtest/config.py`: `report` includes `attribution` in schema/validation.
- Tests in `tests/test_attribution_reporting.py` all pass.
- Verified: 306 tests pass, 1 skipped, ruff clean, mypy clean on backtest/strategies/utils/.

## Next task for the next agent

### Add attribution support to walk-forward reports

The framework computes Brinson/factor attribution when benchmark/factor data are provided to the engine, but walk-forward runs aggregate per-window results and don't propagate attribution breakdowns into walk-forward reporting. Extend walk-forward reporting to surface attribution when available.

### Objective
Make attribution visible in walk-forward text/HTML/PDF reports when benchmark-weights / factor-returns are supplied to walk-forward runs.

### Requirements
1. `backtest/engine.py`: when running walk-forward with attribution inputs, aggregate Brinson/factor attribution across windows (or attach per-window and aggregate totals) into the walk-forward result dict (e.g. under `brinson`/`factor` keys) in a serializable form compatible with `utils.reporting`.
2. `utils/reporting.py`: extend `generate_walk_forward_report`/`walk_forward_report_to_dict` and HTML/PDF walk-forward generators to include an attribution section when present (mirroring the style of `generate_attribution_report`).
3. `backtest/cli.py`: ensure walk-forward + attribution inputs flow correctly and walk-forward reports render attribution when `--walk-forward-report`/walk-forward outputs are used.
4. Add tests in `tests/test_walk_forward_attribution.py` covering aggregation, text/HTML/PDF rendering, and backward compatibility when no attribution inputs are provided.
5. Keep public API backward compatible; all existing tests must still pass; ruff and mypy clean.
6. Follow existing code style (4-space indent, `from __future__ import annotations`, type hints on public functions); no `# type: ignore` for real bugs.

### Verification
```bash
python3 -m pytest tests/ -q
python3 -m ruff check backtest/ data/ strategies/ utils/ tests/ examples/
python3 -m mypy backtest/ strategies/ utils/
```

**Ready for next agent.**
