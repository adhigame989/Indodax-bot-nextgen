"""
buyer.py
INDODAX BOT NEXTGEN V4
"""

from __future__ import annotations

import time
import uuid

from logger import info, warning, error


class Buyer:
    def __init__(self, exchange, position_manager, config):
        self.exchange = exchange
        self.pm = position_manager
        self.cfg = config

    def _layer_id(self):
        return uuid.uuid4().hex[:12]

    def can_buy(self, symbol):
        max_layer = getattr(self.cfg, "MAX_LAYER_PER_COIN", 3)
        return len(self.pm.layers(symbol)) < max_layer

    def create_position(self, symbol, amount_idr, buy_price, amount_coin):
        return {
            "layer_id": self._layer_id(),
            "symbol": symbol,
            "buy_price": float(buy_price),
            "amount": float(amount_coin),
            "cost": float(amount_idr),
            "status": "OPEN",
            "highest_price": float(buy_price),
            "highest_profit": 0.0,
            "profit_percent": 0.0,
            "manual_sell": False,
        }

    def buy(self, symbol, amount_idr, price):
        try:
            if not self.can_buy(symbol):
                warning(f"Layer penuh: {symbol}")
                return None

            amount_coin = amount_idr / price

            order = self.exchange.create_limit_buy_order(
                symbol,
                amount_coin,
                price
            )

            time.sleep(getattr(self.cfg, "ORDER_WAIT", 2))

            position = self.create_position(
                symbol,
                amount_idr,
                price,
                amount_coin
            )

            if isinstance(order, dict):
                position["order_id"] = order.get("id")

            self.pm.add_layer(symbol, position)

            info(f"BUY sukses {symbol}")

            return position

        except Exception as e:
            error(f"BUY ERROR {symbol}: {e}")
            return None
