"""
validator.py
Production BUY validation engine.
"""

from __future__ import annotations
from typing import Dict, Tuple

import config
from exchange import ExchangeClient
from logger import info
from position_manager import PositionManager

class BuyValidator:
    def __init__(self, exchange: ExchangeClient, positions: PositionManager):
        self.exchange = exchange
        self.positions = positions

    def validate(self, snapshot: Dict, ai_score: Dict) -> Tuple[bool, str]:
        symbol = snapshot["symbol"]
        if not ai_score.get("eligible_buy", False):
            return False, "AI_SCORE"
        if snapshot.get("spread", 999) > config.MAX_SPREAD_PERCENT:
            return False, "SPREAD"
        if snapshot.get("volume", 0) < config.MIN_VOLUME_IDR:
            return False, "VOLUME"
        idr = float(self.exchange.safe_balance().get("IDR", {}).get("free", 0))
        if idr < config.BASE_TRADE_AMOUNT:
            return False, "BALANCE"
        if len(self.positions.layers(symbol)) >= config.MAX_LAYER_PER_COIN:
            return False, "MAX_LAYER"
        if self.positions.layer_count() >= config.MAX_ACTIVE_TRADES:
            return False, "MAX_ACTIVE"
        ticker=self.exchange.fetch_ticker(symbol)
        ask=float(ticker["ask"])
        amount=float(self.exchange.amount_precision(symbol, config.BASE_TRADE_AMOUNT/ask))
        if amount < self.exchange.minimum_amount(symbol):
            return False,"MIN_AMOUNT"
        if amount*ask < self.exchange.minimum_cost(symbol):
            return False,"MIN_COST"
        ob=snapshot.get("orderbook",{})
        bids=ob.get("bids",[])
        asks=ob.get("asks",[])
        if len(bids)<5 or len(asks)<5:
            return False,"ORDERBOOK"
        slip=((float(asks[0][0])-float(bids[0][0]))/float(bids[0][0]))*100
        if slip>config.MAX_SPREAD_PERCENT:
            return False,"SLIPPAGE"
        info(f"Validator OK : {symbol}")
        return True,"OK"
