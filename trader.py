"""
trader.py
State machine integrated with SellStrategy.

Comments: English
Terminal logs: Indonesian
"""

from __future__ import annotations

import time

import config
from buyer import Buyer
from exchange import ExchangeClient
from history import HistoryEngine
from risk import RiskEngine
from scanner import MarketScanner
from scoring import AIScoring
from sell_strategy import SellStrategy
from seller import Seller
from storage import StorageManager
from validator import BuyValidator


class Trader:

    def __init__(self):
        self.storage = StorageManager()
        self.storage.initialize()

        self.exchange = ExchangeClient()
        self.exchange.initialize()

        self.history = HistoryEngine(self.storage)
        self.scanner = MarketScanner(self.exchange)
        self.scoring = AIScoring()
        self.validator = BuyValidator(self.exchange, self.storage)
        self.risk = RiskEngine(self.storage)
        self.strategy = SellStrategy()
        self.buyer = Buyer(self.exchange, self.storage, self.history)
        self.seller = Seller(self.exchange, self.storage, self.history)

    def scan_phase(self):
        return self.scanner.scan()

    def buy_phase(self, snapshots):
        for snap in snapshots:
            score = self.scoring.calculate(snap)
            ok, reason = self.validator.validate(snap, score)
            if not ok:
                continue
            ok, reason = self.risk.validate(snap["symbol"])
            if not ok:
                continue
            self.buyer.buy(snap["symbol"])

    def monitor_phase(self):
        active = self.storage.active_trades.load()

        for symbol, layers in list(active.items()):
            ticker = self.exchange.fetch_ticker(symbol)
            last = float(ticker["last"])

            for layer in list(layers):
                reason = self.strategy.evaluate(
                    layer=layer,
                    current_price=last,
                    momentum={
                        "ema_weak": False,
                        "rsi_weak": False,
                        "volume_weak": False,
                    },
                )

                if reason:
                    self.seller.sell_layer(symbol, layer, reason)

            self.storage.active_trades.save(active)

    def cycle(self):
        print("[STATE] SCAN")
        snapshots = self.scan_phase()

        print("[STATE] BUY")
        self.buy_phase(snapshots)

        print("[STATE] MONITOR")
        self.monitor_phase()

    def run_forever(self):
        while True:
            try:
                self.cycle()
            except Exception as e:
                print(f"[ERROR] {e}")
            time.sleep(config.SCAN_INTERVAL)
