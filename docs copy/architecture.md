# Architecture and defense notes

## Core idea

Each AMR owns:

1. Its current state.
2. Its local A* planner.
3. Its task.
4. Its telemetry/anomaly model.
5. Its view of peer intent.
6. Its local conflict decision.

There is no central path planner in the simulation loop.

## P2P layer

The MVP uses an in-process message bus to keep the repository runnable on a normal laptop. The bus broadcasts robot intent messages, but route generation remains local to each robot.

For physical deployment, replace `PeerMessage` transport with ROS2 DDS, Zenoh or another peer-to-peer middleware.

## Conflict resolution

A robot proposes its next cell. If two robots want the same cell or want to swap positions, the lower-priority robot yields. The yielding robot replans on later ticks.

This is a deliberately understandable baseline for the hackathon MVP. A research-grade implementation should add:
- time-indexed reservations,
- aging/fairness to prevent starvation,
- deadlock graphs,
- priority inheritance,
- conflict-based search or prioritized MAPF,
- communication loss simulation.

## Edge AI

Every robot owns an `EdgeAnomalyDetector`. It is trained once from normal synthetic telemetry and then scores its own battery, temperature and speed locally. This demonstrates the placement of intelligence at the edge rather than sending raw telemetry to a central cloud model.

## Evaluation

The benchmark compares parallel distributed execution against a serialized stop-and-wait workload. The metric is task-time reduction, while the dashboard also exposes collisions and negotiation events.

Do not present the benchmark as a physical-world performance guarantee. It is a simulation result.
