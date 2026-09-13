from __future__ import annotations

import asyncio
from pathlib import Path

from fastapi import FastAPI, WebSocket, WebSocketDisconnect
from fastapi.responses import FileResponse
from fastapi.staticfiles import StaticFiles
from fastapi.middleware.cors import CORSMiddleware

from app.core.fleet import Fleet
from app.models import BlockRequest, TaskRequest

BASE = Path(__file__).resolve().parent.parent
app = FastAPI(title="EdgeFleet AI", version="1.0.0")
app.mount("/static", StaticFiles(directory=BASE / "static"), name="static")

app.add_middleware(
    CORSMiddleware,
    allow_origins=["*"],
    allow_methods=["*"],
    allow_headers=["*"],
)

fleet = Fleet()
clients: set[WebSocket] = set()

@app.get("/")
def index():
    return FileResponse(BASE / "static" / "index.html")

@app.get("/api/status")
def status():
    return fleet.snapshot()

@app.get("/api/events")
def events():
    return {"events": fleet.events[-100:]}

@app.post("/api/reset")
def reset():
    fleet.reset()
    return fleet.snapshot()

@app.post("/api/block")
def block(req: BlockRequest):
    return {"success": fleet.block((req.x, req.y)), "status": fleet.snapshot()}

@app.post("/api/unblock")
def unblock(req: BlockRequest):
    fleet.unblock((req.x, req.y))
    return {"success": True, "status": fleet.snapshot()}

@app.post("/api/conflict")
def conflict():
    fleet.force_conflict()
    return {"success": True, "status": fleet.snapshot()}

@app.post("/api/task")
def task(req: TaskRequest):
    tid = fleet.add_task(
        (req.pickup_x, req.pickup_y),
        (req.dropoff_x, req.dropoff_y)
    )
    return {"task_id": tid, "status": fleet.snapshot()}

@app.post("/api/benchmark")
def benchmark():
    return fleet.benchmark()

async def simulation_loop():
    while True:
        fleet.tick()
        if clients:
            payload = fleet.snapshot()
            dead = []
            for ws in clients:
                try:
                    await ws.send_json(payload)
                except Exception:
                    dead.append(ws)
            for ws in dead:
                clients.discard(ws)
        await asyncio.sleep(0.25)

@app.on_event("startup")
async def startup():
    asyncio.create_task(simulation_loop())

@app.websocket("/ws")
async def websocket(ws: WebSocket):
    await ws.accept()
    clients.add(ws)
    try:
        await ws.send_json(fleet.snapshot())
        while True:
            await ws.receive_text()
    except WebSocketDisconnect:
        clients.discard(ws)
    except Exception:
        clients.discard(ws)
