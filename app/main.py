import asyncio, json
from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from .core.fleet import FleetRuntime
from .models import TaskRequest, ScaleRequest, FaultRequest, NetworkRequest, BlockRequest, CongestionRequest, ExperimentRequest, PacketLossRequest

app=FastAPI(title='EdgeFleet AI-X', version='2.0.0', description='Research-grade simulation of decentralized edge-AI AMR fleet coordination.')
fleet=FleetRuntime()
app.mount('/static',StaticFiles(directory='static'),name='static')

@app.get('/')
def home(): return FileResponse('static/index.html')
@app.get('/api/status')
def status(): return fleet.status()
@app.post('/api/reset')
def reset(req:ScaleRequest|None=None): fleet.reset(req.count if req else 5); return fleet.status()
@app.post('/api/scale')
def scale(req:ScaleRequest): fleet.scale(req.count); return fleet.status()
@app.post('/api/task')
def task(req:TaskRequest): return fleet.add_task(req.pickup,req.dropoff,req.priority)
@app.post('/api/block')
def block(req:BlockRequest): fleet.block((req.x,req.y)); return {'ok':True}
@app.post('/api/unblock')
def unblock(req:BlockRequest): fleet.unblock((req.x,req.y)); return {'ok':True}
@app.post('/api/fault')
def fault(req:FaultRequest): fleet.fault_robot(req.robot_id); return {'ok':True}
@app.post('/api/recover')
def recover(req:FaultRequest): fleet.recover_robot(req.robot_id); return {'ok':True}
@app.post('/api/network')
def network(req:NetworkRequest): fleet.partition(req.robot_id,req.enabled); return {'ok':True}
@app.post('/api/congestion')
def congestion(req:CongestionRequest): fleet.set_congestion(req.level); return {'ok':True}
@app.post('/api/packet-loss')
def packet_loss(req:PacketLossRequest): fleet.packet_loss=req.level; fleet.log('WARN' if req.level>0 else 'INFO','packet_loss_changed',{'level':req.level}); return {'ok':True,'packet_loss':req.level}
@app.post('/api/conflict')
def conflict(): fleet.force_conflict(); return {'ok':True}
@app.post('/api/benchmark')
def benchmark(): return fleet.benchmark()
@app.post('/api/experiment')
def experiment(req:ExperimentRequest): return {'results':fleet.run_experiment(req.robots,req.ticks)}
@app.get('/api/events')
def events(): return fleet.db.recent(100)
@app.get('/api/health')
def health(): return {'status':'ok','tick':fleet.tick_count,'version':app.version}

@app.websocket('/ws')
async def websocket(ws:WebSocket):
    await ws.accept()
    try:
        while True:
            await ws.send_text(json.dumps(fleet.status()))
            await asyncio.sleep(.25)
    except (WebSocketDisconnect, RuntimeError): pass
