"""
Statistical Arbitrage Strategy Base Classes
"""

from abc import ABC, abstractmethod
from typing import Dict, List, Any
import pandas as pd


class Strategy(ABC):
    """Base class for all statistical arbitrage strategies."""
    
    def __init__(self, name: str, params: Dict[str, Any] = None):
        self.name = name
        self.params = params or {}
        self.positions = {}
        
    @abstractmethod
    def generate_signals(self, data: pd.DataFrame) -> pd.DataFrame:
        """Generate trading signals based on market data."""
        pass
        
    @abstractmethod
    def calculate_position_sizes(self, signals: pd.DataFrame) -> Dict[str, float]:
        """Calculate position sizes for each asset."""
        pass


class PairStrategy(Strategy):
    """Base class for pairs trading strategies."""
    
    def __init__(self, name: str, pair: tuple, params: Dict[str, Any] = None):
        super().__init__(name, params)
        self.pair = pair
        self.hedge_ratio = 1.0
