"""
scanner.py
Market scanner for INDODAX AI Trading Bot.

Comments: English
Terminal logs: Indonesian
"""

from __future__ import annotations

from typing import Dict, List

import config
from exchange import ExchangeClient


class MarketScanner:
    """Scan and filter IDR spot markets."""

    def __init__(self, exchange: ExchangeClient):
        self.exchange = exchange

    def get_idr_pairs(self) -> List[str]:
        """Return tradable IDR pairs."""
        pairs = []

        for symbol, market in self.exchange.markets.items():
            if market.get("quote") != "IDR":
                continue

            if not market.get("active", True):
                continue

            base = market.get("base", "")

            if base in config.EXCLUDED_COINS:
                continue

            pairs.append(symbol)

        print(f"[SCAN] Pair IDR aktif: {len(pairs)}")
        return sorted(pairs)

    def fetch_market_snapshot(self, symbol: str) -> Dict:
        """Collect raw market data."""

        ticker = self.exchange.fetch_ticker(symbol)
        orderbook = self.exchange.fetch_order_book(symbol, 20)

        ohlcv_15m = self.exchange.fetch_ohlcv(
            symbol,
            config.TIMEFRAME_ENTRY,
            200,
        )

        ohlcv_1h = self.exchange.fetch_ohlcv(
            symbol,
            config.TIMEFRAME_H1,
            200,
        )

        ohlcv_4h = self.exchange.fetch_ohlcv(
            symbol,
            config.TIMEFRAME_H4,
            200,
        )

        return {
            "symbol": symbol,
            "ticker": ticker,
            "orderbook": orderbook,
            "15m": ohlcv_15m,
            "1h": ohlcv_1h,
            "4h": ohlcv_4h,
        }

    def scan(self) -> List[Dict]:
        """Scan all supported markets."""

        results = []

        for symbol in self.get_idr_pairs():
            try:
                data = self.fetch_market_snapshot(symbol)

                volume = data["ticker"].get("quoteVolume", 0)

                if volume < config.MIN_VOLUME_IDR:
                    continue

                bid = data["ticker"].get("bid", 0)
                ask = data["ticker"].get("ask", 0)

                if bid <= 0 or ask <= 0:
                    continue

                spread = ((ask - bid) / bid) * 100

                if spread > config.MAX_SPREAD_PERCENT:
                    continue

                data["spread"] = round(spread, 3)
                data["volume"] = volume

                results.append(data)

                print(f"[SCAN] {symbol} | Spread {spread:.2f}% | Volume OK")

            except Exception as err:
                print(f"[ERROR] Scan {symbol} gagal: {err}")

        print(f"[INFO] Scanner selesai. Kandidat: {len(results)}")

        return results
