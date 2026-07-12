"""
validator.py
Pre-BUY validation engine.

Comments: English
Terminal logs: Indonesian
"""

from __future__ import annotations

from typing import Dict

import config
from exchange import ExchangeClient
from storage import StorageManager


class BuyValidator:
    """Validate whether a BUY is allowed."""

    def __init__(self, exchange: ExchangeClient, storage: StorageManager):
        self.exchange = exchange
        self.storage = storage

    def _balance_ok(self, required_idr: float) -> bool:
        balance = self.exchange.fetch_balance()
        idr = balance.get("IDR", {}).get("free", 0)
        return idr >= required_idr

    def _cooldown_ok(self, symbol: str) -> bool:
        cooldown = self.storage.cooldown.load()
        return symbol not in cooldown

    def _position_ok(self, symbol: str) -> bool:
        active = self.storage.active_trades.load()
        layers = active.get(symbol, [])
        return len(layers) < config.MAX_LAYER_PER_COIN

    def _portfolio_ok(self) -> bool:
        active = self.storage.active_trades.load()
        total = sum(len(v) for v in active.values())
        return total < config.MAX_ACTIVE_TRADES

    def _spread_ok(self, spread: float) -> bool:
        return spread <= config.MAX_SPREAD_PERCENT

    def _volume_ok(self, volume: float) -> bool:
        return volume >= config.MIN_VOLUME_IDR

    def _orderbook_ok(self, snapshot: Dict) -> bool:
        book = snapshot.get("orderbook", {})
        bids = book.get("bids", [])
        asks = book.get("asks", [])
        return len(bids) >= 5 and len(asks) >= 5

    def validate(self, snapshot: Dict, ai_score: Dict) -> tuple[bool, str]:
        symbol = snapshot["symbol"]

        if not ai_score.get("eligible_buy"):
            return False, "AI_SCORE"

        if not self._spread_ok(snapshot["spread"]):
            return False, "SPREAD"

        if not self._volume_ok(snapshot["volume"]):
            return False, "VOLUME"

        if not self._balance_ok(config.BASE_TRADE_AMOUNT):
            return False, "BALANCE"

        if not self._cooldown_ok(symbol):
            return False, "COOLDOWN"

        if not self._position_ok(symbol):
            return False, "MAX_LAYER"

        if not self._portfolio_ok():
            return False, "MAX_ACTIVE"

        if not self._orderbook_ok(snapshot):
            return False, "ORDERBOOK"

        print(f"[BUY] {symbol} lolos seluruh validasi.")
        return True, "OK"
