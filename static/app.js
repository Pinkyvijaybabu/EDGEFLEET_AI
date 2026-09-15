let last={};
const $=s=>document.querySelector(s);
async function post(url,body={}){const r=await fetch(url,{method:'POST',headers:{'Content-Type':'application/json'},body:JSON.stringify(body)});return r.json()}
function selected(){return $('#robotSelect').value}
function resetFleet(){post('/api/reset',{count:5})}
function fault(){post('/api/fault',{robot_id:selected()})}
function recover(){post('/api/recover',{robot_id:selected()})}
function partition(){post('/api/network',{robot_id:selected(),enabled:true})}
function unpartition(){post('/api/network',{robot_id:selected(),enabled:false})}
function forceConflict(){post('/api/conflict')}
function blockRandom(){let x=2+Math.floor(Math.random()*14),y=2+Math.floor(Math.random()*14);post('/api/block',{x,y})}
function addTask(){post('/api/task',{pickup:[1+Math.floor(Math.random()*16),1+Math.floor(Math.random()*16)],dropoff:[1+Math.floor(Math.random()*16),1+Math.floor(Math.random()*16)],priority:1+Math.floor(Math.random()*10)})}
async function benchmark(){const r=await post('/api/benchmark');$('#experiment').textContent=JSON.stringify(r,null,2)}
async function runExperiment(){ $('#experiment').textContent='Running 5→100 robot scalability experiment…'; const r=await post('/api/experiment',{robots:[5,10,25,50,100],ticks:100}); $('#experiment').textContent=JSON.stringify(r.results,null,2)}
function render(s){last=s;const m=s.metrics;const cards=[['Fleet',m.fleet_size],['Active',m.active],['Tasks done',m.completed_tasks],['Collisions',m.collisions],['Negotiations',m.negotiations],['P2P msgs',m.p2p_messages],['Isolated',m.partitioned]];$('#metrics').innerHTML=cards.map(c=>`<div class="metric"><span>${c[0]}</span><strong>${c[1]}</strong></div>`).join('');
$('#robotSelect').innerHTML=s.robots.map(r=>`<option>${r.id}</option>`).join('');
const map={};s.robots.forEach(r=>map[`${r.x},${r.y}`]=r);let html='';for(let y=0;y<s.grid.height;y++)for(let x=0;x<s.grid.width;x++){const key=`${x},${y}`,r=map[key],blocked=s.grid.blocked.some(p=>p[0]===x&&p[1]===y);let cls='cell'+(blocked?' blocked':'');if(r)cls+=' robot'+(!r.connected?' isolated':'');html+=`<div class="${cls}">${r?`<b>${r.id.replace('AMR-','')}</b>`:''}</div>`}$('#grid').innerHTML=html;
$('#robots').innerHTML=s.robots.map(r=>{const t=r.telemetry;return `<div class="robot"><div class="row"><strong>${r.id}</strong><span class="tag ${t.anomaly_risk>.72?'alert':''}">${r.state}${t.anomaly_risk>.72?' · AI ALERT':''}</span></div><small>task ${r.task||'—'} · ${r.alive?'online':'FAILED'} · ${r.connected?'P2P connected':'NETWORK ISOLATED'}</small><div class="bar"><i style="width:${Math.max(0,t.battery)}%"></i></div><small>Battery ${t.battery}% · Temp ${t.temperature}°C · Speed ${t.speed} · Risk ${t.anomaly_risk}</small></div>`}).join('');
$('#conn').textContent='● live';$('#conn').className='ok';}
async function refresh(){try{const s=await (await fetch('/api/status')).json();render(s)}catch(e){$('#conn').textContent='offline'}}
async function events(){try{const e=await (await fetch('/api/events')).json();$('#events').innerHTML=e.slice(0,25).map(x=>`<div class="event"><strong>${x.level}</strong> ${x.event}<br><small>${new Date(x.ts*1000).toLocaleTimeString()}</small></div>`).join('')}catch(e){}}
function connect(){let ws;try{ws=new WebSocket(`ws://${location.host}/ws`);ws.onopen=()=>$('#conn').textContent='● WebSocket live';ws.onmessage=e=>render(JSON.parse(e.data));ws.onclose=()=>setTimeout(connect,1000)}catch(e){setTimeout(connect,1000)}}
refresh();events();setInterval(events,1500);connect();
