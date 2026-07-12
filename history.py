"""
history.py
History engine for INDODAX AI Trading Bot.

Comments: English
Terminal logs: Indonesian
"""

from __future__ import annotations

from datetime import datetime, timezone
from uuid import uuid4
from typing import Optional

from storage import StorageManager


class HistoryEngine:
    """Append-only trade history manager."""

    def __init__(self, storage: StorageManager):
        self.storage = storage

    def record(
        self,
        symbol: str,
        side: str,
        reason: str,
        price: float,
        amount: float,
        profit_percent: float = 0.0,
        profit_idr: float = 0.0,
        hold_seconds: int = 0,
        trade_id: Optional[str] = None,
        layer_id: Optional[str] = None,
        note: str = "",
    ) -> str:
        """Append a history record."""

        trade_id = trade_id or str(uuid4())
        layer_id = layer_id or str(uuid4())

        record = {
            "trade_id": trade_id,
            "layer_id": layer_id,
            "timestamp": datetime.now(timezone.utc).astimezone().isoformat(),
            "symbol": symbol,
            "side": side.upper(),
            "reason": reason.upper(),
            "price": round(price, 8),
            "amount": round(amount, 8),
            "profit_percent": round(profit_percent, 2),
            "profit_idr": round(profit_idr, 2),
            "hold_seconds": hold_seconds,
            "note": note,
        }

        def append(data):
            if not isinstance(data, list):
                data = []
            data.append(record)
            return data

        history = self.storage.history.load()
        if not isinstance(history, list):
            history = []
        history.append(record)
        self.storage.history.save(history)

        print(f"[HISTORY] {symbol} | {side.upper()} | {reason.upper()} berhasil disimpan.")

        return trade_id

    def all(self):
        """Return all history."""
        return self.storage.history.load()

    def last(self, limit: int = 20):
        """Return latest history."""
        history = self.storage.history.load()
        if not isinstance(history, list):
            return []
        return history[-limit:]
