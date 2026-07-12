"""
exchange.py
CCXT wrapper for INDODAX Spot.

Comments: English
Terminal logs: Indonesian
"""

from __future__ import annotations

import time
from typing import Any, Dict, List

import ccxt

import config


class ExchangeClient:
    """Production-ready CCXT wrapper."""

    def __init__(self):
        self.exchange = ccxt.indodax({
            "apiKey": config.API_KEY,
            "secret": config.API_SECRET,
            "enableRateLimit": True,
            "timeout": 30000,
        })
        self.markets: Dict[str, Any] = {}

    def _retry(self, func, *args, **kwargs):
        """Retry API calls with exponential backoff."""
        delay = config.INITIAL_BACKOFF
        last_error = None

        for attempt in range(1, config.MAX_API_RETRY + 1):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last_error = e
                print(f"[WARNING] Retry API {attempt}/{config.MAX_API_RETRY}: {e}")
                if attempt < config.MAX_API_RETRY:
                    time.sleep(delay)
                    delay *= 2

        raise last_error

    def initialize(self):
        """Load exchange markets."""
        self.markets = self._retry(self.exchange.load_markets)
        print(f"[INFO] Market berhasil dimuat ({len(self.markets)} pair).")

    def fetch_balance(self):
        return self._retry(self.exchange.fetch_balance)

    def fetch_ticker(self, symbol: str):
        return self._retry(self.exchange.fetch_ticker, symbol)

    def fetch_order_book(self, symbol: str, limit: int = 20):
        return self._retry(self.exchange.fetch_order_book, symbol, limit)

    def fetch_ohlcv(self, symbol: str, timeframe: str, limit: int = 200):
        return self._retry(
            self.exchange.fetch_ohlcv,
            symbol,
            timeframe=timeframe,
            limit=limit,
        )

    def create_market_buy(self, symbol: str, amount: float):
        print(f"[BUY] Mengirim order BUY {symbol}")
        return self._retry(
            self.exchange.create_market_buy_order,
            symbol,
            amount,
        )

    def create_market_sell(self, symbol: str, amount: float):
        print(f"[SELL] Mengirim order SELL {symbol}")
        return self._retry(
            self.exchange.create_market_sell_order,
            symbol,
            amount,
        )

    def fetch_order(self, order_id: str, symbol: str):
        return self._retry(
            self.exchange.fetch_order,
            order_id,
            symbol,
        )

    def amount_precision(self, symbol: str, amount: float):
        return self.exchange.amount_to_precision(symbol, amount)

    def price_precision(self, symbol: str, price: float):
        return self.exchange.price_to_precision(symbol, price)

    def market(self, symbol: str):
        return self.markets.get(symbol)
