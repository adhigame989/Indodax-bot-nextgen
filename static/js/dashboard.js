// dashboard.js V4
function $(id){return document.getElementById(id);}
function rupiah(v){return "Rp "+Number(v||0).toLocaleString("id-ID");}

async function getJSON(url){
  const r=await fetch(url+"?t="+Date.now(),{cache:"no-store"});
  if(!r.ok) throw new Error(r.status);
  return await r.json();
}

async function loadDashboard(){
  try{
    const [status,stats,positions,scanner]=await Promise.all([
      getJSON("/api/status"),
      getJSON("/api/stats"),
      getJSON("/api/positions"),
      getJSON("/api/scanner").catch(()=>({}))
    ]);

    if($("bot-status")) $("bot-status").innerText=status.running?"ONLINE":"OFFLINE";
    if($("exchange-status")) $("exchange-status").innerText="CONNECTED";
    if($("btc-status")) $("btc-status").innerText=scanner.btc_status||"-";
    if($("top-scanner")) $("top-scanner").innerText=scanner.top||scanner.scanner||"-";
    if($("win-rate")) $("win-rate").innerText=(stats.winrate||0)+"%";
    if($("today-profit")) $("today-profit").innerText=(stats.total_profit_percent||0)+"%";

    const wrap=$("active-position");
    if(wrap){
      const rows=[];
      Object.entries(positions||{}).forEach(([symbol,layers])=>{
        (layers||[]).forEach((p,i)=>{
          rows.push(`<div class="card">
<b>${symbol}</b><br>
Layer: ${p.layer_id||i+1}<br>
Status: ${p.status||"OPEN"}<br>
Profit: ${Number(p.profit_percent||0).toFixed(2)}%<br>
High: ${p.highest_profit||0}%
</div>`);
        });
      });
      wrap.innerHTML=rows.length?rows.join(""):"Belum ada posisi aktif.";
    }
  }catch(e){
    console.error("Dashboard:",e);
    if($("bot-status")) $("bot-status").innerText="OFFLINE";
    if($("exchange-status")) $("exchange-status").innerText="ERROR";
  }
}

document.addEventListener("DOMContentLoaded",()=>{
  loadDashboard();
  setInterval(loadDashboard,3000);
});
