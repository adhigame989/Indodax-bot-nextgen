"""
buyer.py
BUY engine for INDODAX AI Trading Bot.
"""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4

import config
from exchange import ExchangeClient
from storage import StorageManager
from history import HistoryEngine


class Buyer:
    """Execute validated BUY orders."""

    def __init__(self, exchange: ExchangeClient, storage: StorageManager, history: HistoryEngine):
        self.exchange = exchange
        self.storage = storage
        self.history = history

    def buy(self, symbol: str) -> bool:
        market = self.exchange.market(symbol)
        if market is None:
            print(f"[BUY] Market {symbol} tidak ditemukan.")
            return False

        ticker = self.exchange.fetch_ticker(symbol)
        buy_price = float(ticker["last"])

        amount = config.BASE_TRADE_AMOUNT / buy_price
        amount = float(self.exchange.amount_precision(symbol, amount))

        try:
            order = self.exchange.create_market_buy(symbol, amount)
        except Exception as err:
            print(f"[ERROR] BUY {symbol} gagal: {err}")
            return False

        order_id = order.get("id")
        if order_id:
            status = self.exchange.fetch_order(order_id, symbol)
            if status.get("status") not in ("closed", "filled"):
                print(f"[BUY] Order {symbol} belum selesai.")
                return False

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

        print(f"[BUY] BUY {symbol} berhasil.")
        return True
