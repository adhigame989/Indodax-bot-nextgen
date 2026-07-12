"""
scoring.py
AI scoring engine for INDODAX AI Trading Bot.

Comments: English
Terminal logs: Indonesian
"""

from __future__ import annotations

from typing import Dict

class AIScoring:
    """Rule-based AI scoring engine."""

    WEIGHTS = {
        "ema": 20,
        "macd": 15,
        "rsi": 15,
        "atr": 10,
        "volume": 10,
        "breakout": 10,
        "momentum": 10,
        "trend_h1": 5,
        "trend_h4": 5,
    }

    def _score_ema(self, data: Dict) -> int:
        return self.WEIGHTS["ema"] if data.get("ema20",0) > data.get("ema50",0) else 0

    def _score_macd(self, data: Dict) -> int:
        return self.WEIGHTS["macd"] if data.get("macd",0) > data.get("macd_signal",0) else 0

    def _score_rsi(self, data: Dict) -> int:
        rsi = data.get("rsi",50)
        return self.WEIGHTS["rsi"] if 50 <= rsi <= 70 else 0

    def _score_atr(self, data: Dict) -> int:
        return self.WEIGHTS["atr"] if data.get("atr",0) > 0 else 0

    def _score_volume(self, data: Dict) -> int:
        return self.WEIGHTS["volume"] if data.get("volume_spike",False) else 0

    def _score_breakout(self, data: Dict) -> int:
        return self.WEIGHTS["breakout"] if data.get("breakout",False) else 0

    def _score_momentum(self, data: Dict) -> int:
        return self.WEIGHTS["momentum"] if data.get("momentum",False) else 0

    def _score_trend(self, data: Dict) -> int:
        score = 0
        if data.get("trend_h1") == "bullish":
            score += self.WEIGHTS["trend_h1"]
        if data.get("trend_h4") == "bullish":
            score += self.WEIGHTS["trend_h4"]
        return score

    def calculate(self, data: Dict) -> Dict:
        """Calculate normalized AI score."""
        raw = (
            self._score_ema(data)
            + self._score_macd(data)
            + self._score_rsi(data)
            + self._score_atr(data)
            + self._score_volume(data)
            + self._score_breakout(data)
            + self._score_momentum(data)
            + self._score_trend(data)
        )

        max_score = sum(self.WEIGHTS.values())
        normalized = round((raw / max_score) * 100, 2)

        result = {
            "score": normalized,
            "raw_score": raw,
            "max_score": max_score,
            "eligible_buy": normalized >= 80,
        }

        print(f"[SCAN] AI Score: {normalized}/100")
        return result
