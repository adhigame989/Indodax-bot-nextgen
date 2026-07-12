"""
trader.py
Main trading state machine.

Comments: English
Terminal logs: Indonesian
"""

from __future__ import annotations

import time

from buyer import Buyer
from exchange import ExchangeClient
from history import HistoryEngine
from scanner import MarketScanner
from scoring import AIScoring
from seller import Seller
from storage import StorageManager
from timeout import TimeoutEngine
from validator import BuyValidator


class Trader:
    """Main trading engine."""

    def __init__(self):
        self.storage = StorageManager()
        self.storage.initialize()

        self.exchange = ExchangeClient()
        self.exchange.initialize()

        self.history = HistoryEngine(self.storage)
        self.scanner = MarketScanner(self.exchange)
        self.scoring = AIScoring()
        self.validator = BuyValidator(self.exchange, self.storage)
        self.buyer = Buyer(self.exchange, self.storage, self.history)
        self.seller = Seller(self.exchange, self.storage, self.history)
        self.timeout = TimeoutEngine()

    def scan_and_buy(self):
        """Scan markets and execute BUY."""
        snapshots = self.scanner.scan()

        for snapshot in snapshots:
            try:
                score = self.scoring.calculate(snapshot)
                ok, reason = self.validator.validate(snapshot, score)

                if not ok:
                    print(f"[BUY] {snapshot['symbol']} ditolak ({reason})")
                    continue

                self.buyer.buy(snapshot["symbol"])

            except Exception as err:
                print(f"[ERROR] BUY FLOW {snapshot['symbol']} : {err}")

    def monitor_positions(self):
        """Monitor active trades."""
        active = self.storage.active_trades.load()

        for symbol, layers in list(active.items()):
            ticker = self.exchange.fetch_ticker(symbol)
            last_price = float(ticker["last"])

            for layer in list(layers):
                buy_price = layer["buy_price"]
                profit = ((last_price - buy_price) / buy_price) * 100

                if last_price > layer["highest_price"]:
                    layer["highest_price"] = last_price
                    layer["highest_profit"] = profit

                momentum = {
                    "ema_weak": False,
                    "rsi_weak": False,
                    "volume_weak": False,
                }

                timeout_reason = self.timeout.evaluate(
                    layer,
                    profit,
                    momentum,
                )

                if timeout_reason:
                    self.seller.sell_layer(symbol, layer, timeout_reason)
                    continue

                if profit >= layer["take_profit"]:
                    self.seller.sell_layer(symbol, layer, "TAKE_PROFIT")
                    continue

                if profit > 0:
                    trigger = layer["highest_profit"] - 2.0
                    if profit <= trigger:
                        self.seller.sell_layer(symbol, layer, "TRAILING")

            self.storage.active_trades.save(active)

    def cycle(self):
        """Single trading cycle."""
        print("[INFO] Memulai siklus trading...")
        self.scan_and_buy()
        self.monitor_positions()
        print("[INFO] Siklus trading selesai.")

    def run_forever(self, interval=60):
        """Main loop."""
        print("[INFO] Bot Trading aktif.")

        while True:
            try:
                self.cycle()
            except Exception as err:
                print(f"[ERROR] Trader crash dicegah: {err}")

            time.sleep(interval)
