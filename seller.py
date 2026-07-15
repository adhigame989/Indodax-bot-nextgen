"""
seller.py
INDODAX BOT NEXTGEN V4
"""

from __future__ import annotations

import time

from logger import info, warning, error


class Seller:
    def __init__(self, exchange, position_manager, config):
        self.exchange = exchange
        self.pm = position_manager
        self.cfg = config

    def sell(self, symbol, layer_id, price, reason="SELL"):
        layer = self.pm.get_layer(symbol, layer_id)
        if layer is None:
            warning(f"Layer tidak ditemukan: {symbol}/{layer_id}")
            return False

        try:
            self.pm.update_status(symbol, layer_id, "SELLING")

            amount = float(layer.get("amount", 0))
            if amount <= 0:
                raise ValueError("amount <= 0")

            order = self.exchange.create_limit_sell_order(
                symbol,
                amount,
                price
            )

            time.sleep(getattr(self.cfg, "ORDER_WAIT", 2))

            buy_price = float(layer.get("buy_price", price))
            profit_pct = ((price - buy_price) / buy_price) * 100 if buy_price else 0.0

            layer["sell_price"] = float(price)
            layer["profit_percent"] = round(profit_pct, 4)
            layer["status"] = "CLOSED"
            layer["sell_reason"] = reason
            layer["closed"] = True

            if isinstance(order, dict):
                layer["sell_order_id"] = order.get("id")

            self.pm.replace_layer(symbol, layer)
            self.pm.remove_layer(symbol, layer_id)
            self.pm.cleanup_empty()

            info(f"SELL sukses {symbol} ({reason}) {profit_pct:.2f}%")
            return True

        except Exception as e:
            self.pm.update_status(symbol, layer_id, "OPEN")
            error(f"SELL ERROR {symbol}: {e}")
            return False

    def manual_sell(self, symbol, layer_id, price):
        self.pm.mark_manual_sell(symbol, layer_id)
        return self.sell(symbol, layer_id, price, reason="MANUAL")

    def stop_loss(self, symbol, layer_id, price):
        return self.sell(symbol, layer_id, price, reason="STOP_LOSS")

    def take_profit(self, symbol, layer_id, price):
        return self.sell(symbol, layer_id, price, reason="TAKE_PROFIT")

    def trailing_sell(self, symbol, layer_id, price):
        return self.sell(symbol, layer_id, price, reason="TRAILING")

    def timeout_sell(self, symbol, layer_id, price):
        return self.sell(symbol, layer_id, price, reason="TIMEOUT")
