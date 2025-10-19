from __future__ import annotations

class Broker:
    """
    A broker accepts market orders, updates cash/position 
    with no slippage/fees (keep deterministic for tests)
    """

    def __init__(self, cash: float = 1_000_000.0, allow_short: bool = False):
        """Initialize broker with starting cash and shorting permission."""
        if cash < 0:
            raise ValueError("cash must be non-negative")
        self.cash = float(cash)
        self.position = 0
        self.allow_short = bool(allow_short)

    def market_order(self, side: str, qty: int, price: float) -> None:
        """Process a market order"""
        if side not in {"BUY", "SELL"}:
            raise ValueError("side must be 'BUY' or 'SELL'")
        if not isinstance(qty, int) or qty <= 0:
            raise ValueError("qty must be positive int")
        if price <= 0 or not (price == price):
            raise ValueError("price must be positive and finite")

        totalcost = qty * float(price) # total cost of the order

        if side == "BUY":
            if self.cash < totalcost:
                raise RuntimeError("insufficient cash")
            self.cash -= totalcost # update cash
            self.position += qty # update position
        else:
            if not self.allow_short and self.position < qty:
                raise RuntimeError("insufficient shares") 
            self.cash += totalcost # update cash
            self.position -= qty # update position

    def equity(self, price: float) -> float:
        """Calculate total equity"""
        if price <= 0 or not (price == price):
            raise ValueError("price must be positive and finite")
        return self.cash + self.position * float(price)
