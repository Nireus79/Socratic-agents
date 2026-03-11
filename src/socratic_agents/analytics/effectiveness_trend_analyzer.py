"""Effectiveness Trend Analyzer for tracking and analyzing skill effectiveness trends."""

import logging
import statistics
from datetime import datetime, UTC
from typing import Dict, List, Optional, Any
from collections import defaultdict


class EffectivenessTrendAnalyzer:
    """Analyzes trends in skill effectiveness over time."""

    def __init__(self):
        """Initialize the EffectivenessTrendAnalyzer."""
        self.logger = logging.getLogger(f"socratic_agents.{self.__class__.__name__}")
        self._effectiveness_data: Dict[str, List[Dict[str, Any]]] = defaultdict(list)

    def record_effectiveness_data(
        self, skill_id: str, effectiveness: float, timestamp: Optional[str] = None
    ) -> None:
        """Record effectiveness data for a skill."""
        if not (0.0 <= effectiveness <= 1.0):
            raise ValueError("effectiveness must be between 0.0 and 1.0")

        ts = timestamp or datetime.now(UTC).isoformat()
        
        data_point = {"effectiveness": effectiveness, "timestamp": ts}
        self._effectiveness_data[skill_id].append(data_point)

    def get_moving_average(self, skill_id: str, window_size: int = 5) -> List[float]:
        """Calculate moving average for a skill."""
        if skill_id not in self._effectiveness_data:
            return []
        data = self._effectiveness_data[skill_id]
        if len(data) < window_size:
            return []
        moving_averages = []
        for i in range(len(data) - window_size + 1):
            window = data[i : i + window_size]
            avg = sum(d["effectiveness"] for d in window) / window_size
            moving_averages.append(avg)
        return moving_averages

    def calculate_trend(self, skill_id: str, window_size: int = 5) -> Dict[str, Any]:
        """Calculate trend for a skill effectiveness."""
        if skill_id not in self._effectiveness_data:
            raise ValueError(f"No data found for skill: {skill_id}")
        data = self._effectiveness_data[skill_id]
        if len(data) < window_size:
            raise ValueError(f"Insufficient data for trend analysis. Need {window_size}, found {len(data)}")
        moving_avgs = self.get_moving_average(skill_id, window_size)
        if len(moving_avgs) < 2:
            raise ValueError("Insufficient moving averages for trend calculation")
        slope = (moving_avgs[-1] - moving_avgs[0]) / len(moving_avgs)
        threshold = 0.01
        if slope > threshold:
            trend = "improving"
        elif slope < -threshold:
            trend = "declining"
        else:
            trend = "stable"
        return {
            "trend": trend,
            "slope": slope,
            "moving_averages": moving_avgs,
            "current_effectiveness": data[-1]["effectiveness"],
        }

    def detect_anomalies(
        self, skill_id: str, threshold: float = 2.0
    ) -> List[Dict[str, Any]]:
        """Detect anomalies in skill effectiveness data."""
        if skill_id not in self._effectiveness_data:
            return []
        data = self._effectiveness_data[skill_id]
        if len(data) < 2:
            return []
        moving_avgs = self.get_moving_average(skill_id, 5)
        if not moving_avgs:
            return []
        effectiveness_values = [d["effectiveness"] for d in data]
        std_dev = statistics.stdev(effectiveness_values)
        if std_dev == 0:
            return []
        anomalies = []
        for i, avg in enumerate(moving_avgs):
            for j in range(i, min(i + 5, len(data))):
                value = data[j]["effectiveness"]
                deviation = abs(value - avg)
                if deviation > threshold * std_dev:
                    anomalies.append({
                        "index": j,
                        "value": value,
                        "moving_average": avg,
                        "deviation": deviation,
                        "timestamp": data[j]["timestamp"],
                    })
        return anomalies

    def forecast_effectiveness(self, skill_id: str, periods: int = 5) -> List[float]:
        """Forecast future effectiveness using linear regression."""
        if skill_id not in self._effectiveness_data:
            raise ValueError(f"No data found for skill: {skill_id}")
        data = self._effectiveness_data[skill_id]
        if len(data) < 2:
            raise ValueError("Need at least 2 data points for forecasting")
        x_values = list(range(len(data)))
        y_values = [d["effectiveness"] for d in data]
        x_mean = statistics.mean(x_values)
        y_mean = statistics.mean(y_values)
        numerator = sum((x_values[i] - x_mean) * (y_values[i] - y_mean) for i in range(len(x_values)))
        denominator = sum((x - x_mean) ** 2 for x in x_values)
        slope = 0 if denominator == 0 else numerator / denominator
        intercept = y_mean - slope * x_mean
        forecasts = []
        for period in range(1, periods + 1):
            x = len(data) + period - 1
            y = intercept + slope * x
            y = max(0.0, min(1.0, y))
            forecasts.append(y)
        return forecasts

    def get_effectiveness_statistics(self, skill_id: str) -> Dict[str, float]:
        """Get statistical summary of effectiveness data."""
        if skill_id not in self._effectiveness_data:
            raise ValueError(f"No data found for skill: {skill_id}")
        data = self._effectiveness_data[skill_id]
        if len(data) < 1:
            raise ValueError("No effectiveness data available")
        effectiveness_values = [d["effectiveness"] for d in data]
        min_val = min(effectiveness_values)
        max_val = max(effectiveness_values)
        mean_val = statistics.mean(effectiveness_values)
        median_val = statistics.median(effectiveness_values)
        std_dev = 0.0 if len(effectiveness_values) <= 1 else statistics.stdev(effectiveness_values)
        coef_variation = (std_dev / mean_val * 100) if mean_val > 0 else 0.0
        return {
            "min": min_val,
            "max": max_val,
            "mean": mean_val,
            "median": median_val,
            "std_dev": std_dev,
            "coefficient_variation": coef_variation,
        }

    def compare_skills(self, skill_ids: List[str]) -> Dict[str, Any]:
        """Compare effectiveness across multiple skills."""
        if not skill_ids:
            raise ValueError("skill_ids cannot be empty")
        comparison = {}
        for skill_id in skill_ids:
            try:
                stats = self.get_effectiveness_statistics(skill_id)
                comparison[skill_id] = stats
            except ValueError:
                continue
        if not comparison:
            raise ValueError("No valid skills found with data")
        best_performer = max(comparison, key=lambda k: comparison[k]["mean"])
        ranking = sorted(comparison.keys(), key=lambda k: comparison[k]["mean"], reverse=True)
        return {"comparison": comparison, "best_performer": best_performer, "ranking": ranking}

    def get_effectiveness_data(self, skill_id: str) -> List[Dict[str, Any]]:
        """Get all effectiveness data for a skill."""
        return self._effectiveness_data.get(skill_id, []).copy()

    def clear_data(self, skill_id: Optional[str] = None) -> None:
        """Clear effectiveness data."""
        if skill_id is None:
            self._effectiveness_data.clear()
        elif skill_id in self._effectiveness_data:
            del self._effectiveness_data[skill_id]

    def get_all_skills(self) -> List[str]:
        """Get list of all skills with recorded data."""
        return list(self._effectiveness_data.keys())
