"""
order_manager.py
Production Order Manager for INDODAX AI Bot.

Comments: English
Terminal logs: Indonesian
"""

from __future__ import annotations

from dataclasses import dataclass
from enum import Enum
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
    """Centralized order lifecycle."""

    def __init__(self, exchange: ExchangeClient):
        self.exchange = exchange

    def place_buy(self, symbol: str, amount: float) -> OrderResult:
        buy(f"Mengirim BUY {symbol}")
        return self._execute(symbol, amount, is_buy=True)

    def place_sell(self, symbol: str, amount: float) -> OrderResult:
        sell(f"Mengirim SELL {symbol}")
        return self._execute(symbol, amount, is_buy=False)

    def _execute(self, symbol: str, amount: float, is_buy: bool) -> OrderResult:
        try:
            order = (
                self.exchange.safe_limit_buy(symbol, amount)
                if is_buy
                else self.exchange.safe_limit_sell(symbol, amount)
            )
        except Exception as exc:
            error(f"Order gagal: {exc}")
            return OrderResult(
                False,
                OrderState.BUY_CANCELLED if is_buy else OrderState.SELL_CANCELLED,
                None,
                str(exc),
            )

        order_id = order.get("id")
        if not order_id:
            return OrderResult(
                False,
                OrderState.BUY_CANCELLED if is_buy else OrderState.SELL_CANCELLED,
                order,
                "Order ID tidak tersedia",
            )

        if self.exchange.wait_order_filled(order_id, symbol):
            latest = self.exchange.fetch_order(order_id, symbol)
            state = OrderState.BUY_FILLED if is_buy else OrderState.SELL_FILLED
            info(f"{symbol} order filled.")
            return OrderResult(True, state, latest)

        warning(f"{symbol} timeout, membatalkan order.")
        try:
            self.exchange.cancel_order(order_id, symbol)
        except Exception as exc:
            warning(f"Gagal cancel order: {exc}")

        return OrderResult(
            False,
            OrderState.BUY_CANCELLED if is_buy else OrderState.SELL_CANCELLED,
            None,
            "Timeout",
        )

    def sync(self, order_id: str, symbol: str) -> Optional[dict]:
        try:
            return self.exchange.fetch_order(order_id, symbol)
        except Exception as exc:
            warning(f"Sync order gagal: {exc}")
            return None
