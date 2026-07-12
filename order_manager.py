"""
order_manager.py
Production Order Manager V3 (Thread Safe)

Comments: English
Terminal logs: Indonesian
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
from threading import RLock
from typing import Optional

from exchange import ExchangeClient
from logger import buy, sell, info, warning, error


class OrderState(str, Enum):
    BUY_PENDING = "BUY_PENDING"
    BUY_FILLED = "BUY_FILLED"
    BUY_CANCELLED = "BUY_CANCELLED"
    SELL_PENDING = "SELL_PENDING"
    SELL_FILLED = "SELL_FILLED"
    SELL_CANCELLED = "SELL_CANCELLED"


@dataclass
class OrderResult:
    success: bool
    state: OrderState
    order: Optional[dict]
    message: str = ""


class OrderManager:
    """Thread-safe order lifecycle manager."""

    def __init__(self, exchange: ExchangeClient):
        self.exchange = exchange
        self._lock = RLock()

    def place_buy(self, symbol: str, amount: float) -> OrderResult:
        with self._lock:
            buy(f"BUY {symbol} dimulai")
            return self._execute(symbol, amount, True)

    def place_sell(self, symbol: str, amount: float) -> OrderResult:
        with self._lock:
            sell(f"SELL {symbol} dimulai")
            return self._execute(symbol, amount, False)

    def _execute(self, symbol: str, amount: float, is_buy: bool) -> OrderResult:
        try:
            order = (
                self.exchange.safe_limit_buy(symbol, amount)
                if is_buy else
                self.exchange.safe_limit_sell(symbol, amount)
            )
        except Exception as exc:
            error(f"Order gagal: {exc}")
            return OrderResult(
                False,
                OrderState.BUY_CANCELLED if is_buy else OrderState.SELL_CANCELLED,
                None,
                str(exc)
            )

        order_id = order.get("id")
        if not order_id:
            return OrderResult(
                False,
                OrderState.BUY_CANCELLED if is_buy else OrderState.SELL_CANCELLED,
                order,
                "Order ID kosong"
            )

        if self.exchange.wait_order_filled(order_id, symbol):
            latest = self.exchange.fetch_order(order_id, symbol)
            state = OrderState.BUY_FILLED if is_buy else OrderState.SELL_FILLED
            info(f"{symbol} order filled")
            return OrderResult(True, state, latest)

        warning(f"{symbol} timeout, cancel order")

        try:
            self.exchange.cancel_order(order_id, symbol)
        except Exception as exc:
            warning(f"Cancel gagal: {exc}")

        return OrderResult(
            False,
            OrderState.BUY_CANCELLED if is_buy else OrderState.SELL_CANCELLED,
            None,
            "TIMEOUT"
        )

    def sync(self, order_id: str, symbol: str):
        with self._lock:
            try:
                return self.exchange.fetch_order(order_id, symbol)
            except Exception as exc:
                warning(f"Sync gagal: {exc}")
                return None

    def open_orders(self, symbol=None):
        with self._lock:
            return self.exchange.fetch_open_orders(symbol)

    def closed_orders(self, symbol=None):
        with self._lock:
            return self.exchange.fetch_closed_orders(symbol)

    def trades(self, symbol=None):
        with self._lock:
            return self.exchange.fetch_my_trades(symbol)
