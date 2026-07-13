"""
storage.py
Production Storage Manager (Railway Volume Ready)
"""

from __future__ import annotations

import json
import os
from pathlib import Path
from threading import RLock


class JsonStorage:

    def __init__(self, path: Path):
        self.path = path
        self.lock = RLock()

    def load(self):
        with self.lock:
            if not self.path.exists():
                return {} if self.path.suffix == ".json" else None

            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return {}

    def save(self, data):
        with self.lock:
            self.path.parent.mkdir(parents=True, exist_ok=True)
            tmp = self.path.with_suffix(".tmp")

            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(data, f, indent=2, ensure_ascii=False)

            os.replace(tmp, self.path)


class StorageManager:

    def __init__(self):

        base = os.getenv("DATA_DIR")

        if not base:
            if os.getenv("RAILWAY_ENVIRONMENT"):
                base = "/data"
            else:
                base = "./data"

        self.base_dir = Path(base)

        self.history = JsonStorage(self.base_dir / "history.json")
        self.active_trades = JsonStorage(self.base_dir / "active_trades.json")
        self.cooldown = JsonStorage(self.base_dir / "cooldown.json")
        self.config = JsonStorage(self.base_dir / "config.json")
        self.paper_wallet = JsonStorage(self.base_dir / "paper_wallet.json")

    def initialize(self):

        self.base_dir.mkdir(parents=True, exist_ok=True)

        defaults = {
            self.history: [],
            self.active_trades: {},
            self.cooldown: {},
            self.config: {},
            self.paper_wallet: {}
        }

        for storage, default in defaults.items():
            if not storage.path.exists():
                storage.save(default)
