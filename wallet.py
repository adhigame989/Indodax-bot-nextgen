# wallet.py
# INDODAX AI BOT
# Wallet Service V1

import time
import threading

CACHE = {
    "last_update": 0,
    "idr_balance": 0.0,
    "coins": {},
    "total_asset": 0.0,
    "online": False
}


class WalletService:

    def __init__(self, exchange):
        self.exchange = exchange
        self.lock = threading.Lock()

    def refresh(self):
        try:
            info = self.exchange.safe_balance() or {}

            raw = info.get("info", {}).get("return", {})
            balance = raw.get("balance", {})

            with self.lock:
                CACHE["last_update"] = time.time()
                CACHE["online"] = True

                CACHE["idr_balance"] = float(balance.get("idr", 0))

                CACHE["coins"] = {}

                total = CACHE["idr_balance"]

                for coin, amount in balance.items():
                    try:
                        amount = float(amount)
                    except Exception:
                        continue

                    if amount <= 0:
                        continue

                    CACHE["coins"][coin.upper()] = amount

                CACHE["total_asset"] = total
                    except Exception as e:
            print("[Wallet]", e)

            with self.lock:
                CACHE["online"] = False

    def get_idr(self):
        return CACHE["idr_balance"]

    def get_total_asset(self):
        return CACHE["total_asset"]

    def get_assets(self):
        return CACHE["coins"]

    def is_online(self):
        return CACHE["online"]

    def last_update(self):
        return CACHE["last_update"]


wallet = None


def init_wallet(exchange):
    global wallet

    wallet = WalletService(exchange)

    wallet.refresh()

    return wallet


def get_wallet():
    return wallet
