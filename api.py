"""
api_v4.py
NextGen API V4
Compatible with:
    app.register_blueprint(init_api(trader), url_prefix="/api")
"""

from flask import Blueprint, jsonify


def init_api(trader):
    api = Blueprint("api", __name__)

    @api.get("/status")
    def status():
        pm = trader.positions
        return jsonify({
            "running": getattr(trader, "running", False),
            "symbols": pm.symbol_count() if hasattr(pm, "symbol_count") else 0,
            "layers": pm.layer_count() if hasattr(pm, "layer_count") else 0,
        })

    @api.get("/positions")
    def positions():
        pm = trader.positions
        if hasattr(pm, "snapshot"):
            return jsonify(pm.snapshot())
        if hasattr(pm, "all"):
            return jsonify(pm.all())
        return jsonify({})

    @api.get("/stats")
    def stats():
        if hasattr(trader, "stats"):
            stats = trader.stats
            for fn in ("summary", "export_summary", "export", "to_dict"):
                if hasattr(stats, fn):
                    return jsonify(getattr(stats, fn)())
        pm = trader.positions
        if hasattr(pm, "export_summary"):
            return jsonify(pm.export_summary())
        return jsonify({})

    @api.get("/scanner")
    def scanner():
        sc = getattr(trader, "scanner", None)
        if sc is None:
            return jsonify({"scanner": "unavailable"})
        return jsonify(getattr(sc, "last_result", {}))

    @api.get("/dashboard")
    def dashboard():
        pm = trader.positions
        return jsonify({
            "status": {
                "bot": "ONLINE" if getattr(trader, "running", False) else "OFFLINE",
                "exchange": "CONNECTED",
            },
            "stats": pm.export_summary() if hasattr(pm, "export_summary") else {},
            "positions": pm.snapshot() if hasattr(pm, "snapshot") else {},
            "history": []
        })

    @api.post("/start")
    def start():
        trader.start()
        return jsonify({"success": True})

    @api.post("/stop")
    def stop():
        trader.stop()
        return jsonify({"success": True})

    return api
