import numpy as np
from sklearn.ensemble import IsolationForest

class EdgeAnomalyEngine:
    """Small edge-side model trained on synthetic normal telemetry."""
    def __init__(self):
        rng=np.random.default_rng(42)
        normal=np.column_stack([
            rng.normal(80,8,400), rng.normal(45,3,400),
            rng.normal(1.0,.12,400), rng.normal(0.15,.03,400)])
        self.model=IsolationForest(contamination=0.06, random_state=42)
        self.model.fit(normal)

    def score(self, battery, temperature, speed, load):
        x=np.array([[battery,temperature,speed,load]])
        raw=float(-self.model.decision_function(x)[0])
        risk=max(0.0,min(1.0,0.5+raw*2.0))
        return round(risk,3)
