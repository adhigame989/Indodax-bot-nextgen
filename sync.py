"""
sync.py
Exchange synchronization engine.

Comments: English
Terminal logs: Indonesian
"""

from __future__ import annotations

from typing import Dict

from exchange import ExchangeClient
from history import HistoryEngine
from position_manager import PositionManager


class SyncEngine:
    """Synchronize local positions with exchange."""

    def __init__(
        self,
        exchange: ExchangeClient,
        positions: PositionManager,
        history: HistoryEngine,
    ):
        self.exchange = exchange
        self.positions = positions
        self.history = history

    def sync(self):
        """Run one synchronization cycle."""
        active = self.positions.load()
        balance = self.exchange.safe_balance()

        for symbol, layers in list(active.items()):
            base = symbol.split("/")[0]
            asset = float(balance.get(base, {}).get("free", 0))

            if asset <= 0:
                print(f"[SYNC] Manual SELL terdeteksi: {symbol}")

                for layer in layers:
                    self.history.record(
                        symbol=symbol,
                        side="SELL",
                        reason="MANUAL_SELL",
                        price=0,
                        amount=layer.get("amount", 0),
                        trade_id=layer.get("trade_id"),
                        layer_id=layer.get("layer_id"),
                        note="Detected by Sync Engine",
                    )

                    self.positions.remove_layer(
                        symbol,
                        layer["layer_id"],
                    )

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

            except Exception as err:
                print(f"[WARNING] Sinkronisasi {symbol} gagal: {err}")

        print("[SYNC] Sinkronisasi selesai.")
