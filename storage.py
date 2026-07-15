"""
storage.py
INDODAX BOT NEXTGEN
Storage Manager V2
- Atomic Save
- Auto Backup
- Auto Recovery
- Railway Ready
"""

from __future__ import annotations

import json
import os
import shutil
from pathlib import Path
from threading import RLock


class JsonStorage:

    def __init__(self, path: Path):
        self.path = path
        self.lock = RLock()

    def load(self, default=None):

        with self.lock:

            if default is None:
                default = {}

            if not self.path.exists():
                return default

            try:
                with open(self.path, "r", encoding="utf-8") as f:
                    return json.load(f)

            except Exception:

                backup = self.path.with_suffix(".bak")

                if backup.exists():

                    try:
                        with open(backup, "r", encoding="utf-8") as f:
                            return json.load(f)
                    except Exception:
                        pass

                return default

    def save(self, data):

        with self.lock:

            self.path.parent.mkdir(parents=True, exist_ok=True)

            tmp = self.path.with_suffix(".tmp")
            bak = self.path.with_suffix(".bak")

            with open(tmp, "w", encoding="utf-8") as f:
                json.dump(
                    data,
                    f,
                    indent=2,
                    ensure_ascii=False
                )

            if self.path.exists():

                try:
                    shutil.copy2(self.path, bak)
                except Exception:
                    pass

            os.replace(tmp, self.path)

    def exists(self):
        return self.path.exists()

    def delete(self):

        with self.lock:

            if self.path.exists():
                self.path.unlink()


class StorageManager:

    def __init__(self):

        base = os.getenv("DATA_DIR")

        if not base:

            if os.getenv("RAILWAY_ENVIRONMENT"):
                base = "/data"
            else:
                base = "./data"

        self.base_dir = Path(base)

        self.history = JsonStorage(
            self.base_dir / "history.json"
        )

        self.active_trades = JsonStorage(
            self.base_dir / "active_trades.json"
        )

        self.layers = JsonStorage(
            self.base_dir / "layers.json"
        )

        self.cooldown = JsonStorage(
            self.base_dir / "cooldown.json"
        )

        self.stats = JsonStorage(
            self.base_dir / "stats.json"
        )

        self.bot_state = JsonStorage(
            self.base_dir / "bot_state.json"
        )

        self.config = JsonStorage(
            self.base_dir / "config.json"
        )

        self.paper_wallet = JsonStorage(
            self.base_dir / "paper_wallet.json"
        )

    def initialize(self):

        self.base_dir.mkdir(
            parents=True,
            exist_ok=True
        )

        defaults = {

            self.history: [],

            self.active_trades: {},

            self.layers: {},

            self.cooldown: {},

            self.stats: {

                "total_trade": 0,
                "win": 0,
                "loss": 0,
                "profit": 0.0,
                "winrate": 0.0

            },

            self.bot_state: {

                "running": False,
                "scanner_running": False,
                "trader_running": False,
                "last_scan": None,
                "last_trade": None

            },

            self.config: {},

            self.paper_wallet: {}

        }

        for storage, default in defaults.items():

            if not storage.exists():
                storage.save(default)

    def backup_all(self):

        files = [

            self.history,
            self.active_trades,
            self.layers,
            self.cooldown,
            self.stats,
            self.bot_state,
            self.config,
            self.paper_wallet

        ]

        for storage in files:

            if storage.exists():

                try:

                    shutil.copy2(
                        storage.path,
                        storage.path.with_suffix(".bak")
                    )

                except Exception:
                    pass


storage = StorageManager()
storage.initialize()
