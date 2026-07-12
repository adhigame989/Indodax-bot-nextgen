"""
scheduler.py
Production Task Scheduler.

Comments: English
Terminal logs: Indonesian
"""

from __future__ import annotations

import threading
import time
from dataclasses import dataclass
from typing import Callable, Dict

from logger import info, error


@dataclass
class ScheduledTask:
    name: str
    interval: int
    callback: Callable
    enabled: bool = True
    last_run: float = 0.0


class Scheduler:
    """Simple production scheduler for recurring tasks."""

    def __init__(self):
        self._tasks: Dict[str, ScheduledTask] = {}
        self._lock = threading.RLock()
        self._running = False

    def add_task(self, name: str, interval: int, callback: Callable):
        with self._lock:
            self._tasks[name] = ScheduledTask(
                name=name,
                interval=interval,
                callback=callback,
            )
        info(f"Scheduler tambah task: {name}")

    def enable(self, name: str):
        with self._lock:
            if name in self._tasks:
                self._tasks[name].enabled = True

    def disable(self, name: str):
        with self._lock:
            if name in self._tasks:
                self._tasks[name].enabled = False

    def run_pending(self):
        now = time.time()
        with self._lock:
            tasks = list(self._tasks.values())

        for task in tasks:
            if not task.enabled:
                continue
            if now - task.last_run < task.interval:
                continue
            try:
                info(f"Scheduler menjalankan: {task.name}")
                task.callback()
                task.last_run = now
            except Exception as exc:
                error(f"Task {task.name} gagal: {exc}")

    def start(self, tick: float = 1.0):
        if self._running:
            return
        self._running = True
        info("Scheduler aktif")

        while self._running:
            self.run_pending()
            time.sleep(tick)

    def stop(self):
        self._running = False
        info("Scheduler berhenti")

    def start_background(self, tick: float = 1.0):
        thread = threading.Thread(
            target=self.start,
            kwargs={"tick": tick},
            daemon=True,
            name="SchedulerThread",
        )
        thread.start()
        return thread
