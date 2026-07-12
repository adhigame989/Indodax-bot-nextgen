"""
stats.py
Production Statistics Engine.
"""
from datetime import datetime
from math import inf
from logger import info
from history import HistoryEngine

class StatisticsEngine:
    def __init__(self, history: HistoryEngine):
        self.history=history
    def _rows(self):
        d=self.history.storage.history.load()
        return d if isinstance(d,list) else []
    def summary(self):
        sells=[r for r in self._rows() if r.get("side")=="SELL"]
        total=len(sells)
        wins=sum(1 for r in sells if float(r.get("profit_percent",0))>0)
        losses=total-wins
        gp=sum(max(0,float(r.get("profit_percent",0))) for r in sells)
        gl=abs(sum(min(0,float(r.get("profit_percent",0))) for r in sells))
        winrate=(wins/total*100) if total else 0
        pf="INF" if gl==0 and gp>0 else round(gp/gl,2) if gl else 0
        exp=((winrate/100)*(gp/wins if wins else 0))-(((100-winrate)/100)*(gl/losses if losses else 0))
        eq=peak=dd=0
        hold=[]
        for r in sells:
            bt=r.get("buy_time"); st=r.get("sell_time") or r.get("timestamp")
            if bt and st:
                try: hold.append((datetime.fromisoformat(st)-datetime.fromisoformat(bt)).total_seconds()/3600)
                except: pass
            eq+=float(r.get("profit_percent",0)); peak=max(peak,eq); dd=max(dd,peak-eq)
        info("Statistik diperbarui.")
        return {
            "total_trades":total,
            "wins":wins,
            "losses":losses,
            "winrate":round(winrate,2),
            "profit_factor":pf,
            "expectancy":round(exp,2),
            "avg_hold_hours":round(sum(hold)/len(hold),2) if hold else 0,
            "max_drawdown_percent":round(dd,2),
            "net_profit_percent":round(gp-gl,2)
        }
