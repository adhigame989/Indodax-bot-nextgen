"""
indicator.py
Technical indicator engine for INDODAX AI Trading Bot.

Comments: English
Terminal logs: Indonesian
"""

from __future__ import annotations

from typing import Dict, List


class IndicatorEngine:
    """Pure-Python technical indicator calculator."""

    @staticmethod
    def _ema(values: List[float], period: int) -> float:
        if len(values) < period:
            return values[-1] if values else 0.0

        k = 2 / (period + 1)
        ema = sum(values[:period]) / period

        for price in values[period:]:
            ema = (price * k) + (ema * (1 - k))

        return ema

    @staticmethod
    def _rsi(values: List[float], period: int = 14) -> float:
        if len(values) < period + 1:
            return 50.0

        gains = []
        losses = []

        for i in range(1, period + 1):
            diff = values[-period - 1 + i] - values[-period - 2 + i]
            if diff >= 0:
                gains.append(diff)
                losses.append(0)
            else:
                gains.append(0)
                losses.append(abs(diff))

        avg_gain = sum(gains) / period
        avg_loss = sum(losses) / period

        if avg_loss == 0:
            return 100.0

        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))

    @staticmethod
    def _atr(candles: List[List[float]], period: int = 14) -> float:
        if len(candles) < period + 1:
            return 0.0

        tr_values = []

        for i in range(-period, 0):
            high = candles[i][2]
            low = candles[i][3]
            prev_close = candles[i - 1][4]

            tr = max(
                high - low,
                abs(high - prev_close),
                abs(low - prev_close),
            )

            tr_values.append(tr)

        return sum(tr_values) / period

    @staticmethod
    def _macd(values: List[float]):
        ema12 = IndicatorEngine._ema(values, 12)
        ema26 = IndicatorEngine._ema(values, 26)
        macd = ema12 - ema26
        signal = macd
        return macd, signal

    @staticmethod
    def analyze(ohlcv: List[List[float]]) -> Dict:
        closes = [c[4] for c in ohlcv]
        volumes = [c[5] for c in ohlcv]

        ema20 = IndicatorEngine._ema(closes, 20)
        ema50 = IndicatorEngine._ema(closes, 50)

        rsi = IndicatorEngine._rsi(closes)
        atr = IndicatorEngine._atr(ohlcv)

        macd, signal = IndicatorEngine._macd(closes)

        avg_volume = (
            sum(volumes[-20:]) / min(20, len(volumes))
            if volumes else 0
        )

        volume_spike = (
            volumes[-1] > avg_volume * 1.5
            if volumes else False
        )

        breakout = (
            closes[-1] > max(closes[-20:-1])
            if len(closes) >= 20 else False
        )

        momentum = (
            ema20 > ema50
            and macd > signal
            and rsi > 55
        )

        return {
            "ema20": round(ema20, 8),
            "ema50": round(ema50, 8),
            "rsi": round(rsi, 2),
            "atr": round(atr, 8),
            "macd": round(macd, 8),
            "macd_signal": round(signal, 8),
            "volume_spike": volume_spike,
            "breakout": breakout,
            "momentum": momentum,
        }
