"""
risk.py
Risk management engine for INDODAX AI Trading Bot.

Comments: English
Terminal logs: Indonesian
"""

from __future__ import annotations

from datetime import datetime
from typing import Dict

import config
from storage import StorageManager


class RiskEngine:
    """Evaluate portfolio risk before BUY."""

    def __init__(self, storage: StorageManager):
        self.storage = storage

    def _active_layer_count(self) -> int:
        active = self.storage.active_trades.load()
        if not isinstance(active, dict):
            return 0
        return sum(len(v) for v in active.values())

    def _daily_stats(self):
        history = self.storage.history.load()
        today = datetime.now().date()

        trades = 0
        pnl = 0.0

        if isinstance(history, list):
            for row in history:
                try:
                    if row.get("side") != "SELL":
                        continue

                    ts = datetime.fromisoformat(row["timestamp"]).date()
                    if ts != today:
                        continue

                    trades += 1
                    pnl += float(row.get("profit_percent", 0))
                except Exception:
                    continue

        return trades, pnl

    def validate(self, symbol: str) -> tuple[bool, str]:
        """Validate portfolio level risk."""

        active = self.storage.active_trades.load()
        layers = active.get(symbol, []) if isinstance(active, dict) else []

        if len(layers) >= config.MAX_LAYER_PER_COIN:
            return False, "MAX_LAYER_PER_COIN"

        if self._active_layer_count() >= config.MAX_ACTIVE_TRADES:
            return False, "MAX_ACTIVE_TRADES"

        trades_today, pnl_today = self._daily_stats()

        if trades_today >= config.MAX_TRADE_PER_DAY:
            return False, "MAX_TRADE_PER_DAY"

        if pnl_today <= -abs(config.MAX_DAILY_LOSS_PERCENT):
            return False, "MAX_DAILY_LOSS"

        print("[RISK] Validasi risiko berhasil.")
        return True, "OK"

    def position_size(self, ai_score: float) -> float:
        """Return position size multiplier based on AI score."""

        if ai_score >= 95:
            return 1.00

        if ai_score >= 90:
            return 0.80

        if ai_score >= 85:
            return 0.60

        return 0.50
