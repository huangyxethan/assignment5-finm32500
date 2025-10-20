import pandas as pd
from unittest.mock import MagicMock,DEFAULT
try:
    from backtester.engine import Backtester
except ImportError:
    print("Source Broken. Please implement backtester under .backtester. Aborting...")

def test_engine_loop_and_final_equity(broker,rising_prices):
    dummy_strategy = MagicMock()
    #standard att -> MagicMock().return_value
    dummy_strategy.signals.return_value=pd.Series(0, index=rising_prices.index)
    bt =Backtester(dummy_strategy,broker,5)
    equity_curve = bt.run(rising_prices)
    # standard method -> MagicMock().assert_called_once_with(params)
    dummy_strategy.signals.assert_called_once_with(rising_prices)
    final_equity = equity_curve.iloc[-1]# return pd.Series
    assert final_equity == broker.initial_cash

def test_engine_uses_tminus1_signal(broker,rising_prices):
    # Force exactly one buy at t=10 by controlling signals
    fake_strategy = MagicMock()
    #create signal
    signals=pd.Series(0, index=rising_prices.index)
    signals.iloc[9]=1

    fake_strategy.signals.return_value=signals
    bt = Backtester(fake_strategy,broker,1)
    bt.run(rising_prices)
    price_at_t10=rising_prices.iloc[10]
    assert broker.position==1
    assert broker.cash==broker.initial_cash-price_at_t10

def test_engine_handles_broker_failure(broker,rising_prices):
    failing_broker = MagicMock(wraps=broker)#keep orginal broker function
    failing_broker.cash=broker.cash
    failing_broker.market_order.side_effect = [
        DEFAULT,#success at first time
        ValueError("Simulated API error"),#fail at the second time
        DEFAULT
    ]
    fake_strategy = MagicMock()
    signals = pd.Series(0, index=rising_prices.index)#len==15
    signals.iloc[10] = 1
    signals.iloc[12] = 1 
    signals.iloc[14] = 1
    fake_strategy.signals.return_value = signals

    bt = Backtester(fake_strategy, failing_broker,1)
    bt.run(rising_prices)

    assert failing_broker.market_order.call_count == 3
    assert broker.position == 2