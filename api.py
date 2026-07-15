"""
api.py
INDODAX BOT NEXTGEN API V4
"""

from flask import Blueprint, jsonify

api = Blueprint("api", __name__)

def init_api(app, trader, positions, scanner=None):
    app.register_blueprint(api)

    @api.get("/api/status")
    def status():
        return jsonify({
            "running": trader.running,
            "symbols": positions.symbol_count() if hasattr(positions, "symbol_count") else 0,
            "layers": positions.layer_count() if hasattr(positions, "layer_count") else 0,
        })

    @api.get("/api/positions")
    def position_list():
        data = positions.snapshot() if hasattr(positions, "snapshot") else positions.all()
        return jsonify(data)

    @api.get("/api/stats")
    def stats():
        if hasattr(positions, "export_summary"):
            return jsonify(positions.export_summary())
        return jsonify({})

    @api.get("/api/scanner")
    def scanner_state():
        if scanner is None:
            return jsonify({"scanner": "unavailable"})
        if hasattr(scanner, "last_result"):
            return jsonify(scanner.last_result)
        return jsonify({"scanner": "ready"})

    @api.post("/api/start")
    def start():
        trader.start()
        return jsonify({"success": True, "running": True})

    @api.post("/api/stop")
    def stop():
        trader.stop()
        return jsonify({"success": True, "running": False})

    return app
