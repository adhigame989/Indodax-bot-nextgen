"""api.py V5"""
from flask import Blueprint,jsonify
import config
from wallet import get_wallet

def init_api(trader):
 api=Blueprint("api",__name__)
 j=lambda d,s=200:(jsonify(d),s)
 def pos():
  try:
   if hasattr(trader.positions,"export"): d=trader.positions.export() or []
   elif hasattr(trader.positions,"all"): d=trader.positions.all()
   else: d=[]
   return list(d.values()) if isinstance(d,dict) else (d if isinstance(d,list) else [])
  except: return []
 def stat():
  t="-"
  try:
   if hasattr(trader.scanner,"last_result"): t=(trader.scanner.last_result or {}).get("top_scanner","-")
  except: pass
  return {"status":"OK","bot":"RUNNING" if getattr(trader,"running",True) else "STOPPED","exchange":"ONLINE","idr_balance": wallet.get_idr() if wallet else 0,"total_asset": wallet.get_total_asset() if wallet else 0,"wallet": wallet.get_assets() if wallet else {},"btc_status":getattr(trader,"btc_status","-"),"top_scanner":t,"last_activity":getattr(trader,"last_activity","-"),"active_trades":len(pos()),"symbols":len(pos()),"version":"5.0"}
 def sts():
  try:
   return trader.stats.summary()
  except: return {}
 def sc():
  try:return trader.scanner.last_result or {}
  except:return {}
 def hist():
  try:
   return trader.history.all()
  except:
   return []
 @api.get("/status")
 def a(): return j(stat())
 @api.get("/stats")
 def b(): return j(sts())
 @api.get("/positions")
 def c(): return j(pos())
 @api.get("/scanner")
 def d(): return j(sc())
 @api.get("/dashboard")
 def e(): return j({"status":stat(),"stats":sts(),"positions":pos(),"scanner":sc(),"history":hist()})
 @api.get("/history")
 def f(): return j(hist())
 @api.get("/settings")
 def g(): return j({"base_trade_amount":config.BASE_TRADE_AMOUNT,"max_active_trades":config.MAX_ACTIVE_TRADES,"max_layer_per_coin":config.MAX_LAYER_PER_COIN})
 @api.post("/start")
 def h():
  hasattr(trader,"start") and trader.start()
  return j({"success":True})
 @api.post("/stop")
 def i():
  hasattr(trader,"stop") and trader.stop()
  return j({"success":True})
 @api.post("/sync")
 def k():
  hasattr(trader,"sync_engine") and hasattr(trader.sync_engine,"run") and trader.sync_engine.run()
  return j({"success":True})
 @api.post("/recovery")
 def l():
  hasattr(trader,"recovery_engine") and hasattr(trader.recovery_engine,"recover") and trader.recovery_engine.recover()
  return j({"success":True})
 return api
