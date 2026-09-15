# API quick reference

All POST bodies are JSON.

- `GET /api/status` — current digital twin and metrics
- `GET /api/events` — persisted event stream
- `GET /api/health` — health/version
- `POST /api/reset` — reset with `{count: 5}`
- `POST /api/scale` — scale to 3–100 robots
- `POST /api/task` — create pickup/dropoff task
- `POST /api/fault` — kill `{robot_id:"AMR-1"}`
- `POST /api/recover` — recover a robot
- `POST /api/network` — isolate/reconnect a robot
- `POST /api/block` / `POST /api/unblock` — dynamic obstacle
- `POST /api/congestion` — set congestion 0–1
- `POST /api/packet-loss` — set packet loss 0–1
- `POST /api/conflict` — inject a narrow-intersection conflict
- `POST /api/benchmark` — distributed vs stop-and-wait comparison
- `POST /api/experiment` — run scalability experiment
- `WS /ws` — live fleet stream
