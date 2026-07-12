"""
indicator.py
Production Technical Indicator Engine.

Comments: English
Terminal logs: Indonesian
"""

from __future__ import annotations

from typing import Dict, List


class IndicatorEngine:

    @staticmethod
    def ema(values: List[float], period: int) -> float:
        if len(values) < period:
            return values[-1] if values else 0.0
        k = 2 / (period + 1)
        value = sum(values[:period]) / period
        for price in values[period:]:
            value = (price - value) * k + value
        return value

    @staticmethod
    def rsi(values: List[float], period: int = 14) -> float:
        if len(values) <= period:
            return 50.0
        gains, losses = [], []
        for i in range(1, period + 1):
            diff = values[-period - 1 + i] - values[-period - 2 + i]
            gains.append(max(diff, 0))
            losses.append(max(-diff, 0))
        avg_gain = sum(gains) / period
        avg_loss = sum(losses) / period
        for i in range(len(values) - period, len(values) - 1):
            diff = values[i + 1] - values[i]
            gain = max(diff, 0)
            loss = max(-diff, 0)
            avg_gain = ((avg_gain * (period - 1)) + gain) / period
            avg_loss = ((avg_loss * (period - 1)) + loss) / period
        if avg_loss == 0:
            return 100.0
        rs = avg_gain / avg_loss
        return 100 - (100 / (1 + rs))

    @staticmethod
    def atr(candles: List[List[float]], period: int = 14) -> float:
        if len(candles) <= period:
            return 0.0
        tr = []
        for i in range(1, len(candles)):
            h, l, pc = candles[i][2], candles[i][3], candles[i-1][4]
            tr.append(max(h-l, abs(h-pc), abs(l-pc)))
        atr = sum(tr[:period]) / period
        for x in tr[period:]:
            atr = ((atr * (period-1)) + x) / period
        return atr

    @classmethod
    def macd(cls, values: List[float]):
        if len(values) < 35:
            return 0.0, 0.0, 0.0
        macd_series = []
        for i in range(26, len(values)):
            part = values[:i+1]
            macd_series.append(cls.ema(part,12)-cls.ema(part,26))
        signal = cls.ema(macd_series,9)
        macd = macd_series[-1]
        hist = macd - signal
        return macd, signal, hist

    @staticmethod
    def volume_spike(volumes: List[float], period: int = 20) -> bool:
        if len(volumes) < period:
            return False
        avg = sum(volumes[-period:-1])/(period-1)
        return volumes[-1] > avg * 1.5

    @staticmethod
    def breakout(closes: List[float], period: int = 20) -> bool:
        if len(closes) < period:
            return False
        return closes[-1] > max(closes[-period:-1])

    @classmethod
    def analyze(cls, ohlcv: List[List[float]]) -> Dict:
        closes = [c[4] for c in ohlcv]
        volumes = [c[5] for c in ohlcv]
        ema20 = cls.ema(closes,20)
        ema50 = cls.ema(closes,50)
        macd, signal, hist = cls.macd(closes)
        rsi = cls.rsi(closes)
        atr = cls.atr(ohlcv)
        return {
            "ema20": round(ema20,8),
            "ema50": round(ema50,8),
            "rsi": round(rsi,2),
            "atr": round(atr,8),
            "macd": round(macd,8),
            "macd_signal": round(signal,8),
            "macd_histogram": round(hist,8),
            "volume_spike": cls.volume_spike(volumes),
            "breakout": cls.breakout(closes),
            "momentum": ema20>ema50 and macd>signal and rsi>55,
        }
