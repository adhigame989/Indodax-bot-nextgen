"""
trader.py
Production Trading State Machine.

Comments: English
Terminal logs: Indonesian
"""

from __future__ import annotations

import time

import config
from buyer import Buyer
from history import HistoryEngine
from logger import error, info
from order_manager import OrderManager
from position_manager import PositionManager
from recovery import RecoveryEngine
from risk import RiskEngine
from scanner import MarketScanner
from scoring import AIScoring
from sell_strategy import SellStrategy
from seller import Seller
from storage import StorageManager
from sync import SyncEngine
from validator import BuyValidator
from exchange import ExchangeClient


class Trader:
    """Main trading orchestrator."""

    def __init__(self):
        storage = StorageManager()
        storage.initialize()

        exchange = ExchangeClient()
        exchange.initialize()

        history = HistoryEngine(storage)
        positions = PositionManager(storage)
        orders = OrderManager(exchange)

        self.exchange = exchange
        self.scanner = MarketScanner(exchange)
        self.scoring = AIScoring()
        self.validator = BuyValidator(exchange, storage)
        self.risk = RiskEngine(storage)
        self.strategy = SellStrategy()

        self.buyer = Buyer(orders, positions, history)
        self.seller = Seller(orders, positions, history)

        self.sync = SyncEngine(exchange, positions, history)
        self.recovery = RecoveryEngine(exchange, positions, history)
        self.positions = positions

    def startup(self):
        info("Recovery startup dimulai.")
        self.recovery.recover()

    def cycle(self):
        snapshots = self.scanner.scan()

        for snap in snapshots:
            score = self.scoring.calculate(snap)

            ok, _ = self.validator.validate(snap, score)
            if not ok:
                continue

            ok, _ = self.risk.validate(snap["symbol"])
            if not ok:
                continue

            ask = float(snap["ticker"]["ask"])
            amount = config.BASE_TRADE_AMOUNT / ask
            self.buyer.execute(snap["symbol"], amount)

        for symbol, layers in self.positions.all().items():
            ticker = self.exchange.fetch_ticker(symbol)
            price = float(ticker["last"])

            for layer in list(layers):
                reason = self.strategy.evaluate(
                    layer=layer,
                    current_price=price,
                    momentum={
                        "ema_weak": False,
                        "rsi_weak": False,
                        "volume_weak": False,
                    },
                )
                if reason:
                    self.seller.execute(symbol, layer, reason)

        self.sync.sync()

    def run_forever(self):
        self.startup()
        info("Trading Engine aktif.")

        while True:
            try:
                self.cycle()
            except Exception as exc:
                error(f"Trader error: {exc}")

            time.sleep(config.SCAN_INTERVAL)
