# M.E. Research Plan

## Proposed title
**EdgeFleet AI-X: Fault-Tolerant Decentralized Edge-AI Coordination for Scalable Autonomous Mobile Robot Fleets**

## Hypothesis
A decentralized coordination strategy with local AI risk scoring can maintain task throughput and resilience under robot failures, network isolation, congestion and dynamic obstacles while reducing dependence on a central controller.

## Independent variables
- Fleet size: 5, 10, 25, 50, 100
- Packet loss: 0–50%
- Congestion: 0–100%
- Robot failures: injected at controlled ticks
- Dynamic blocked aisles

## Dependent variables
- Task completion time
- Throughput
- Collision count
- Recovery time
- P2P message overhead
- Negotiation count
- Active-robot utilization
- AI risk and false-alert rate (after adding labeled failure traces)

## Baselines
1. Stop-and-wait serialized execution.
2. Centralized task allocation baseline.
3. Decentralized allocation without AI risk score.
4. Full EdgeFleet AI-X.

## Experimental protocol
Use fixed random seeds, repeated trials, and report mean ± standard deviation. For stronger thesis results, run at least 20 repetitions per configuration and use confidence intervals. Never report a single synthetic run as a real-world guarantee.

## Novel engineering contribution
The project combines decentralized peer coordination, fault injection, risk-aware task bidding, dynamic rerouting and edge/cloud separation in one reproducible experimental laboratory. The novelty claim should be validated with a formal literature and patent review before being stated as a research novelty claim.
