"""
seller.py
Production SELL engine.

Comments: English
Terminal logs: Indonesian
"""

from __future__ import annotations

from history import HistoryEngine
from logger import error, sell
from order_manager import OrderManager
from position_manager import PositionManager


class Seller:
    """Execute SELL after strategy decision."""

    def __init__(
        self,
        order_manager: OrderManager,
        positions: PositionManager,
        history: HistoryEngine,
    ):
        self.orders = order_manager
        self.positions = positions
        self.history = history

    def execute(self, symbol: str, layer: dict, reason: str) -> bool:
        amount = float(layer["amount"])

        result = self.orders.place_sell(symbol, amount)

        if not result.success:
            error(f"SELL gagal {symbol}: {result.message}")
            return False

        order = result.order or {}
        price = float(order.get("price") or order.get("average") or 0)

        buy_price = float(layer["buy_price"])
        profit_percent = ((price - buy_price) / buy_price) * 100
        profit_idr = (price - buy_price) * amount

        self.history.record(
            symbol=symbol,
            side="SELL",
            reason=reason,
            price=price,
            amount=amount,
            profit_percent=profit_percent,
            profit_idr=profit_idr,
            trade_id=layer["trade_id"],
            layer_id=layer["layer_id"],
            order_id=order.get("id"),
        )

        self.positions.remove_layer(symbol, layer["layer_id"])

        sell(
            f"{symbol} | {reason} | "
            f"{profit_percent:.2f}% | "
            f"{profit_idr:.0f} IDR"
        )

        return True
