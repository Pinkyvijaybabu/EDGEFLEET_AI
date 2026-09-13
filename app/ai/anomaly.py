from __future__ import annotations

import numpy as np
from sklearn.ensemble import IsolationForest

class EdgeAnomalyDetector:
    """Tiny local model representing an anomaly detector running on each AMR."""

    def __init__(self, seed: int = 42):
        rng = np.random.default_rng(seed)
        normal = np.column_stack([
            rng.normal(75, 5, 500),   # battery %
            rng.normal(38, 2.5, 500), # temperature C
            rng.normal(1.0, .15, 500) # speed cells/s
        ])
        self.model = IsolationForest(
            n_estimators=80,
            contamination=0.06,
            random_state=seed
        )
        self.model.fit(normal)

    def score(self, battery: float, temperature: float, speed: float) -> tuple[bool, float]:
        x = np.array([[battery, temperature, speed]], dtype=float)
        prediction = int(self.model.predict(x)[0])
        raw = float(self.model.decision_function(x)[0])
        # Convert so larger magnitude/low raw values are more suspicious.
        risk = max(0.0, min(1.0, 0.5 - raw))
        return prediction == -1, round(risk, 3)
