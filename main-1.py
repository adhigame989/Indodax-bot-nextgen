"""
main.py
Application entry point for INDODAX AI Trading Bot.

Comments: English
Terminal logs: Indonesian
"""

from __future__ import annotations

import threading

from flask import Flask, jsonify, render_template

import config
from storage import StorageManager
from trader import Trader

app = Flask(__name__)

storage = StorageManager()
storage.initialize()

trader = Trader()


@app.route("/")
def home():
    active = storage.active_trades.load()
    history = storage.history.load()

    return render_template(
        "home.html",
        active_trades=active,
        history=history[-20:] if isinstance(history, list) else [],
        bot_status="RUNNING",
    )


@app.route("/api/status")
def api_status():
    active = storage.active_trades.load()
    history = storage.history.load()

    active_layers = sum(len(v) for v in active.values()) if isinstance(active, dict) else 0

    return jsonify({
        "status": "RUNNING",
        "exchange": config.EXCHANGE_NAME,
        "active_symbols": len(active) if isinstance(active, dict) else 0,
        "active_layers": active_layers,
        "history_count": len(history) if isinstance(history, list) else 0,
    })


@app.route("/api/active")
def api_active():
    return jsonify(storage.active_trades.load())


@app.route("/api/history")
def api_history():
    return jsonify(storage.history.load())


def trading_worker():
    """Run trading engine forever."""
    trader.run_forever(config.SCAN_INTERVAL)


if __name__ == "__main__":
    print("[INFO] Memulai INDODAX AI Trading Bot...")

    worker = threading.Thread(
        target=trading_worker,
        daemon=True,
        name="TraderThread",
    )
    worker.start()

    print("[INFO] Dashboard Flask aktif.")

    app.run(
        host="0.0.0.0",
        port=5000,
        debug=False,
        threaded=True,
    )
