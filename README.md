# EdgeFleet AI-X

**Decentralized Edge-AI Fleet Coordination and Resilience Laboratory for Autonomous Mobile Robots (AMRs)**

> A research-grade software simulation built from the original EdgeFleet AI MVP. It is designed to demonstrate decentralized coordination, AI-assisted fleet resilience, dynamic rerouting and scalability from 5 to 100 simulated AMRs.

## What makes this the full project

- **5–100 AMRs** with one-click fleet scaling
- Local **A*** route planning for every robot
- Distributed auction-style task allocation using local robot bids
- Peer intent/state exchange with configurable network isolation and packet-loss model
- Local conflict negotiation and yielding
- Dynamic aisle blocking and rerouting
- **Robot kill/recovery** fault injection
- **Network node disconnect/reconnect** fault injection
- Congestion-aware route cost
- Edge-side **Isolation Forest anomaly detection** on battery, temperature, speed and load
- Risk-aware task assignment and predictive low-battery shutdown
- Live WebSocket digital twin dashboard
- REST API + interactive `/docs`
- SQLite event and experiment history
- Automated **5→100 robot scalability experiment**
- Comparative distributed vs stop-and-wait benchmark
- Unit tests and Docker support

## Important scope statement

This is a **software simulation/research prototype**, not a physical robot controller. Claims about collisions, speedup or recovery apply only to the simulated workload. The transport layer is intentionally replaceable with ROS 2/DDS, Zenoh or another real communication stack for hardware experiments.

## Run in VS Code (Windows)

```powershell
python -m venv .venv
.\.venv\Scripts\python.exe -m pip install -r requirements.txt
.\.venv\Scripts\python.exe run.py
```

Open `http://127.0.0.1:8000` and API docs at `http://127.0.0.1:8000/docs`.

## Demo sequence

1. Watch the fleet move and complete tasks.
2. **Block Aisle** to trigger rerouting.
3. **Force Conflict** to trigger local negotiation.
4. Select a robot and **Kill Robot**; observe task reassignment/failure state.
5. **Disconnect Node**; observe network isolation.
6. **Recover Robot** / **Reconnect Node**.
7. Run **Benchmark**.
8. Run **Scalability Experiment** to evaluate 5, 10, 25, 50 and 100 robots.

## API highlights

- `GET /api/status`
- `POST /api/scale`
- `POST /api/task`
- `POST /api/fault`
- `POST /api/recover`
- `POST /api/network`
- `POST /api/block`
- `POST /api/unblock`
- `POST /api/congestion`
- `POST /api/conflict`
- `POST /api/benchmark`
- `POST /api/experiment`
- `GET /api/events`
- `WS /ws`

## Research questions

1. How does decentralized task allocation affect throughput as fleet size grows?
2. How does network isolation affect task completion and communication overhead?
3. Can local anomaly risk reduce assignment of risky robots to new tasks?
4. How quickly can the fleet recover after robot or aisle failures?
5. What is the communication overhead of decentralized coordination compared with serialized execution?

## Suggested thesis evaluation

Measure task completion time, throughput, collision count, recovery time, message overhead, robot utilization, anomaly detection precision/recall (when labeled failure data is introduced), and scalability across repeated trials. Report mean, standard deviation and confidence intervals rather than a single run.

## Project structure

```text
edgefleet_ai/
├── app/
│   ├── ai/anomaly.py
│   ├── core/grid.py
│   ├── core/robot.py
│   ├── core/fleet.py
│   ├── storage/db.py
│   ├── main.py
│   └── models.py
├── static/
├── tests/
├── scripts/
├── docs/
├── requirements.txt
├── Dockerfile
├── docker-compose.yml
├── .gitignore
└── run.py
```

## Future physical integration

A hardware-ready extension would replace the simulated message bus with ROS 2/DDS or Zenoh, connect telemetry from LiDAR/IMU/encoders, use a robotics simulator or AMR hardware, and deploy cloud analytics separately from safety-critical edge control.
