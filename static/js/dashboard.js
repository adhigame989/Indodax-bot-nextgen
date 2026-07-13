// dashboard.js V3 Full Replacement
function el(id){return document.getElementById(id);}
function fmtIDR(v){return "Rp"+Number(v||0).toLocaleString("id-ID");}

async function fetchStatus(){
 const s=await apiSafe(()=>API.status(),null);
 if(!s)return;
 if(el("bot-status"))el("bot-status").innerText=s.bot??"OFFLINE";
 if(el("exchange-status"))el("exchange-status").innerText=s.exchange??"OFFLINE";
 if(el("idr-balance"))el("idr-balance").innerText=fmtIDR(s.idr_balance);
 if(el("total-asset"))el("total-asset").innerText=fmtIDR(s.total_asset);
 if(el("btc-status"))el("btc-status").innerText=s.btc_status??"-";
 if(el("top-scanner"))el("top-scanner").innerText=s.top_scanner??"-";
 if(el("recent-activity"))el("recent-activity").innerText=s.last_activity??"-";
}

async function fetchStats(){
 const s=await apiSafe(()=>API.stats(),null);
 if(!s)return;
 if(el("today-profit"))el("today-profit").innerText=(s.today_profit??0)+"%";
 if(el("win-rate"))el("win-rate").innerText=(s.winrate??0)+"%";
}

async function fetchPositions(){
 const p=await apiSafe(()=>API.positions(),[]);
 const box=el("active-position");
 if(!box)return;
 if(!Array.isArray(p)||!p.length){
   box.innerHTML="Belum ada posisi aktif.";
   return;
 }
 box.innerHTML=p.map(x=>`
 <div>
 <b>${x.symbol||"-"}</b><br>
 Profit : ${x.profit_percent??0}%<br>
 Layer : ${x.layer??1}<br>
 Hold : ${x.hold_time??"-"}
 </div>
 <hr>`).join("");
}

async function refreshDashboard(){
 await Promise.all([
   fetchStatus(),
   fetchStats(),
   fetchPositions()
 ]);
}

document.addEventListener("DOMContentLoaded",()=>{
 refreshDashboard();
 setInterval(refreshDashboard,5000);
});
