"""
recovery.py
Production Recovery Engine V3.

Comments: English
Terminal logs: Indonesian
"""

from __future__ import annotations

from logger import info, warning, error
from exchange import ExchangeClient
from order_manager import OrderManager
from position_manager import PositionManager
from history import HistoryEngine


class RecoveryEngine:
    """Recover trading state after restart."""

    def __init__(
        self,
        exchange: ExchangeClient,
        orders: OrderManager,
        positions: PositionManager,
        history: HistoryEngine,
    ):
        self.exchange = exchange
        self.orders = orders
        self.positions = positions
        self.history = history

    def recover(self):
        info("Recovery dimulai.")

        try:
            balance = self.exchange.safe_balance()
        except Exception as exc:
            error(f"Recovery gagal mengambil balance: {exc}")
            return

        recovered = 0
        removed = 0

        for symbol, layers in list(self.positions.all().items()):
            asset = symbol.split("/")[0]
            free_asset = float(balance.get(asset, {}).get("free", 0))

            try:
                ticker = self.exchange.fetch_ticker(symbol)
                last_price = float(ticker["last"])
            except Exception as exc:
                warning(f"Gagal mengambil ticker {symbol}: {exc}")
                continue

            for layer in list(layers):
                order_id = layer.get("order_id")

                if order_id:
                    order = self.orders.sync(order_id, symbol)
                    if order:
                        status = str(order.get("status", "")).lower()
                        layer["last_order_status"] = status

                        if status in ("open", "pending"):
                            info(f"{symbol} masih memiliki order aktif.")
                            recovered += 1
                            continue

                if free_asset <= 0:
                    self.history.record(
                        symbol=symbol,
                        side="SELL",
                        reason="RECOVERY_REMOVE",
                        price=last_price,
                        amount=layer.get("amount", 0),
                        trade_id=layer.get("trade_id"),
                        layer_id=layer.get("layer_id"),
                        order_id=layer.get("order_id"),
                    )

                    self.positions.remove_layer(symbol, layer["layer_id"])
                    removed += 1
                    continue

                self.positions.update_market(
                    symbol,
                    layer["layer_id"],
                    last_price,
                )
                recovered += 1

        info(
            f"Recovery selesai | "
            f"Recovered={recovered} Removed={removed}"
        )
