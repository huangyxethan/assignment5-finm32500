from __future__ import annotations
import numpy as np
import pandas as pd
from typing import Dict, Optional


class PriceLoader:
    """
    Returns a pandas.Series of prices for a single symbol (use synthetic data for tests).
    """
    def __init__(self, data: Optional[Dict[str, pd.Series]] = None):
        """Initializes an empty dictionary _data to store symbol–price pairs."""
        self._data: Dict[str, pd.Series] = {}
        if data:
            for sym, ser in data.items():
                self.register(sym, ser)

    def register(self, symbol: str, prices: pd.Series) -> None:
        """"Register a new symbol with its corresponding price series."""
        if not isinstance(prices, pd.Series):
            raise TypeError("prices must be a pandas Series")
        ser = prices.astype(float).copy()
        ser = ser[~ser.index.duplicated(keep="first")] # remove duplicates
        ser = ser.sort_index() # ensure sorted by date
        self._data[symbol] = ser

    def get(self, symbol: str) -> pd.Series:
        """Retrieve the price series for a given symbol."""
        return self._data[symbol].copy() # return a copy to prevent external modification

    @staticmethod
    def synthetic(
        n: int = 252,
        start: float = 100.0,
        mu: float = 0.0, # drift
        sigma: float = 0.01, # volatility
        seed: Optional[int] = None,
        freq: str = "D", # frequency of the date index
    ) -> pd.Series:
        """Generate a synthetic price series using geometric Brownian motion."""
        rng = np.random.default_rng(seed) # create a random number generator
        rets = rng.normal(mu, sigma, size=n) # simulate n normal returns
        path = start * np.exp(np.cumsum(rets)) # compute price path under log-normal
        idx = pd.date_range("2000-01-01", periods=n, freq=freq) # create date index
        return pd.Series(path, index=idx, name="price")
