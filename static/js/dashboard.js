// dashboard.js
class Dashboard{
constructor(){this.interval=5000;}
set(id,val){
const e=document.getElementById(id);
if(e)e.innerText=val;
}
async refresh(){
const status=await apiSafe(()=>API.status(),null);
const stats=await apiSafe(()=>API.stats(),null);
if(status){
this.set("bot",status.bot);
this.set("exchange",status.exchange);
this.set("symbols",status.symbols);
this.set("layers",status.layers);
}
if(stats){
this.set("winrate",(stats.winrate??0)+"%");
this.set("netprofit",(stats.net_profit_percent??0)+"%");
this.set("pf",stats.profit_factor??"-");
this.set("expectancy",stats.expectancy??"-");
this.set("drawdown",(stats.max_drawdown_percent??0)+"%");
}
}
start(){
this.refresh();
setInterval(()=>this.refresh(),this.interval);
}
}
window.addEventListener("DOMContentLoaded",()=>{
new Dashboard().start();
});
