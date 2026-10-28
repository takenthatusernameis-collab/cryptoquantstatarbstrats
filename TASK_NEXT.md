# Task for Next Agent

## Handoff from Previous Agent
Paper trading session reporting & artifact persistence is complete and verified:
- `backtest/paper_report.py`: `build_paper_trading_report`, `paper_report_to_dict`,
  `generate_paper_trading_report_text`, `generate_paper_trading_report_html`,
  `save_paper_trading_artifacts`, `load_paper_trading_artifacts` implemented.
- `backtest/cli.py`: `paper-trade` persists session artifacts (report, fills,
  equity curve, alerts) to `--artifact-dir` when `--monitor` or `--output-path`
  is used; `paper-report` subcommand generates/views a report from saved
  artifacts in json/text/html formats.
- `tests/test_paper_trading_report.py`: report generation, artifact persistence,
  missing-data backward compat, and CLI integration tests added - all passing.
- `python3 -m pytest tests/ -q` passes with 0 failures (421 passed, 1 skipped).
- `python3 -m ruff check backtest/ data/ strategies/ utils/ tests/ examples/` clean.
- `python3 -m mypy backtest/ strategies/ utils/` clean.
- Public API backward compatible; no new runtime dependencies; no `# type: ignore` for real bugs.

## Current State
All assigned tasks from the task chain are implemented. Test suite is fully green.

## Objective
COMPLETED - Paper trading session reporting & artifact persistence implemented and verified.

## Tasks
- [x] Task 1: Create `backtest/paper_report.py` to build a serializable paper-trading session report and render to JSON/text/HTML.
- [x] Task 2: Extend `backtest/cli.py` `paper-trade` to persist session artifacts to `--artifact-dir`; add a `paper-report` subcommand to generate/view a report from saved artifacts.
- [x] Task 3: Add tests in `tests/test_paper_trading_report.py`.
- [x] Task 4: Verify `python3 -m pytest tests/ -q`, `python3 -m ruff check ...`, and `python3 -m mypy ...` remain clean.

## Next task for the next agent
None - the full task chain is complete.

## Verification
```bash
python3 -m pytest tests/ -q
python3 -m ruff check backtest/ data/ strategies/ utils/ tests/ examples/
python3 -m mypy backtest/ strategies/ utils/
```

**Ready.**
