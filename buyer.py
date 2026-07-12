"""
buyer.py
Production BUY engine using Exchange V2 wrapper.

Comments: English
Terminal logs: Indonesian
"""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

import config
from exchange import ExchangeClient
from history import HistoryEngine
from storage import StorageManager


class Buyer:

    def __init__(self,
                 exchange: ExchangeClient,
                 storage: StorageManager,
                 history: HistoryEngine):
        self.exchange = exchange
        self.storage = storage
        self.history = history

    def buy(self, symbol: str) -> bool:

        ticker = self.exchange.fetch_ticker(symbol)
        ask = float(ticker["ask"])

        amount = config.BASE_TRADE_AMOUNT / ask
        amount = float(self.exchange.amount_precision(symbol, amount))

        if amount < self.exchange.minimum_amount(symbol):
            print(f"[BUY] Amount {symbol} di bawah minimum.")
            return False

        try:
            order = self.exchange.safe_limit_buy(symbol, amount)
        except Exception as e:
            print(f"[ERROR] BUY {symbol}: {e}")
            return False

        order_id = order.get("id")
        if order_id and not self.exchange.wait_order_filled(order_id, symbol):
            self.exchange.cancel_order(order_id, symbol)
            print(f"[BUY] Order {symbol} dibatalkan karena timeout.")
            return False

        buy_price = float(order.get("price") or ask)

        layer = {
            "trade_id": str(uuid4()),
            "layer_id": str(uuid4()),
            "symbol": symbol,
            "buy_time": datetime.now(timezone.utc).astimezone().isoformat(),
            "buy_price": buy_price,
            "amount": amount,
            "take_profit": config.DEFAULT_TAKE_PROFIT,
            "stop_loss": config.DEFAULT_STOP_LOSS,
            "highest_price": buy_price,
            "highest_profit": 0.0,
            "status": "ACTIVE"
        }

        active = self.storage.active_trades.load()
        active.setdefault(symbol, []).append(layer)
        self.storage.active_trades.save(active)

        self.history.record(
            symbol=symbol,
            side="BUY",
            reason="ENTRY",
            price=buy_price,
            amount=amount,
            trade_id=layer["trade_id"],
            layer_id=layer["layer_id"]
        )

        print(f"[BUY] {symbol} berhasil dibeli.")
        return True
