"""
exchange.py (replacement)
Production Exchange Wrapper for INDODAX using CCXT.

Replace the existing exchange.py with this file.
"""

from __future__ import annotations

import time
import ccxt
import config


class ExchangeClient:
    def __init__(self):
        self.exchange = ccxt.indodax({
            "apiKey": config.API_KEY,
            "secret": config.API_SECRET,
            "enableRateLimit": True,
            "timeout": 30000,
        })
        self.markets = {}

    def initialize(self):
        self.markets = self.retry_api(self.exchange.load_markets)

    def retry_api(self, func, *args, **kwargs):
        delay = getattr(config, "INITIAL_BACKOFF", 1)
        retry = getattr(config, "MAX_API_RETRY", 5)
        last = None
        for _ in range(retry):
            try:
                return func(*args, **kwargs)
            except Exception as e:
                last = e
                time.sleep(delay)
                delay *= 2
        raise last

    # ---------- Market ----------
    def market_info(self, symbol):
        return self.markets.get(symbol)

    def amount_precision(self, symbol, amount):
        return self.exchange.amount_to_precision(symbol, amount)

    def price_precision(self, symbol, price):
        return self.exchange.price_to_precision(symbol, price)

    def minimum_amount(self, symbol):
        m = self.market_info(symbol) or {}
        return float(m.get("limits", {}).get("amount", {}).get("min") or 0)

    def minimum_cost(self, symbol):
        m = self.market_info(symbol) or {}
        return float(m.get("limits", {}).get("cost", {}).get("min") or 0)

    # ---------- Data ----------
    def safe_balance(self):
        return self.retry_api(self.exchange.fetch_balance)

    def fetch_ticker(self, symbol):
        return self.retry_api(self.exchange.fetch_ticker, symbol)

    def fetch_order_book(self, symbol, limit=20):
        return self.retry_api(self.exchange.fetch_order_book, symbol, limit)

    def fetch_ohlcv(self, symbol, timeframe, limit=200):
        return self.retry_api(self.exchange.fetch_ohlcv, symbol, timeframe=timeframe, limit=limit)

    # ---------- Orders ----------
    def safe_limit_buy(self, symbol, amount):
        ask = float(self.fetch_ticker(symbol)["ask"])
        price = float(self.price_precision(symbol, ask * (1 + config.BUY_SLIPPAGE)))
        amount = float(self.amount_precision(symbol, amount))
        return self.retry_api(self.exchange.create_limit_buy_order, symbol, amount, price)

    def safe_limit_sell(self, symbol, amount):
        bid = float(self.fetch_ticker(symbol)["bid"])
        price = float(self.price_precision(symbol, bid * (1 - config.SELL_SLIPPAGE)))
        amount = float(self.amount_precision(symbol, amount))
        return self.retry_api(self.exchange.create_limit_sell_order, symbol, amount, price)

    def fetch_order(self, order_id, symbol):
        return self.retry_api(self.exchange.fetch_order, order_id, symbol)

    def fetch_open_orders(self, symbol=None):
        return self.retry_api(self.exchange.fetch_open_orders, symbol)

    def fetch_closed_orders(self, symbol=None):
        return self.retry_api(self.exchange.fetch_closed_orders, symbol)

    def fetch_my_trades(self, symbol=None):
        return self.retry_api(self.exchange.fetch_my_trades, symbol)

    def cancel_order(self, order_id, symbol):
        return self.retry_api(self.exchange.cancel_order, order_id, symbol)

    def wait_order_filled(self, order_id, symbol, retry=10, delay=2):
        for _ in range(retry):
            order = self.fetch_order(order_id, symbol)
            status = str(order.get("status", "")).lower()
            if status in ("closed", "filled"):
                return True
            if status == "canceled":
                return False
            time.sleep(delay)
        return False

    def verify_asset_balance(self, asset):
        bal = self.safe_balance()
        return float(bal.get(asset, {}).get("free", 0))

    def health_check(self):
        try:
            self.safe_balance()
            return True
        except Exception:
            return False
