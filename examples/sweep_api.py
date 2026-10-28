"""Example: programmatic usage of the sweep API."""

from backtest.data_loader import DataLoader

from backtest.engine import BacktestEngine
from backtest.sweep import run_parameter_sweep
from strategies.mean_reversion import MeanReversionStrategy

loader = DataLoader()
data = loader.load_data(["BTC"], "2024-01-01", "2024-01-15", freq="1h")
data = loader.clean_data(data)

engine = BacktestEngine(initial_capital=100_000.0)
rows = run_parameter_sweep(
    MeanReversionStrategy(),
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
