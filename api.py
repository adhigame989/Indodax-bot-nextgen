"""REST API for Dashboard V2"""
from flask import Blueprint, jsonify, request

api=Blueprint("api",__name__)

def init_api(bot):
    api.bot=bot
    return api

@api.get("/status")
def status():
    return jsonify({
        "bot":"RUNNING",
        "exchange":"ONLINE" if api.bot.exchange.health_check() else "OFFLINE",
        "symbols":api.bot.positions.symbol_count(),
        "layers":api.bot.positions.layer_count()
    })

@api.get("/stats")
def stats():
    return jsonify(api.bot.stats.summary())

@api.get("/positions")
def positions():
    return jsonify(api.bot.positions.snapshot())

@api.get("/history")
def history():
    d=api.bot.history.storage.history.load()
    return jsonify(d[-200:] if isinstance(d,list) else [])

@api.get("/scanner")
def scanner():
    return jsonify(api.bot.scanner.scan())

@api.post("/sync")
def sync():
    api.bot.sync.run()
    return jsonify({"status":"OK"})

@api.post("/recovery")
def recovery():
    api.bot.recovery.recover()
    return jsonify({"status":"OK"})

@api.post("/start")
def start():
    api.bot.running=True
    return jsonify({"status":"STARTED"})

@api.post("/stop")
def stop():
    api.bot.running=False
    return jsonify({"status":"STOPPED"})

@api.get("/settings")
def settings():
    import config
    return jsonify({
        "base_trade_amount":config.BASE_TRADE_AMOUNT,
        "max_active_trades":config.MAX_ACTIVE_TRADES,
        "max_layer_per_coin":config.MAX_LAYER_PER_COIN
    })

@api.post("/settings")
def save_settings():
    return jsonify({"saved":True,"data":request.json or {}})
