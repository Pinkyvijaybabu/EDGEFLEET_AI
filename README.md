# EdgeFleet AI — Decentralized Edge-AI Fleet Coordination

**SIH 2026 reference:** SIH26123 — *Edge-AI Based Distributed Fleet Coordination for Autonomous Mobile Robots (AMRs) in Smart Warehouses*, Bharat Electronics Limited.

EdgeFleet AI is a complete local simulation/demo of a multi-AMR warehouse where every robot maintains its own route, shares intent with peers, detects local telemetry anomalies, negotiates conflicts, reroutes around blocked aisles, and exposes a live fleet dashboard.

The design directly targets the SIH requirements: at least 3 AMRs, decentralized communication, dynamic conflict/deadlock handling, task allocation/rerouting, and a lightweight dashboard.

## What is implemented

- 5 autonomous robots in a warehouse grid
- Peer-to-peer intent/state exchange through an in-process message bus
- Local A* path planning on every robot
- Spatio-temporal reservation negotiation
- Local priority-based conflict resolution
- Dynamic blocked-aisle injection and rerouting
- Task pickup/drop-off simulation
- Local Edge-AI telemetry anomaly detection using Isolation Forest
- Battery/temperature/speed telemetry
- Live WebSocket dashboard
- Benchmark mode against a stop-and-wait baseline
- Event log
- REST API for status, reset, block/unblock, tasks and benchmark
- Docker support
- Unit tests

> This repository is a simulation/MVP. It does not claim that the simulated communication layer is a physical ROS2/DDS network. The architecture is deliberately modular so the message bus can later be replaced with ROS2 DDS, Zenoh, MQTT or another real P2P transport.

## Quick start — VS Code

### 1. Requirements

- Python 3.11+
- VS Code
- Git

### 2. Open the project

Open the `edgefleet_ai` folder in VS Code.

### 3. Create a virtual environment

Windows PowerShell:

```powershell
python -m venv .venv
.venv\Scripts\Activate.ps1
```

Windows CMD:

```cmd
python -m venv .venv
.venv\Scripts\activate
```

macOS/Linux:

```bash
python3 -m venv .venv
source .venv/bin/activate
```

### 4. Install

```bash
pip install -r requirements.txt
```

### 5. Run

```bash
python run.py
```

Open:

```text
http://127.0.0.1:8000
```

API docs:

```text
http://127.0.0.1:8000/docs
```

## Demo flow

1. Start the application.
2. Watch the 5 robots move independently.
3. Click **Block aisle** to inject a dynamic obstruction.
4. Robots detect the blocked edge and locally reroute.
5. Use **Force conflict** to create a narrow-intersection negotiation.
6. Watch the lower-priority robot yield while the other proceeds.
7. Click **Benchmark** to compare the distributed strategy with the stop-and-wait baseline.
8. Inspect anomaly badges when synthetic telemetry is pushed outside the learned normal range.

## Architecture

```text
             ┌───────────────────────────────┐
             │       Fleet Dashboard         │
             │  Grid + battery + anomalies   │
             └──────────────┬────────────────┘
                            │ WebSocket
                            ▼
┌────────────────────────────────────────────────────────────┐
│                    Simulation Runtime                       │
│                                                            │
│  Robot 1        Robot 2        Robot 3 ... Robot 5         │
│  ┌───────┐      ┌───────┐      ┌───────┐                  │
│  │ A*    │      │ A*    │      │ A*    │                  │
│  │ local │      │ local │      │ local │                  │
│  │ AI    │      │ AI    │      │ AI    │                  │
│  └──┬────┘      └──┬────┘      └──┬────┘                  │
│     │ P2P state/intent messages       │                    │
│     └──────────────┬─────────────────┘                    │
│                    ▼                                      │
│             Local negotiation                              │
│       reservation + priority + yielding                    │
└────────────────────────────────────────────────────────────┘
```

## Main project structure

```text
edgefleet_ai/
├── app/
│   ├── ai/anomaly.py
│   ├── core/grid.py
│   ├── core/robot.py
│   ├── core/fleet.py
│   ├── main.py
│   └── models.py
├── static/
│   ├── index.html
│   ├── style.css
│   └── app.js
├── scripts/benchmark.py
├── tests/test_grid.py
├── docs/architecture.md
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .gitignore
└── run.py
```

## API

- `GET /api/status`
- `POST /api/reset`
- `POST /api/block`
- `POST /api/unblock`
- `POST /api/conflict`
- `POST /api/task`
- `POST /api/benchmark`
- `GET /api/events`
- `WS /ws`

## GitHub

After you verify the demo:

```bash
git init
git add .
git commit -m "Initial EdgeFleet AI implementation"
git branch -M main
git remote add origin https://github.com/YOUR_USERNAME/edgefleet-ai.git
git push -u origin main
```

Do not commit `.venv`, secrets, API keys, or credentials.

## Extension path

For a stronger SIH/hackathon version, replace the simulated message bus with ROS2 DDS or Zenoh, connect each robot process to an actual Raspberry Pi/Jetson, replace grid motion with ROS2 Nav2/Gazebo, and use a real LiDAR/IMU telemetry stream.

## SIH alignment

The SIH26123 problem statement asks for decentralized communication, conflict resolution, task allocation/rerouting and a fleet dashboard for at least three AMRs. EdgeFleet AI provides those functions in a reproducible software simulation and exposes measurable task-completion metrics.

