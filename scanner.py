"""
scanner.py
Market scanner integrated with Indicator Engine.
"""

from __future__ import annotations

from typing import Dict, List

import config
from exchange import ExchangeClient
from indicator import IndicatorEngine


class MarketScanner:

    def __init__(self, exchange: ExchangeClient):
        self.exchange = exchange

    def _valid_market(self, market: Dict) -> bool:
        return (
            market.get("quote") == "IDR"
            and market.get("active", True)
            and market.get("base") not in config.EXCLUDED_COINS
        )

    def scan(self) -> List[Dict]:
        results = []

        for symbol, market in self.exchange.markets.items():
            if not self._valid_market(market):
                continue

            try:
                ticker = self.exchange.fetch_ticker(symbol)

                volume = float(ticker.get("quoteVolume", 0) or 0)
                if volume < config.MIN_VOLUME_IDR:
                    continue

                bid = float(ticker.get("bid", 0) or 0)
                ask = float(ticker.get("ask", 0) or 0)
                if bid <= 0 or ask <= 0:
                    continue

                spread = ((ask - bid) / bid) * 100
                if spread > config.MAX_SPREAD_PERCENT:
                    continue

                tf15 = self.exchange.fetch_ohlcv(symbol, config.TIMEFRAME_ENTRY, 200)
                tf1h = self.exchange.fetch_ohlcv(symbol, config.TIMEFRAME_H1, 200)
                tf4h = self.exchange.fetch_ohlcv(symbol, config.TIMEFRAME_H4, 200)

                ind15 = IndicatorEngine.analyze(tf15)
                ind1 = IndicatorEngine.analyze(tf1h)
                ind4 = IndicatorEngine.analyze(tf4h)

                results.append({
                    "symbol": symbol,
                    "ticker": ticker,
                    "orderbook": self.exchange.fetch_order_book(symbol, 20),
                    "spread": round(spread,3),
                    "volume": volume,
                    **ind15,
                    "trend_h1": "bullish" if ind1["ema20"] > ind1["ema50"] else "bearish",
                    "trend_h4": "bullish" if ind4["ema20"] > ind4["ema50"] else "bearish",
                })

                print(f"[SCAN] {symbol} siap diproses.")

            except Exception as e:
                print(f"[ERROR] Scanner {symbol}: {e}")

        print(f"[INFO] Scanner selesai. Kandidat: {len(results)}")
        return results
