"""
storage.py
JSON storage engine for INDODAX AI Trading Bot.
Comments are in English.
"""

import json
import os
import tempfile
import threading
from typing import Any


class JsonStorage:
    """Thread-safe JSON storage with atomic writes."""

    def __init__(self, filename: str):
        self.filename = filename
        self._lock = threading.Lock()
        self._ensure_file()

    def _ensure_file(self):
        """Create file if it does not exist."""
        if not os.path.exists(self.filename):
            self.save({})

    def load(self) -> Any:
        """Load JSON safely."""
        with self._lock:
            try:
                with open(self.filename, "r", encoding="utf-8") as f:
                    return json.load(f)
            except Exception:
                return {}

    def save(self, data: Any):
        """Atomically save JSON."""
        with self._lock:
            directory = os.path.dirname(self.filename) or "."
            fd, temp_path = tempfile.mkstemp(dir=directory, suffix=".tmp")
            try:
                with os.fdopen(fd, "w", encoding="utf-8") as tmp:
                    json.dump(data, tmp, indent=4, ensure_ascii=False)
                    tmp.flush()
                    os.fsync(tmp.fileno())
                os.replace(temp_path, self.filename)
            finally:
                if os.path.exists(temp_path):
                    try:
                        os.remove(temp_path)
                    except OSError:
                        pass

    def update(self, updater):
        """Read-modify-write transaction."""
        with self._lock:
            data = self.load()
            updater(data)
            self.save(data)


class StorageManager:
    """Convenience wrapper for bot JSON files."""

    def __init__(self, active_file, history_file, cooldown_file):
        self.active = JsonStorage(active_file)
        self.history = JsonStorage(history_file)
        self.cooldown = JsonStorage(cooldown_file)
