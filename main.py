"""
main.py
Production Bootstrap (Dependency Injection)

Comments: English
Terminal logs: Indonesian
"""

from __future__ import annotations

import threading
from flask import Flask, jsonify, render_template

import config
from buyer import Buyer
from exchange import ExchangeClient
from history import HistoryEngine
from logger import info, error
from order_manager import OrderManager
from position_manager import PositionManager
from recovery import RecoveryEngine
from risk import RiskEngine
from scanner import MarketScanner
from scoring import AIScoring
from sell_strategy import SellStrategy
from seller import Seller
from storage import StorageManager
from sync import SyncEngine
from trader import Trader
from validator import BuyValidator

app = Flask(__name__)

# ---------- Bootstrap ----------
storage = StorageManager()
storage.initialize()

exchange = ExchangeClient()
exchange.initialize()

positions = PositionManager(storage)
history = HistoryEngine(storage)
orders = OrderManager(exchange)

scanner = MarketScanner(exchange)
scoring = AIScoring()
validator = BuyValidator(exchange, positions)
risk = RiskEngine(positions, history)

buyer = Buyer(orders, positions, history)
seller = Seller(orders, positions, history)
strategy = SellStrategy()

sync_engine = SyncEngine(exchange, orders, positions, history)
recovery = RecoveryEngine(exchange, orders, positions, history)

trader = Trader(
    exchange=exchange,
    scanner=scanner,
    scoring=scoring,
    validator=validator,
    risk=risk,
    buyer=buyer,
    seller=seller,
    strategy=strategy,
    positions=positions,
    sync_engine=sync_engine,
    recovery_engine=recovery,
)

# ---------- Background Worker ----------
def trading_worker():
    info("Memulai Trading Engine")

    if not exchange.health_check():
        error("Exchange health check gagal.")
        return

    trader.run_forever()


# ---------- Dashboard ----------
@app.route("/")
def home():
    return render_template("home.html")


@app.route("/api/status")
def status():
    return jsonify({
        "bot": "RUNNING",
        "exchange": exchange.health_check(),
        "symbols": positions.symbol_count(),
        "layers": positions.layer_count(),
    })


@app.route("/api/sync", methods=["POST"])
def sync_now():
    sync_engine.run()
    return jsonify({"status": "OK"})


@app.route("/api/health")
def health():
    return jsonify({
        "healthy": exchange.health_check()
    })


if __name__ == "__main__":
    thread = threading.Thread(
        target=trading_worker,
        daemon=True
    )
    thread.start()

    info("Dashboard aktif.")

    app.run(
        host="0.0.0.0",
        port=config.PORT,
        debug=False,
        use_reloader=False,
    )
