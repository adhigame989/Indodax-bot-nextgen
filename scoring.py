"""
scoring.py
AI Scoring Engine V2.
"""

from __future__ import annotations
from typing import Dict


class AIScoring:
    """Weighted AI scoring."""

    def calculate(self, data: Dict) -> Dict:
        score = 0

        # EMA Trend
        if data["ema20"] > data["ema50"]:
            score += 20
            gap = ((data["ema20"]-data["ema50"]) / data["ema50"]) * 100
            if gap > 1:
                score += 5

        # RSI
        rsi = data["rsi"]
        if 55 <= rsi <= 68:
            score += 15
        elif 50 <= rsi < 55:
            score += 8
        elif rsi > 75:
            score -= 5

        # MACD
        if data["macd"] > data["macd_signal"]:
            score += 15
        if data.get("macd_histogram", 0) > 0:
            score += 5

        # ATR
        if data["atr"] > 0:
            score += 5

        # Volume
        if data["volume_spike"]:
            score += 10

        # Breakout
        if data["breakout"]:
            score += 10

        # Momentum
        if data["momentum"]:
            score += 10

        # Multi-timeframe trend
        if data["trend_h1"] == "bullish":
            score += 10
        if data["trend_h4"] == "bullish":
            score += 10

        # Spread penalty
        spread = data.get("spread", 99)
        if spread <= 0.5:
            score += 5
        elif spread > 1.5:
            score -= 10

        score = max(0, min(score, 100))

        if score >= 90:
            grade = "A+"
        elif score >= 80:
            grade = "A"
        elif score >= 70:
            grade = "B"
        elif score >= 60:
            grade = "C"
        else:
            grade = "D"

        eligible = score >= 80

        print(f"[AI] Score={score} Grade={grade}")

        return {
            "score": score,
            "grade": grade,
            "eligible_buy": eligible
        }
