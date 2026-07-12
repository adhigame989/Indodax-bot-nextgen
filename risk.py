"""
risk.py
Production Risk Engine.

Comments: English
Terminal logs: Indonesian
"""

from __future__ import annotations

from datetime import datetime

import config
from logger import info
from history import HistoryEngine
from position_manager import PositionManager


class RiskEngine:
    """Portfolio risk validation."""

    def __init__(self, positions: PositionManager, history: HistoryEngine):
        self.positions = positions
        self.history = history

    def _today_stats(self):
        history = self.history.storage.history.load()
        today = datetime.now().date()
        trades = 0
        pnl = 0.0

        if isinstance(history, list):
            for row in history:
                try:
                    if row.get("side") != "SELL":
                        continue
                    if datetime.fromisoformat(row["timestamp"]).date() != today:
                        continue
                    trades += 1
                    pnl += float(row.get("profit_percent", 0))
                except Exception:
                    continue

        return trades, pnl

    def validate(self, symbol: str):
        if len(self.positions.layers(symbol)) >= config.MAX_LAYER_PER_COIN:
            return False, "MAX_LAYER"

        if self.positions.layer_count() >= config.MAX_ACTIVE_TRADES:
            return False, "MAX_ACTIVE"

        trades, pnl = self._today_stats()

        if trades >= config.MAX_TRADE_PER_DAY:
            return False, "MAX_TRADE_DAY"

        if pnl <= -abs(config.MAX_DAILY_LOSS_PERCENT):
            return False, "MAX_DAILY_LOSS"

        info(f"Risk OK : {symbol}")
        return True, "OK"

    def position_multiplier(self, score: float) -> float:
        if score >= 95:
            return 1.00
        if score >= 90:
            return 0.80
        if score >= 85:
            return 0.60
        return 0.50
