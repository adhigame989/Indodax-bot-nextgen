"""
main.py
Production Bootstrap (Refactored)
"""

from flask import Flask, render_template
import threading

import config
from api import init_api
from buyer import Buyer
from exchange import ExchangeClient
from history import HistoryEngine
from logger import info, error
from order_manager import OrderManager
from position_manager import PositionManager
from recovery import RecoveryEngine
from risk import RiskEngine
from scanner import MarketScanner
from scheduler import Scheduler
from scoring import AIScoring
from sell_strategy import SellStrategy
from seller import Seller
from stats import StatisticsEngine
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
stats = StatisticsEngine(history)

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

# Expose shared services
trader.history = history
trader.stats = stats

# API
app.register_blueprint(init_api(trader), url_prefix="/api")

# Scheduler
scheduler = Scheduler()
scheduler.add_task("scan_cycle", config.SCAN_INTERVAL, trader.cycle)
scheduler.add_task("recovery", 600, recovery.recover)

def engine_worker():
    info("Engine startup")
    if not exchange.health_check():
        error("Exchange offline")

    trader.startup()
    scheduler.start()

@app.route("/")
def home():
    return render_template("home.html")

@app.route("/scanner")
def scanner_page():
    return render_template("scanner.html")

@app.route("/monitor")
def monitor_page():
    return render_template("monitor.html")

@app.route("/history")
def history_page():
    return render_template("history.html")

@app.route("/settings")
def settings_page():
    return render_template("settings.html")

if __name__ == "__main__":
    threading.Thread(target=engine_worker, daemon=True).start()
    info("Dashboard aktif")
    app.run(
        host="0.0.0.0",
        port=config.PORT,
        debug=False,
        use_reloader=False
    )
