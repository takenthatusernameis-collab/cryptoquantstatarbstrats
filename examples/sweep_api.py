"""Example: programmatic usage of the sweep API.

Shows both the instance-based approach and the strategy factory/callable
approach (which avoids mutating a shared strategy instance).
"""

from backtest.engine import BacktestEngine
from backtest.sweep import run_parameter_sweep
from data.loader import DataLoader
from strategies.mean_reversion import MeanReversionStrategy

loader = DataLoader()
data = loader.load_data(["BTC"], "2024-01-01", "2024-01-15", freq="1h")
data = loader.clean_data(data)

engine = BacktestEngine(initial_capital=100_000.0)
rows = run_parameter_sweep(
    MeanReversionStrategy("BTC"),
    data,
    {"lookback": [20, 30, 50], "entry_threshold": [1.5, 2.0]},
    train_period=60,
    test_period=20,
    fee_rate=0.0,
    slippage=0.0,
    metric="calmar_ratio",
    engine=engine,
)

for r in rows:
    print(r)


# Factory/callable usage: a fresh strategy instance is built for every combo,
# so the caller never has to worry about mutating a shared object.
def strategy_factory(combo):
    return MeanReversionStrategy(
        "BTC",
        lookback=int(combo.get("lookback", 30)),
        entry_threshold=float(combo.get("entry_threshold", 2.0)),
    )


rows_factory = run_parameter_sweep(
    strategy_factory,
    data,
    {"lookback": [20, 30, 50], "entry_threshold": [1.5, 2.0]},
    train_period=60,
    test_period=20,
    fee_rate=0.0,
    slippage=0.0,
    metric="calmar_ratio",
    engine=engine,
)

print("--- factory results ---")
for r in rows_factory:
    print(r)
