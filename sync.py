"""
sync.py
Production Synchronization Engine V3.

Features:
- Order-aware synchronization
- Manual sell detection
- Partial-fill handling
- Position refresh
"""

from __future__ import annotations

from logger import info, warning, error
from exchange import ExchangeClient
from order_manager import OrderManager
from position_manager import PositionManager
from history import HistoryEngine


class SyncEngine:

    def __init__(self,
                 exchange: ExchangeClient,
                 orders: OrderManager,
                 positions: PositionManager,
                 history: HistoryEngine):
        self.exchange = exchange
        self.orders = orders
        self.positions = positions
        self.history = history

    def run(self):
        info("SYNC dimulai")

        try:
            balance = self.exchange.safe_balance()
        except Exception as exc:
            error(f"Gagal mengambil balance: {exc}")
            return

        for symbol, layers in list(self.positions.all().items()):

            try:
                ticker = self.exchange.fetch_ticker(symbol)
                last_price = float(ticker["last"])
            except Exception as exc:
                warning(f"{symbol} ticker gagal: {exc}")
                continue

            asset = symbol.split("/")[0]
            free_asset = float(balance.get(asset, {}).get("free", 0))

            for layer in list(layers):

                # Refresh market values
                self.positions.update_market(
                    symbol,
                    layer["layer_id"],
                    last_price
                )

                order_id = layer.get("order_id")
                if order_id:
                    order = self.orders.sync(order_id, symbol)
                    if order:
                        status = str(order.get("status", "")).lower()
                        layer["last_order_status"] = status

                        # Pending order -> don't touch position
                        if status in ("open", "pending"):
                            continue

                        # Partial fill
                        filled = float(order.get("filled") or 0)
                        amount = float(layer["amount"])

                        if 0 < filled < amount:
                            layer["amount"] = filled
                            warning(
                                f"{symbol} partial fill "
                                f"{filled:.8f}/{amount:.8f}"
                            )
                            continue

                # Manual sell detection
                if free_asset <= 0:
                    try:
                        trades = self.exchange.fetch_my_trades(symbol)
                    except Exception:
                        trades = []

                    reason = "MANUAL_SELL"

                    if trades:
                        latest = trades[-1]
                        if str(latest.get("side", "")).lower() == "sell":
                            reason = "SYNC_SELL"

                    self.history.record(
                        symbol=symbol,
                        side="SELL",
                        reason=reason,
                        price=last_price,
                        amount=layer["amount"],
                        trade_id=layer["trade_id"],
                        layer_id=layer["layer_id"],
                        order_id=layer.get("order_id"),
                    )

                    self.positions.remove_layer(
                        symbol,
                        layer["layer_id"]
                    )

        info("SYNC selesai")
