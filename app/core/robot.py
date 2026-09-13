from __future__ import annotations

import random
from dataclasses import dataclass, field
from typing import Optional

from app.ai.anomaly import EdgeAnomalyDetector
from app.core.grid import Point, WarehouseGrid

@dataclass
class PeerMessage:
    sender: str
    kind: str
    position: Point
    intent: Optional[Point] = None
    priority: int = 0

@dataclass
class Robot:
    robot_id: str
    position: Point
    battery: float
    priority: int
    grid: WarehouseGrid
    rng: random.Random
    task_id: Optional[str] = None
    pickup: Optional[Point] = None
    dropoff: Optional[Point] = None
    path: list[Point] = field(default_factory=list)
    state: str = "idle"
    temperature: float = 37.0
    speed: float = 1.0
    anomaly: bool = False
    anomaly_score: float = 0.0
    messages_seen: int = 0
    distance: int = 0
    detector: EdgeAnomalyDetector = field(default_factory=EdgeAnomalyDetector)

    def assign(self, task_id: str, pickup: Point, dropoff: Point):
        self.task_id = task_id
        self.pickup = pickup
        self.dropoff = dropoff
        self.state = "to_pickup"
        self.replan()

    def current_goal(self) -> Optional[Point]:
        if self.state == "to_pickup":
            return self.pickup
        if self.state == "to_dropoff":
            return self.dropoff
        return None

    def replan(self):
        goal = self.current_goal()
        if goal is None:
            self.path = []
            return
        self.path = self.grid.astar(self.position, goal)

    def receive(self, msg: PeerMessage):
        self.messages_seen += 1

    def intent(self) -> Optional[Point]:
        return self.path[1] if len(self.path) > 1 else None

    def telemetry(self):
        # Mostly healthy, with a small chance of local sensor drift.
        self.temperature += self.rng.uniform(-0.35, 0.35)
        self.temperature = max(32, min(58, self.temperature))
        self.speed = max(0.0, 1.0 + self.rng.uniform(-0.12, 0.12))
        self.battery = max(0.0, self.battery - 0.025 * self.speed)
        if self.rng.random() < 0.012:
            self.temperature += self.rng.uniform(7, 13)
        self.anomaly, self.anomaly_score = self.detector.score(
            self.battery, self.temperature, self.speed
        )

    def step(self, allowed: bool):
        self.telemetry()
        if not self.path or self.state == "idle":
            return
        if not allowed:
            self.state = "yielding"
            return
        self.state = "moving"
        nxt = self.path[1] if len(self.path) > 1 else self.path[0]
        if nxt != self.position:
            self.position = nxt
            self.distance += 1
            self.battery = max(0, self.battery - 0.12)
        self.path = self.path[1:] if self.path else []
        goal = self.current_goal()
        if goal is not None and self.position == goal:
            if self.state == "moving" and self.pickup == self.position:
                self.state = "to_dropoff"
                self.replan()
            elif self.state == "moving" and self.dropoff == self.position:
                self.state = "idle"
                self.task_id = None
                self.pickup = None
                self.dropoff = None
                self.path = []
