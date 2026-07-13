// api.js
const API={
async get(url){
const r=await fetch(url,{headers:{Accept:"application/json"}});
if(!r.ok) throw new Error(url);
return await r.json();
},
async post(url,data={}){
const r=await fetch(url,{
method:"POST",
headers:{"Content-Type":"application/json"},
body:JSON.stringify(data)
});
if(!r.ok) throw new Error(url);
return await r.json();
},
status(){return this.get("/api/status")},
stats(){return this.get("/api/stats")},
scanner(){return this.get("/api/scanner")},
positions(){return this.get("/api/positions")},
history(){return this.get("/api/history")},
settings(){return this.get("/api/settings")},
start(){return this.post("/api/start")},
stop(){return this.post("/api/stop")},
sync(){return this.post("/api/sync")},
recovery(){return this.post("/api/recovery")},
saveSettings(d){return this.post("/api/settings",d)}
};
async function apiSafe(cb,fallback=null){
try{return await cb();}catch(e){console.error(e);return fallback;}
}
