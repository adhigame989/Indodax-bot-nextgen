"""
validator.py
Production BUY validation engine.

Comments: English
Terminal logs: Indonesian
"""

from __future__ import annotations
from typing import Dict, Tuple

import config
from exchange import ExchangeClient
from storage import StorageManager


class BuyValidator:
    """Validate BUY request before sending order."""

    def __init__(self, exchange: ExchangeClient, storage: StorageManager):
        self.exchange = exchange
        self.storage = storage

    def validate(self, snapshot: Dict, ai_score: Dict) -> Tuple[bool, str]:
        symbol = snapshot["symbol"]

        if not ai_score.get("eligible_buy", False):
            return False, "AI_SCORE"

        if snapshot.get("spread", 999) > config.MAX_SPREAD_PERCENT:
            return False, "SPREAD"

        if snapshot.get("volume", 0) < config.MIN_VOLUME_IDR:
            return False, "VOLUME"

        balance = self.exchange.safe_balance()
        idr = float(balance.get("IDR", {}).get("free", 0))
        if idr < config.BASE_TRADE_AMOUNT:
            return False, "BALANCE"

        cooldown = self.storage.cooldown.load()
        if symbol in cooldown:
            return False, "COOLDOWN"

        active = self.storage.active_trades.load()
        if not isinstance(active, dict):
            active = {}

        if len(active.get(symbol, [])) >= config.MAX_LAYER_PER_COIN:
            return False, "MAX_LAYER"

        total_layers = sum(len(v) for v in active.values())
        if total_layers >= config.MAX_ACTIVE_TRADES:
            return False, "MAX_ACTIVE"

        ticker = self.exchange.fetch_ticker(symbol)
        ask = float(ticker["ask"])

        amount = config.BASE_TRADE_AMOUNT / ask
        amount = float(self.exchange.amount_precision(symbol, amount))

        if amount < self.exchange.minimum_amount(symbol):
            return False, "MIN_ORDER"

        orderbook = snapshot.get("orderbook", {})
        bids = orderbook.get("bids", [])
        asks = orderbook.get("asks", [])

        if len(bids) < 5 or len(asks) < 5:
            return False, "ORDERBOOK"

        best_bid = float(bids[0][0])
        best_ask = float(asks[0][0])

        slippage = ((best_ask - best_bid) / best_bid) * 100
        if slippage > config.MAX_SPREAD_PERCENT:
            return False, "SLIPPAGE"

        print(f"[VALIDATOR] {symbol} lolos semua validasi.")
        return True, "OK"
