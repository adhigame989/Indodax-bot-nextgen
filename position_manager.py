"""
position_manager.py
Position manager for INDODAX AI Trading Bot.

Comments: English
Terminal logs: Indonesian
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict, List

from storage import StorageManager


class PositionManager:
    """Manage active positions and layers."""

    def __init__(self, storage: StorageManager):
        self.storage = storage

    def load(self) -> Dict:
        data = self.storage.active_trades.load()
        return data if isinstance(data, dict) else {}

    def save(self, data: Dict):
        self.storage.active_trades.save(data)

    def get_layers(self, symbol: str) -> List[Dict]:
        return self.load().get(symbol, [])

    def add_layer(self, symbol: str, layer: Dict):
        active = self.load()
        active.setdefault(symbol, []).append(layer)
        self.save(active)
        print(f"[POSITION] Layer ditambahkan: {symbol}")

    def remove_layer(self, symbol: str, layer_id: str):
        active = self.load()
        if symbol not in active:
            return

        active[symbol] = [
            x for x in active[symbol]
            if x.get("layer_id") != layer_id
        ]

        if not active[symbol]:
            del active[symbol]

        self.save(active)
        print(f"[POSITION] Layer dihapus: {symbol}")

    def update_price(self, symbol: str, layer_id: str, current_price: float):
        active = self.load()

        for layer in active.get(symbol, []):
            if layer.get("layer_id") != layer_id:
                continue

            buy = float(layer["buy_price"])
            profit = ((current_price - buy) / buy) * 100

            if current_price > layer.get("highest_price", buy):
                layer["highest_price"] = current_price
                layer["highest_profit"] = profit

            layer["last_price"] = current_price
            layer["last_update"] = datetime.now(
                timezone.utc
            ).astimezone().isoformat()

        self.save(active)

    def total_layers(self) -> int:
        return sum(len(v) for v in self.load().values())

    def total_symbols(self) -> int:
        return len(self.load())
