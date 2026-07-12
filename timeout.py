"""
timeout.py
Timeout engine for INDODAX AI Trading Bot.

Comments: English
Terminal logs: Indonesian
"""

from __future__ import annotations

from datetime import datetime, timezone
from typing import Dict, Optional

import config


class TimeoutEngine:
    """Evaluate timeout exit conditions."""

    def _hours_held(self, buy_time: str) -> float:
        start = datetime.fromisoformat(buy_time)
        now = datetime.now(timezone.utc).astimezone()
        return (now - start).total_seconds() / 3600

    def _weak_momentum(self, signal: Dict) -> bool:
        score = 0

        if signal.get("ema_weak", False):
            score += 1

        if signal.get("rsi_weak", False):
            score += 1

        if signal.get("volume_weak", False):
            score += 1

        return score >= 2

    def evaluate(
        self,
        layer: Dict,
        current_profit: float,
        momentum: Dict,
    ) -> Optional[str]:
        """
        Return:
        - TIMEOUT_WEAK
        - TIMEOUT_STALE
        - TIMEOUT_MAX
        - None
        """

        hold_hours = self._hours_held(layer["buy_time"])

        if hold_hours >= config.TIMEOUT_MAX_HOURS:
            print("[TIMEOUT] Timeout Max terpicu.")
            return "TIMEOUT_MAX"

        if (
            hold_hours >= config.TIMEOUT_STALE_HOURS
            and current_profit < 3
            and self._weak_momentum(momentum)
        ):
            print("[TIMEOUT] Timeout Stale terpicu.")
            return "TIMEOUT_STALE"

        if (
            hold_hours >= config.TIMEOUT_WEAK_HOURS
            and current_profit < 1
            and self._weak_momentum(momentum)
        ):
            print("[TIMEOUT] Timeout Weak terpicu.")
            return "TIMEOUT_WEAK"

        return None
