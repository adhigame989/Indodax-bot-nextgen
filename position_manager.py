"""
position_manager.py
Production Position Manager V3 (Thread Safe)

Comments: English
Terminal logs: Indonesian
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from threading import RLock
from typing import Dict, List, Optional

from logger import info, warning
from storage import StorageManager


class PositionManager:
    """Thread-safe manager for active positions."""

    def __init__(self, storage: StorageManager):
        self.storage = storage
        self._lock = RLock()

    def _load(self) -> Dict:
        data = self.storage.active_trades.load()
        return data if isinstance(data, dict) else {}

    def _save(self, data: Dict):
        self.storage.active_trades.save(data)

    def snapshot(self) -> Dict:
        with self._lock:
            return deepcopy(self._load())

    def all(self) -> Dict:
        return self.snapshot()

    def layers(self, symbol: str) -> List[Dict]:
        with self._lock:
            return deepcopy(self._load().get(symbol, []))

    def get_layer(self, symbol: str, layer_id: str) -> Optional[Dict]:
        for layer in self.layers(symbol):
            if layer.get("layer_id") == layer_id:
                return layer
        return None

    def exists(self, symbol: str, layer_id: str) -> bool:
        return self.get_layer(symbol, layer_id) is not None

    def add_layer(self, symbol: str, layer: Dict):
        with self._lock:
            active = self._load()
            active.setdefault(symbol, []).append(layer)
            self._save(active)
        info(f"Layer ditambahkan: {symbol}")

    def remove_layer(self, symbol: str, layer_id: str):
        with self._lock:
            active = self._load()
            if symbol not in active:
                warning(f"Symbol tidak ditemukan: {symbol}")
                return
            active[symbol] = [x for x in active[symbol] if x.get("layer_id") != layer_id]
            if not active[symbol]:
                del active[symbol]
            self._save(active)
        info(f"Layer dihapus: {symbol}")

    def replace_layer(self, symbol: str, layer: Dict):
        with self._lock:
            active = self._load()
            rows = active.get(symbol, [])
            for i, old in enumerate(rows):
                if old.get("layer_id") == layer.get("layer_id"):
                    rows[i] = layer
                    break
            self._save(active)

    def update_market(self, symbol: str, layer_id: str, price: float):
        with self._lock:
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
                layer["last_update"] = datetime.now(timezone.utc).astimezone().isoformat()
            self._save(active)

    def symbol_count(self) -> int:
        return len(self.snapshot())

    def layer_count(self) -> int:
        return sum(len(v) for v in self.snapshot().values())
