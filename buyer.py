"""
buyer.py
Production BUY engine.

Comments: English
Terminal logs: Indonesian
"""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

import config
from history import HistoryEngine
from logger import buy, error
from order_manager import OrderManager
from position_manager import PositionManager


class Buyer:
    """Execute validated BUY requests."""

    def __init__(
        self,
        order_manager: OrderManager,
        positions: PositionManager,
        history: HistoryEngine,
    ):
        self.orders = order_manager
        self.positions = positions
        self.history = history

    def execute(self, symbol: str, amount: float) -> bool:
        """Place BUY and register new layer only after fill."""

        result = self.orders.place_buy(symbol, amount)

        if not result.success:
            error(f"BUY gagal {symbol}: {result.message}")
            return False

        order = result.order or {}
        price = float(order.get("price") or order.get("average") or 0)

        layer = {
            "trade_id": str(uuid4()),
            "layer_id": str(uuid4()),
            "symbol": symbol,
            "buy_time": datetime.now(timezone.utc).astimezone().isoformat(),
            "buy_price": price,
            "amount": amount,
            "take_profit": config.DEFAULT_TAKE_PROFIT,
            "stop_loss": config.DEFAULT_STOP_LOSS,
            "highest_price": price,
            "highest_profit": 0.0,
            "status": "ACTIVE",
            "order_id": order.get("id"),
        }

        self.positions.add_layer(symbol, layer)

        self.history.record(
            symbol=symbol,
            side="BUY",
            reason="ENTRY",
            price=price,
            amount=amount,
            trade_id=layer["trade_id"],
            layer_id=layer["layer_id"],
            order_id=order.get("id"),
        )

        buy(f"BUY berhasil {symbol} @ {price}")
        return True
