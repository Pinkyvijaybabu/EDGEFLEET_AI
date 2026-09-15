# EdgeFleet AI-X Architecture

## Goal
A reproducible research simulator for decentralized coordination of autonomous mobile robots (AMRs) in a warehouse. The simulator emphasizes local decisions, peer intent exchange, fault injection, AI telemetry risk scoring, dynamic rerouting and measurable scalability.

## Layers
1. **Digital twin** — grid warehouse, shelves, dynamic blocked cells and congestion.
2. **Robot edge agents** — local A* route planning, telemetry, task execution and local conflict yielding.
3. **Distributed coordination** — peer intent/state messages, network partitions, packet-loss parameter, distributed auction-style task assignment.
4. **Edge AI** — Isolation Forest anomaly score from battery, temperature, speed and load; risk changes robot state and affects task bids.
5. **Resilience** — robot failure/recovery, network isolation/reconnection, blocked aisle rerouting and low-battery shutdown.
6. **Cloud analytics simulation** — SQLite event/experiment persistence and repeatable scalability experiments. A real deployment can move this persistence/analytics to a cloud service.
7. **Observability** — REST API, WebSocket stream and dashboard.

## Research experiments
The experiment endpoint runs fleet sizes 5, 10, 25, 50 and 100 and records completed tasks, messages, negotiations, collisions and rates. This supports plots and statistical analysis in a thesis.

## Real-world migration
The current transport is an in-process simulation to remain reproducible on one laptop. For a physical deployment, replace it with ROS 2/DDS, Zenoh or another authenticated transport; use Gazebo/Webots/Isaac Sim for robotics simulation; and deploy edge agents on Jetson/Raspberry Pi-class devices.
