from __future__ import annotations
import numpy as np
import pandas as pd

class VolatilityBreakoutStrategy:
    """
    A trading strategy class that generates signals based on volatility breakouts
    """

    def __init__(self, window: int = 20, min_periods: int | None = None):
        """Initialize the strategy with a rolling window size and minimum periods."""
        self.window = int(window)
        self.min_periods = int(min_periods) if min_periods is not None else window

    def signals(self, prices: pd.Series) -> pd.Series:
        """Generate trading signals based on volatility breakouts."""
        if not isinstance(prices, pd.Series):
            raise TypeError("prices must be a pandas Series")
        if prices.empty:
            return pd.Series(dtype="int64")

        p = prices.astype(float)
        ret = p.pct_change() # daily percent returns
        vol = ret.rolling(self.window, min_periods=self.min_periods).std().shift(1) # rolling std dev

        sig = pd.Series(0, index=p.index, dtype="int64") # initialize signals to 0
        cond_buy = (ret > vol) & vol.notna() # buy when return > volatility
        cond_sell = (ret < -vol) & vol.notna() # sell when return < -volatility
        sig[cond_buy] = 1
        sig[cond_sell] = -1
        return sig
