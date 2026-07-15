// dashboard.js V5
function $(id){return document.getElementById(id);}
function rupiah(v){return "Rp "+Number(v||0).toLocaleString("id-ID");}

async function loadDashboard(){
  try{
    const r=await fetch("/api/dashboard?t="+Date.now(),{cache:"no-store"});
    if(!r.ok) throw new Error(r.status);
    const d=await r.json();

    const s=d.status||{};
    const st=d.stats||{};
    const pos=Array.isArray(d.positions)?d.positions:[];
    const hist=Array.isArray(d.history)?d.history:[];

    if($("bot-status")) $("bot-status").innerText=s.bot||"OFFLINE";
    if($("exchange-status")) $("exchange-status").innerText=s.exchange||"-";
    if($("idr-balance")) $("idr-balance").innerText=rupiah(s.idr_balance);
    if($("total-asset")) $("total-asset").innerText=rupiah(s.total_asset);
    if($("btc-status")) $("btc-status").innerText=s.btc_status||"-";
    if($("top-scanner")) $("top-scanner").innerText=s.top_scanner||"-";
    if($("today-profit")) $("today-profit").innerText=(st.today_profit||0)+"%";
    if($("win-rate")) $("win-rate").innerText=(st.winrate||0)+"%";
    if($("recent-activity")){
      $("recent-activity").innerText=s.last_activity||(
        hist.length?"Trade terakhir tersedia":"Belum ada aktivitas.");
    }
    if($("active-position")){
      if(!pos.length){
        $("active-position").innerHTML="Belum ada posisi aktif.";
      }else{
        $("active-position").innerHTML=pos.map(p=>
          `<div class="card">
          <b>${p.symbol||"-"}</b><br>
          Layer: ${p.layer??1}<br>
          Profit: ${p.profit_percent??0}%<br>
          Hold: ${p.hold_time??"-"}
          </div>`
        ).join("");
      }
    }
  }catch(e){
    console.error("Dashboard:",e);
    if($("bot-status")) $("bot-status").innerText="OFFLINE";
    if($("exchange-status")) $("exchange-status").innerText="ERROR";
  }
}
document.addEventListener("DOMContentLoaded",()=>{
  loadDashboard();
  setInterval(loadDashboard,5000);
});
