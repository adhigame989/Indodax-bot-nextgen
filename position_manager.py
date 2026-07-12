"""
position_manager.py
Production Position Manager.

Comments: English
Terminal logs: Indonesian
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict, List, Optional

from logger import info, warning
from storage import StorageManager


class PositionManager:
    """Single access point for active positions."""

    def __init__(self, storage: StorageManager):
        self.storage = storage

    def _load(self) -> Dict:
        data = self.storage.active_trades.load()
        return data if isinstance(data, dict) else {}

    def _save(self, data: Dict):
        self.storage.active_trades.save(data)

    def all(self) -> Dict:
        return self._load()

    def layers(self, symbol: str) -> List[Dict]:
        return self._load().get(symbol, [])

    def get_layer(self, symbol: str, layer_id: str) -> Optional[Dict]:
        for layer in self.layers(symbol):
            if layer.get("layer_id") == layer_id:
                return layer
        return None

    def add_layer(self, symbol: str, layer: Dict):
        active = self._load()
        active.setdefault(symbol, []).append(layer)
        self._save(active)
        info(f"Layer ditambahkan: {symbol}")

    def remove_layer(self, symbol: str, layer_id: str):
        active = self._load()
        if symbol not in active:
            warning(f"Symbol tidak ditemukan: {symbol}")
            return

        active[symbol] = [
            x for x in active[symbol]
            if x.get("layer_id") != layer_id
        ]

        if not active[symbol]:
            del active[symbol]

        self._save(active)
        info(f"Layer dihapus: {symbol}")

    def update_market(self, symbol: str, layer_id: str, price: float):
        active = self._load()

        for layer in active.get(symbol, []):
            if layer.get("layer_id") != layer_id:
                continue

            buy = float(layer["buy_price"])
            profit = ((price - buy) / buy) * 100

            if price > float(layer.get("highest_price", buy)):
                layer["highest_price"] = price
                layer["highest_profit"] = profit

            layer["last_price"] = price
            layer["profit_percent"] = profit
            layer["last_update"] = datetime.now(
                timezone.utc
            ).astimezone().isoformat()

        self._save(active)

    def symbol_count(self) -> int:
        return len(self._load())

    def layer_count(self) -> int:
        return sum(len(v) for v in self._load().values())
