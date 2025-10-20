import pandas as pd
import pytest

#basic test
def test_signals_length_and_type(strategy, rising_prices):
    signals = strategy.signals(rising_prices)
    assert isinstance(signals,pd.Series)
    assert len(signals)==len(rising_prices)

def test_breakout_signal_generation(strategy,volatile_prices):
    signals = strategy.signals(volatile_prices)
    assert signals.iloc[14] == 1#should bahave based on setting
    assert signals.iloc[13] == 0

def test_constant_prices_no_signal(strategy,constant_prices):
    signals = strategy.signals(constant_prices)
    assert (signals==0).all

def test_short_prices_raises_value_error(strategy):
    """Tests that a short price series correctly raises a ValueError."""
    short_prices = pd.Series([100, 101, 102])
    with pytest.raises(ValueError, match="length of price must be greater"):
        strategy.signals(short_prices)