from pydantic import BaseModel, Field
from typing import Optional, List

class TaskRequest(BaseModel):
    pickup: tuple[int, int] = (1, 1)
    dropoff: tuple[int, int] = (14, 14)
    priority: int = Field(default=5, ge=1, le=10)

class ScaleRequest(BaseModel):
    count: int = Field(ge=3, le=100)

class FaultRequest(BaseModel):
    robot_id: str

class NetworkRequest(BaseModel):
    robot_id: str
    enabled: bool = False

class BlockRequest(BaseModel):
    x: int
    y: int

class CongestionRequest(BaseModel):
    level: float = Field(ge=0, le=1)

class ExperimentRequest(BaseModel):
    robots: List[int] = [5, 10, 25, 50, 100]
    ticks: int = Field(default=250, ge=20, le=2000)

class PacketLossRequest(BaseModel):
    level: float = Field(ge=0, le=1)
