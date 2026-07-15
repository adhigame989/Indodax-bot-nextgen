"""
position_manager.py
Production Position Manager V4 (Thread Safe)
"""

from __future__ import annotations

from copy import deepcopy
from datetime import datetime, timezone
from threading import RLock
from typing import Dict, List, Optional

from logger import info, warning
from storage import StorageManager


def _now():
    return datetime.now(timezone.utc).astimezone().isoformat()


class PositionManager:
    def __init__(self, storage: StorageManager):
        self.storage = storage
        self._lock = RLock()

    def _load(self)->Dict:
        data=self.storage.active_trades.load({})
        return data if isinstance(data,dict) else {}

    def _save(self,data:Dict):
        self.storage.active_trades.save(data)

    def snapshot(self)->Dict:
        with self._lock:
            return deepcopy(self._load())

    def all(self)->Dict:
        return self.snapshot()

    def layers(self,symbol:str)->List[Dict]:
        return deepcopy(self.snapshot().get(symbol,[]))

    def get_layer(self,symbol:str,layer_id:str)->Optional[Dict]:
        for row in self.layers(symbol):
            if row.get("layer_id")==layer_id:
                return row
        return None

    def exists(self,symbol:str,layer_id:str)->bool:
        return self.get_layer(symbol,layer_id) is not None

    def add_layer(self,symbol:str,layer:Dict):
        with self._lock:
            active=self._load()
            layer.setdefault("status","OPEN")
            layer.setdefault("highest_price",layer.get("buy_price",0))
            layer.setdefault("highest_profit",0.0)
            layer.setdefault("manual_sell",False)
            layer.setdefault("sell_reason","")
            layer.setdefault("created_at",_now())
            layer["last_update"]=_now()
            active.setdefault(symbol,[]).append(layer)
            self._save(active)
        info(f"Layer ditambahkan: {symbol}")

    def replace_layer(self,symbol:str,layer:Dict):
        with self._lock:
            active=self._load()
            rows=active.get(symbol,[])
            for i,old in enumerate(rows):
                if old.get("layer_id")==layer.get("layer_id"):
                    layer["last_update"]=_now()
                    rows[i]=layer
                    break
            self._save(active)

    def remove_layer(self,symbol:str,layer_id:str):
        with self._lock:
            active=self._load()
            if symbol not in active:
                warning(f"Symbol tidak ditemukan: {symbol}")
                return
            active[symbol]=[x for x in active[symbol] if x.get("layer_id")!=layer_id]
            if not active[symbol]:
                active.pop(symbol,None)
            self._save(active)

    def update_market(self,symbol:str,layer_id:str,price:float):
        with self._lock:
            active=self._load()
            for layer in active.get(symbol,[]):
                if layer.get("layer_id")!=layer_id:
                    continue
                buy=float(layer.get("buy_price",price))
                profit=((price-buy)/buy)*100 if buy else 0
                if price>float(layer.get("highest_price",buy)):
                    layer["highest_price"]=price
                    layer["highest_profit"]=profit
                layer["last_price"]=price
                layer["profit_percent"]=profit
                layer["last_update"]=_now()
            self._save(active)

    def update_status(self,symbol:str,layer_id:str,status:str):
        with self._lock:
            active=self._load()
            for layer in active.get(symbol,[]):
                if layer.get("layer_id")==layer_id:
                    layer["status"]=status
                    layer["last_update"]=_now()
            self._save(active)

    def mark_manual_sell(self,symbol:str,layer_id:str):
        with self._lock:
            active=self._load()
            for layer in active.get(symbol,[]):
                if layer.get("layer_id")==layer_id:
                    layer["manual_sell"]=True
                    layer["sell_reason"]="MANUAL"
                    layer["status"]="CLOSED"
                    layer["closed_at"]=_now()
            self._save(active)

    def cleanup_empty(self):
        with self._lock:
            active=self._load()
            active={k:v for k,v in active.items() if v}
            self._save(active)

    def export_summary(self):
        snap=self.snapshot()
        total_layers=sum(len(v) for v in snap.values())
        total_profit=sum(float(x.get("profit_percent",0)) for rows in snap.values() for x in rows)
        return {
            "symbols":len(snap),
            "layers":total_layers,
            "total_profit_percent":round(total_profit,2)
        }

    def symbol_count(self)->int:
        return len(self.snapshot())

    def layer_count(self)->int:
        return sum(len(v) for v in self.snapshot().values())
