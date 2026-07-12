"""
order_manager.py
Central order lifecycle manager for INDODAX AI Trading Bot.

Comments: English
Terminal logs: Indonesian
"""

from __future__ import annotations

import time
from enum import Enum
from typing import Optional

from exchange import ExchangeClient


class OrderState(str, Enum):
    BUY_PENDING = "BUY_PENDING"
    BUY_FILLED = "BUY_FILLED"
    BUY_CANCELLED = "BUY_CANCELLED"
    SELL_PENDING = "SELL_PENDING"
    SELL_FILLED = "SELL_FILLED"
    SELL_CANCELLED = "SELL_CANCELLED"


class OrderManager:
    """Handle all order lifecycle operations."""

    def __init__(self, exchange: ExchangeClient):
        self.exchange = exchange

    def place_limit_buy(self, symbol: str, amount: float):
        print(f"[ORDER] Membuat BUY {symbol}")
        order = self.exchange.safe_limit_buy(symbol, amount)
        return self._finalize(order, symbol, True)

    def place_limit_sell(self, symbol: str, amount: float):
        print(f"[ORDER] Membuat SELL {symbol}")
        order = self.exchange.safe_limit_sell(symbol, amount)
        return self._finalize(order, symbol, False)

    def _finalize(self, order: dict, symbol: str, is_buy: bool):
        order_id = order.get("id")
        if not order_id:
            return False, OrderState.BUY_CANCELLED if is_buy else OrderState.SELL_CANCELLED, None

        filled = self.exchange.wait_order_filled(order_id, symbol)

        if filled:
            state = OrderState.BUY_FILLED if is_buy else OrderState.SELL_FILLED
            print(f"[ORDER] {symbol} Filled")
            return True, state, self.exchange.fetch_order(order_id, symbol)

        try:
            self.exchange.cancel_order(order_id, symbol)
        except Exception:
            pass

        state = OrderState.BUY_CANCELLED if is_buy else OrderState.SELL_CANCELLED
        print(f"[ORDER] {symbol} Dibatalkan")
        return False, state, None

    def sync_order(self, order_id: str, symbol: str) -> Optional[dict]:
        try:
            return self.exchange.fetch_order(order_id, symbol)
        except Exception as e:
            print(f"[WARNING] Sinkronisasi order gagal: {e}")
            return None
