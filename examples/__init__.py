"""Real-data validation and demonstration scripts for cryptoquantstatarbstrats.

Scripts in this package insert the repository root onto ``sys.path`` so they
can import ``backtest``, ``data``, ``strategies``, and ``utils`` regardless of
the current working directory. They are intentionally not importable as a
package from outside the repository root; the empty ``__init__`` here only
exists so test modules can import helper functions (e.g.
``examples.run_portfolio_real.PortfolioRiskController``) without a
``ModuleNotFoundError`` during collection.
"""