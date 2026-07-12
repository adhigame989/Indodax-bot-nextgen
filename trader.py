"""
trader.py
Production Trading State Machine (Dependency Injection).

Comments: English
Terminal logs: Indonesian
"""

from __future__ import annotations

import time

import config
from logger import info, error


class Trader:
    """Trading orchestrator using dependency injection."""

    def __init__(
        self,
        exchange,
        scanner,
        scoring,
        validator,
        risk,
        buyer,
        seller,
        strategy,
        positions,
        sync_engine,
        recovery_engine,
    ):
        self.exchange = exchange
        self.scanner = scanner
        self.scoring = scoring
        self.validator = validator
        self.risk = risk
        self.buyer = buyer
        self.seller = seller
        self.strategy = strategy
        self.positions = positions
        self.sync = sync_engine
        self.recovery = recovery_engine

    def startup(self):
        info("Recovery startup dimulai.")
        self.recovery.recover()

    def scan_buy_phase(self):
        snapshots = self.scanner.scan()

        for snapshot in snapshots:
            score = self.scoring.calculate(snapshot)

            ok, reason = self.validator.validate(snapshot, score)
            if not ok:
                continue

            ok, reason = self.risk.validate(snapshot["symbol"])
            if not ok:
                continue

            ask = float(snapshot["ticker"]["ask"])
            amount = config.BASE_TRADE_AMOUNT / ask

            self.buyer.execute(snapshot["symbol"], amount)

    def monitor_phase(self):
        for symbol, layers in list(self.positions.all().items()):
            try:
                ticker = self.exchange.fetch_ticker(symbol)
                last_price = float(ticker["last"])

                for layer in list(layers):
                    decision = self.strategy.evaluate(
                        layer=layer,
                        current_price=last_price,
                        momentum={
                            "ema_weak": False,
                            "rsi_weak": False,
                            "volume_weak": False,
                        },
                    )

                    if decision:
                        self.seller.execute(symbol, layer, decision)

            except Exception as exc:
                error(f"Monitor {symbol}: {exc}")

    def cycle(self):
        info("STATE : SCAN")
        self.scan_buy_phase()

        info("STATE : MONITOR")
        self.monitor_phase()

        info("STATE : SYNC")
        self.sync.run()

    def run_forever(self):
        self.startup()

        info("Trading Engine aktif.")

        while True:
            try:
                self.cycle()
            except Exception as exc:
                error(f"Trader Error: {exc}")

            time.sleep(config.SCAN_INTERVAL)
