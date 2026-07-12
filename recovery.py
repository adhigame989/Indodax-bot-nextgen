"""
recovery.py
Recovery engine for INDODAX AI Trading Bot.

Comments: English
Terminal logs: Indonesian
"""

from __future__ import annotations

from exchange import ExchangeClient
from history import HistoryEngine
from position_manager import PositionManager


class RecoveryEngine:
    """Recover local state after restart."""

    def __init__(
        self,
        exchange: ExchangeClient,
        positions: PositionManager,
        history: HistoryEngine,
    ):
        self.exchange = exchange
        self.positions = positions
        self.history = history

    def recover(self):
        print("[RECOVERY] Memulai proses recovery...")

        active = self.positions.load()
        balance = self.exchange.safe_balance()

        recovered = 0
        removed = 0

        for symbol, layers in list(active.items()):
            base = symbol.split("/")[0]
            asset = float(balance.get(base, {}).get("free", 0))

            if asset <= 0:
                print(f"[RECOVERY] Menghapus posisi tidak valid: {symbol}")

                for layer in list(layers):
                    self.history.record(
                        symbol=symbol,
                        side="SELL",
                        reason="RECOVERY_REMOVE",
                        price=0,
                        amount=layer.get("amount", 0),
                        trade_id=layer.get("trade_id"),
                        layer_id=layer.get("layer_id"),
                        note="Removed during recovery",
                    )
                    self.positions.remove_layer(symbol, layer["layer_id"])
                    removed += 1
                continue

            try:
                ticker = self.exchange.fetch_ticker(symbol)
                last_price = float(ticker["last"])

                for layer in layers:
                    self.positions.update_price(
                        symbol=symbol,
                        layer_id=layer["layer_id"],
                        current_price=last_price,
                    )
                    recovered += 1

            except Exception as err:
                print(f"[WARNING] Recovery {symbol} gagal: {err}")

        print(f"[RECOVERY] Selesai | Recovered={recovered} Removed={removed}")
