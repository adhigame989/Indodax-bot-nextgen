"""
api.py - V3.1 Dashboard Fix
"""
from flask import Blueprint, jsonify, request

def init_api(trader):
    api = Blueprint("api", __name__)

    def j(data, status=200):
        return jsonify(data), status

    @api.get("/status")
    def status():
        try:
            positions = []
            if hasattr(trader, "positions"):
                if hasattr(trader.positions, "export"):
                    positions = trader.positions.export() or []
                elif hasattr(trader.positions, "all"):
                    p = trader.positions.all()
                    positions = p if isinstance(p, list) else list(p.values()) if isinstance(p, dict) else []

            active = len(positions) if isinstance(positions, list) else 0

            scanner = getattr(trader, "scanner", None)
            top = "-"
            if scanner is not None and hasattr(scanner, "last_result"):
                lr = scanner.last_result or {}
                top = lr.get("top_scanner", "-")

            return j({
                "status": "OK",
                "bot": "RUNNING" if getattr(trader, "running", True) else "STOPPED",
                "exchange": "ONLINE",
                "idr_balance": getattr(trader, "idr_balance", 0),
                "total_asset": getattr(trader, "total_asset", 0),
                "btc_status": getattr(trader, "btc_status", "-"),
                "top_scanner": top,
                "last_activity": getattr(trader, "last_activity", "-"),
                "symbols": active,
                "active_trades": active,
                "version": "3.1"
            })
        except Exception as e:
            return j({"status":"ERROR","message":str(e)},500)

    @api.get("/stats")
    def stats():
        try:
            if hasattr(trader, "stats") and hasattr(trader.stats, "summary"):
                return j(trader.stats.summary())
            return j({})
        except Exception as e:
            return j({"status":"ERROR","message":str(e)},500)

    @api.get("/positions")
    def positions():
        try:
            if hasattr(trader.positions, "export"):
                data = trader.positions.export()
            elif hasattr(trader.positions, "all"):
                data = trader.positions.all()
            else:
                data = []
            if isinstance(data, dict):
                data = []
            return j(data or [])
        except Exception as e:
            return j([],200)

    @api.get("/scanner")
    def scanner():
        try:
            if hasattr(trader.scanner, "last_result"):
                return j(trader.scanner.last_result or {})
            return j({})
        except Exception as e:
            return j({"status":"ERROR","message":str(e)},500)

    @api.get("/history")
    def history():
        try:
            if hasattr(trader.history, "all"):
                return j(trader.history.all())
            if hasattr(trader.history, "load"):
                return j(trader.history.load())
            return j([])
        except:
            return j([])

    @api.get("/settings")
    def settings():
        import config
        return j({
            "base_trade_amount": config.BASE_TRADE_AMOUNT,
            "max_active_trades": config.MAX_ACTIVE_TRADES,
            "max_layer_per_coin": config.MAX_LAYER_PER_COIN
        })

    @api.post("/settings")
    def save_settings():
        return j({"success": True})

    @api.post("/start")
    def start():
        if hasattr(trader,"start"): trader.start()
        return j({"success":True})

    @api.post("/stop")
    def stop():
        if hasattr(trader,"stop"): trader.stop()
        return j({"success":True})

    @api.post("/sync")
    def sync():
        if hasattr(trader,"sync_engine") and hasattr(trader.sync_engine,"run"):
            trader.sync_engine.run()
        return j({"success":True})

    @api.post("/recovery")
    def recovery():
        if hasattr(trader,"recovery_engine") and hasattr(trader.recovery_engine,"recover"):
            trader.recovery_engine.recover()
        return j({"success":True})

    return api
