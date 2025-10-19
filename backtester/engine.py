from __future__ import annotations
import pandas as pd


class Backtester:
    """
    A backtester that runs a strategy against price data using a broker.
        - Compute signals from strategy
        - Execute yesterday's signal at today’s closing price (to avoid look-ahead bias)
        - Interpret signals as target positions
    """

    def __init__(self, strategy, broker, unit_size: int = 1):
        if unit_size <= 0:
            raise ValueError("unit_size must be positive")
        self.strategy = strategy
        self.broker = broker
        self.unit_size = int(unit_size)

    def run(self, prices: pd.Series) -> pd.Series:
        """
        Runs the backtest simulation over the given price series.
        Returns a pandas Series representing the equity curve 
        """
        if not isinstance(prices, pd.Series):
            raise TypeError("prices must be a pandas Series")
        if prices.empty:
            return pd.Series(dtype="float64")

        p = prices.astype(float)
        raw_sig = self.strategy.signals(p).astype("int64") # get signals for each time step
        exec_sig = raw_sig.shift(1)  # only act on yesterday’s signal today
        exec_sig.iloc[0] = 0  # at first day, no prior signal to act on.

        cash = [] # cash balance
        pos = [] # position size
        eq = [] # equity value

        for i, (ts, price) in enumerate(p.items()):
            # Determines the target number of shares based on the signal
            target = int(exec_sig.iloc[i]) * self.unit_size if exec_sig.notna().iloc[i] else 0
            # Compute change from current position
            delta = target - self.broker.position
            # Execute the change via the broker if non-zero change
            if delta != 0:
                side = "BUY" if delta > 0 else "SELL"
                self.broker.market_order(side, abs(delta), float(price))
            # Update cash, position, and equity
            cash.append(self.broker.cash)
            pos.append(self.broker.position)
            eq.append(self.broker.cash + self.broker.position * float(price))

        # Output equity curve
        out = pd.Series(eq, index=p.index, name="equity")

        # Store extra attributes for unit tests later
        out.attrs["cash"] = pd.Series(cash, index=p.index, name="cash")
        out.attrs["position"] = pd.Series(pos, index=p.index, name="position")
        out.attrs["signal_raw"] = raw_sig
        out.attrs["signal_exec"] = exec_sig

        return out
