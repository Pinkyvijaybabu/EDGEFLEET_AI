const W=22,H=14;
let ws;

function cellClass(x,y,blocked){
  const base = `cell ${blocked.some(p=>p[0]===x&&p[1]===y)?'blocked':''}`;
  return base;
}
function render(s){
  document.getElementById('tick').textContent=s.tick;
  document.getElementById('completed').textContent=s.completed_tasks;
  document.getElementById('collisions').textContent=s.collisions;
  document.getElementById('deadlocks').textContent=s.deadlocks_resolved;
  document.getElementById('messages').textContent=s.messages;

  const grid=document.getElementById('grid');
  const staticObs = new Set([[4,2],[4,3],[4,4],[4,6],[4,7],[4,8],[4,9],
    [9,4],[9,5],[9,6],[9,7],[9,9],[9,10],[9,11],[9,12],
    [14,1],[14,2],[14,3],[14,4],[14,5],[14,7],[14,8],[14,9],
    [18,4],[18,5],[18,6],[18,8],[18,9],[18,10],[18,11],[18,12]]);
  grid.innerHTML='';
  for(let y=0;y<H;y++) for(let x=0;x<W;x++){
    const c=document.createElement('div');
    c.className=cellClass(x,y,s.blocked);
    if(staticObs.has([x,y].toString())) c.classList.add('obstacle');
    const r=s.robots.find(r=>r.x===x&&r.y===y);
    if(r){
      const dot=document.createElement('div');
      dot.className='robot-dot';
      dot.textContent=r.robot_id.replace('AMR-','');
      dot.title=`${r.robot_id} ${r.state}`;
      c.appendChild(dot);
    }
    grid.appendChild(c);
  }

  document.getElementById('robots').innerHTML=s.robots.map(r=>`
    <div class="robot">
      <div class="robot-top">
        <span>${r.robot_id}</span>
        <span class="badge ${r.anomaly?'warn':''}">${r.anomaly?'AI ANOMALY':'healthy'}</span>
      </div>
      <div class="muted">(${r.x},${r.y}) · ${r.state} · task ${r.task_id||'—'}</div>
      <div class="muted">Battery ${r.battery}% · ${r.temperature}°C · speed ${r.speed}</div>
      <div class="bar"><div class="fill" style="width:${r.battery}%"></div></div>
      ${r.anomaly?`<div class="muted">anomaly risk: ${r.anomaly_score}</div>`:''}
    </div>`).join('');

  document.getElementById('tasks').innerHTML='<table><tr><th>ID</th><th>Status</th><th>Robot</th></tr>'+
    s.tasks.map(t=>`<tr><td>${t.task_id}</td><td>${t.status}</td><td>${t.assigned_to||'—'}</td></tr>`).join('')+'</table>';
}

function renderEvents(events){
  document.getElementById('events').innerHTML=events.slice().reverse().map(e=>
    `<div class="event"><b>t${e.tick}</b> ${e.type} ${JSON.stringify(e).replace(`"tick":${e.tick},`,'')}</div>`
  ).join('');
}
async function getEvents(){ renderEvents((await fetch('/api/events')).json ? (await (await fetch('/api/events')).json()).events : []); }
async function action(url,method='POST',body=null){
  const r=await fetch(url,{method,headers:{'Content-Type':'application/json'},body:body?JSON.stringify(body):null});
  const data=await r.json(); if(data.status) render(data.status); return data;
}
async function resetFleet(){await action('/api/reset');}
async function injectBlock(){
  const x=prompt('x coordinate (0-21):','10'); const y=prompt('y coordinate (0-13):','7');
  if(x!==null&&y!==null) await action('/api/block','POST',{x:+x,y:+y});
}
async function forceConflict(){await action('/api/conflict');}
async function addTask(){
  const px=prompt('pickup x','3'); const py=prompt('pickup y','12');
  const dx=prompt('dropoff x','20'); const dy=prompt('dropoff y','1');
  if([px,py,dx,dy].every(v=>v!==null)) await action('/api/task','POST',{pickup_x:+px,pickup_y:+py,dropoff_x:+dx,dropoff_y:+dy});
}
async function runBenchmark(){
  const r=await fetch('/api/benchmark',{method:'POST'}); const b=await r.json();
  document.getElementById('benchmark').textContent=JSON.stringify(b,null,2);
}
function connect(){
  ws=new WebSocket(`ws://${location.host}/ws`);
  ws.onopen=()=>document.getElementById('connection').textContent='live';
  ws.onclose=()=>{document.getElementById('connection').textContent='reconnecting';setTimeout(connect,1000);}
  ws.onmessage=e=>render(JSON.parse(e.data));
}
connect();
