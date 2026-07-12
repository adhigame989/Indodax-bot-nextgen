"""
seller.py
SELL engine for INDODAX AI Trading Bot.

Comments: English
Terminal logs: Indonesian
"""

from __future__ import annotations

from typing import Dict

import config
from exchange import ExchangeClient
from history import HistoryEngine
from storage import StorageManager


class Seller:
    """Execute safe SELL operations."""

    def __init__(self, exchange: ExchangeClient,
                 storage: StorageManager,
                 history: HistoryEngine):
        self.exchange = exchange
        self.storage = storage
        self.history = history

    def sell_layer(self,
                   symbol: str,
                   layer: Dict,
                   reason: str) -> bool:
        """Sell a single layer safely."""

        balance = self.exchange.fetch_balance()
        base = symbol.split("/")[0]

        asset = balance.get(base, {}).get("free", 0)

        if asset <= 0:
            print(f"[SELL] Asset {base} tidak ditemukan.")
            return False

        amount = min(asset, layer["amount"])
        amount = float(self.exchange.amount_precision(symbol, amount))

        try:
            order = self.exchange.create_market_sell(symbol, amount)
        except Exception as err:
            print(f"[ERROR] SELL {symbol} gagal: {err}")
            return False

        order_id = order.get("id")

        if order_id:
            status = self.exchange.fetch_order(order_id, symbol)

            if status.get("status") not in ("closed", "filled"):
                print(f"[SELL] Order {symbol} belum selesai.")
                return False

        ticker = self.exchange.fetch_ticker(symbol)
        sell_price = float(ticker["last"])

        buy_price = layer["buy_price"]

        profit_percent = (
            (sell_price - buy_price) / buy_price
        ) * 100

        profit_idr = (
            (sell_price - buy_price)
            * amount
        )

        active = self.storage.active_trades.load()

        if symbol in active:
            active[symbol] = [
                x for x in active[symbol]
                if x["layer_id"] != layer["layer_id"]
            ]

            if not active[symbol]:
                del active[symbol]

            self.storage.active_trades.save(active)

        self.history.record(
            symbol=symbol,
            side="SELL",
            reason=reason,
            price=sell_price,
            amount=amount,
            profit_percent=profit_percent,
            profit_idr=profit_idr,
            trade_id=layer["trade_id"],
            layer_id=layer["layer_id"],
        )

        if reason in ("STOP_LOSS", "TRAILING", "TIMEOUT"):
            cooldown = self.storage.cooldown.load()
            cooldown[symbol] = {
                "reason": reason,
                "timestamp": layer["buy_time"]
            }
            self.storage.cooldown.save(cooldown)

        print(
            f"[SELL] {symbol} berhasil dijual | "
            f"{reason} | {profit_percent:.2f}%"
        )

        return True
