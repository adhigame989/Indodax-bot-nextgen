"""
api.py V3 - Production API
Replace existing api.py
"""
from flask import Blueprint, jsonify, request
from logger import error

def init_api(trader):
    api = Blueprint("api", __name__)

    def ok(data):
        return jsonify(data)

    def fail(exc):
        error(f"API ERROR: {exc}")
        return jsonify({"status":"ERROR","message":str(exc)}),500

    @api.get("/status")
    def status():
        try:
            stats = getattr(trader, "stats", None)
            positions = trader.positions.all() if hasattr(trader.positions,"all") else {}
            active = sum(len(v) for v in positions.values()) if isinstance(positions,dict) else 0
            return ok({
                "status":"OK",
                "bot":"RUNNING" if getattr(trader,"running",False) else "STOPPED",
                "exchange":"ONLINE",
                "active_trades":active,
                "symbols":len(positions) if isinstance(positions,dict) else 0,
                "version":"2.0"
            })
        except Exception as e:
            return fail(e)

    @api.get("/stats")
    def api_stats():
        try:
            if hasattr(trader,"stats") and hasattr(trader.stats,"summary"):
                return ok(trader.stats.summary())
            return ok({})
        except Exception as e:
            return fail(e)

    @api.get("/positions")
    def api_positions():
        try:
            if hasattr(trader.positions,"export"):
                return ok(trader.positions.export())
            if hasattr(trader.positions,"all"):
                return ok(trader.positions.all())
            return ok([])
        except Exception as e:
            return fail(e)

    @api.get("/scanner")
    def api_scanner():
        try:
            if hasattr(trader.scanner,"last_result"):
                return ok(trader.scanner.last_result)
            return ok([])
        except Exception as e:
            return fail(e)

    @api.get("/history")
    def api_history():
        try:
            if hasattr(trader.history,"all"):
                return ok(trader.history.all())
            if hasattr(trader.history,"load"):
                return ok(trader.history.load())
            return ok([])
        except Exception as e:
            return fail(e)

    @api.get("/settings")
    def settings():
        import config
        return ok({
            "base_trade_amount":config.BASE_TRADE_AMOUNT,
            "max_active_trades":config.MAX_ACTIVE_TRADES,
            "max_layer_per_coin":config.MAX_LAYER_PER_COIN,
            "take_profit":config.TAKE_PROFIT,
            "stop_loss":config.STOP_LOSS,
            "trailing_gap":config.TRAILING_GAP
        })

    @api.post("/settings")
    def save_settings():
        try:
            data=request.get_json(silent=True) or {}
            if hasattr(trader,"save_settings"):
                trader.save_settings(data)
            return ok({"success":True})
        except Exception as e:
            return fail(e)

    @api.post("/start")
    def start():
        trader.start()
        return ok({"success":True})

    @api.post("/stop")
    def stop():
        trader.stop()
        return ok({"success":True})

    @api.post("/sync")
    def sync():
        try:
            trader.sync.run()
            return ok({"success":True})
        except Exception as e:
            return fail(e)

    @api.post("/recovery")
    def recovery():
        try:
            trader.recovery.recover()
            return ok({"success":True})
        except Exception as e:
            return fail(e)

    @api.get("/health")
    def health():
        return ok({"status":"OK"})

    return api
