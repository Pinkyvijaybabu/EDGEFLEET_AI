from dataclasses import dataclass, field
from random import Random

@dataclass
class Robot:
    robot_id: str
    pos: tuple[int,int]
    battery: float=100.0
    temperature: float=43.0
    speed: float=1.0
    load: float=0.0
    alive: bool=True
    connected: bool=True
    task_id: str|None=None
    path: list[tuple[int,int]]=field(default_factory=list)
    goal: tuple[int,int]|None=None
    anomaly_risk: float=0.0
    state: str='idle'
    wait_ticks: int=0
    completed: int=0
    rng: Random=field(default_factory=Random, repr=False)

    def telemetry(self):
        return {'battery':round(self.battery,1),'temperature':round(self.temperature,1),'speed':round(self.speed,2),'load':round(self.load,2),'anomaly_risk':self.anomaly_risk}

    def tick_energy(self):
        if not self.alive: return
        self.battery=max(0.0,self.battery-(0.035+0.018*self.load+0.02*(self.speed>0)))
        self.temperature += (0.05 if self.speed>0 else -0.08) + self.rng.uniform(-0.03,0.03)
        self.temperature=max(30,min(75,self.temperature))
