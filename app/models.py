from typing import List, Tuple, Optional
from pydantic import BaseModel, Field

Point = Tuple[int, int]

class Task(BaseModel):
    task_id: str
    pickup: Point
    dropoff: Point
    status: str = "pending"
    assigned_to: Optional[str] = None

class RobotSnapshot(BaseModel):
    robot_id: str
    x: int
    y: int
    battery: float
    temperature: float
    speed: float
    state: str
    task_id: Optional[str] = None
    anomaly: bool = False
    anomaly_score: float = 0.0
    path_length: int = 0
    priority: int = 0

class FleetSnapshot(BaseModel):
    tick: int
    robots: List[RobotSnapshot]
    blocked: List[Point]
    tasks: List[Task]
    completed_tasks: int
    collisions: int
    deadlocks_resolved: int
    messages: int
    elapsed_sim_seconds: float

class BlockRequest(BaseModel):
    x: int = Field(ge=0)
    y: int = Field(ge=0)

class TaskRequest(BaseModel):
    pickup_x: int = Field(ge=0)
    pickup_y: int = Field(ge=0)
    dropoff_x: int = Field(ge=0)
    dropoff_y: int = Field(ge=0)
