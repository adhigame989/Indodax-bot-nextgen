"""
sell_strategy.py
Sell decision engine for INDODAX AI Trading Bot.

Comments: English
Terminal logs: Indonesian
"""

from __future__ import annotations

from typing import Dict, Optional

import config
from timeout import TimeoutEngine


class SellStrategy:
    """Determine when a position should be sold."""

    def __init__(self):
        self.timeout = TimeoutEngine()

    def evaluate(
        self,
        layer: Dict,
        current_price: float,
        momentum: Dict,
    ) -> Optional[str]:
        """
        Return sell reason or None.

        Possible results:
        TAKE_PROFIT
        TRAILING
        STOP_LOSS
        EMERGENCY_STOP_LOSS
        TIMEOUT_WEAK
        TIMEOUT_STALE
        TIMEOUT_MAX
        """

        buy_price = float(layer["buy_price"])
        profit = ((current_price - buy_price) / buy_price) * 100

        # Update highest values
        if current_price > layer.get("highest_price", buy_price):
            layer["highest_price"] = current_price
            layer["highest_profit"] = profit

        # Emergency stop loss
        if profit <= config.EMERGENCY_STOP_LOSS:
            print("[SELL] Emergency Stop Loss terpicu.")
            return "EMERGENCY_STOP_LOSS"

        # Smart stop loss (confirmation handled by trader)
        if profit <= layer.get("stop_loss", config.DEFAULT_STOP_LOSS):
            print("[SELL] Stop Loss terpicu.")
            return "STOP_LOSS"

        # Take profit
        if profit >= layer.get("take_profit", config.DEFAULT_TAKE_PROFIT):
            print("[SELL] Take Profit tercapai.")
            return "TAKE_PROFIT"

        # Trailing stop
        highest_profit = layer.get("highest_profit", 0.0)
        if highest_profit > 0:
            trigger = highest_profit - config.TRAILING_GAP
            if profit <= trigger:
                print("[SELL] Trailing Stop terpicu.")
                return "TRAILING"

        # Timeout engine
        timeout_reason = self.timeout.evaluate(
            layer=layer,
            current_profit=profit,
            momentum=momentum,
        )

        if timeout_reason:
            return timeout_reason

        return None
