"""
trader.py
Production Trading Engine (Scheduler Ready)
"""

from logger import info,error
import config

class Trader:
    def __init__(self,exchange,scanner,scoring,validator,risk,buyer,seller,
                 strategy,positions,sync_engine,recovery_engine):
        self.exchange=exchange
        self.scanner=scanner
        self.scoring=scoring
        self.validator=validator
        self.risk=risk
        self.buyer=buyer
        self.seller=seller
        self.strategy=strategy
        self.positions=positions
        self.sync=sync_engine
        self.recovery=recovery_engine
        self.running=True

    def startup(self):
        info("Recovery startup dimulai.")
        self.recovery.recover()

    def start(self):
        self.running=True
        info("Trading Engine START")

    def stop(self):
        self.running=False
        info("Trading Engine STOP")

    def scan_phase(self):
        for snap in self.scanner.scan():
            score=self.scoring.calculate(snap)
            ok,_=self.validator.validate(snap,score)
            if not ok: continue
            ok,_=self.risk.validate(snap["symbol"])
            if not ok: continue
            ask=float(snap["ticker"]["ask"])
            amount=config.BASE_TRADE_AMOUNT/ask
            self.buyer.execute(snap["symbol"],amount)

    def monitor_phase(self):
        for symbol,layers in self.positions.all().items():
            try:
                price=float(self.exchange.fetch_ticker(symbol)["last"])
                for layer in list(layers):
                    reason=self.strategy.evaluate(
                        layer=layer,
                        current_price=price,
                        momentum={"ema_weak":False,"rsi_weak":False,"volume_weak":False}
                    )
                    if reason:
                        self.seller.execute(symbol,layer,reason)
            except Exception as exc:
                error(f"{symbol}: {exc}")

    def cycle(self):
        if not self.running:
            return
        try:
            self.scan_phase()
            self.monitor_phase()
            self.sync.run()
        except Exception as exc:
            error(f"Cycle error: {exc}")
