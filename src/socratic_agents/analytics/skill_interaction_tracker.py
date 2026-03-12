"""Skill Interaction Tracker for analyzing skill combinations and synergies."""

import logging
from collections import defaultdict
from datetime import datetime, timezone
from typing import Dict, List, Optional, Tuple


class SkillInteractionTracker:
    """Tracks skill interactions and identifies synergies and conflicts."""

    def __init__(self):
        """Initialize the SkillInteractionTracker."""
        self.logger = logging.getLogger(f"socratic_agents.{self.__class__.__name__}")
        self._interaction_history: List[Dict] = []
        self._interaction_matrix: Optional[Dict[str, Dict[str, float]]] = None
        self._skill_pair_stats: Dict[Tuple[str, str], List[float]] = defaultdict(list)

    def record_skill_interaction(
        self, skill_ids: List[str], effectiveness: float, timestamp: Optional[str] = None
    ) -> None:
        """Record a skill interaction event."""
        if not skill_ids:
            raise ValueError("skill_ids cannot be empty")
        if len(skill_ids) < 2:
            raise ValueError("At least 2 skills required for interaction recording")
        if not (0.0 <= effectiveness <= 1.0):
            raise ValueError("effectiveness must be between 0.0 and 1.0")

        ts = timestamp or datetime.now(timezone.utc).isoformat()

        interaction_record = {
            "skill_ids": sorted(skill_ids),
            "effectiveness": effectiveness,
            "timestamp": ts,
        }
        self._interaction_history.append(interaction_record)

        unique_skills = set(skill_ids)
        for i, skill_a in enumerate(sorted(unique_skills)):
            for skill_b in sorted(unique_skills)[i + 1 :]:
                pair_key = (skill_a, skill_b)
                self._skill_pair_stats[pair_key].append(effectiveness)

        self._interaction_matrix = None

    def get_interaction_matrix(self) -> Dict[str, Dict[str, float]]:
        """Get the interaction matrix showing average effectiveness."""
        if self._interaction_matrix is not None:
            return self._interaction_matrix

        matrix: Dict[str, Dict[str, float]] = defaultdict(dict)

        for (skill_a, skill_b), effectiveness_scores in self._skill_pair_stats.items():
            avg_effectiveness = sum(effectiveness_scores) / len(effectiveness_scores)
            matrix[skill_a][skill_b] = avg_effectiveness
            matrix[skill_b][skill_a] = avg_effectiveness

        self._interaction_matrix = {k: dict(v) for k, v in matrix.items()}
        return self._interaction_matrix

    def identify_skill_synergies(self, threshold: float = 0.7) -> List[Tuple[str, str, float]]:
        """Identify skill synergies (positive interactions above threshold)."""
        if not (0.0 <= threshold <= 1.0):
            raise ValueError("threshold must be between 0.0 and 1.0")

        synergies: List[Tuple[str, str, float]] = []
        interaction_matrix = self.get_interaction_matrix()

        processed_pairs = set()
        for skill_a, pairs in interaction_matrix.items():
            for skill_b, score in pairs.items():
                pair = tuple(sorted([skill_a, skill_b]))
                if pair in processed_pairs:
                    continue
                if score >= threshold:
                    synergies.append((*pair, score))
                    processed_pairs.add(pair)

        synergies.sort(key=lambda x: x[2], reverse=True)
        return synergies

    def identify_skill_conflicts(self, threshold: float = 0.3) -> List[Tuple[str, str, float]]:
        """Identify skill conflicts (negative interactions below threshold)."""
        if not (0.0 <= threshold <= 1.0):
            raise ValueError("threshold must be between 0.0 and 1.0")

        conflicts: List[Tuple[str, str, float]] = []
        interaction_matrix = self.get_interaction_matrix()

        processed_pairs = set()
        for skill_a, pairs in interaction_matrix.items():
            for skill_b, score in pairs.items():
                pair = tuple(sorted([skill_a, skill_b]))
                if pair in processed_pairs:
                    continue
                if score <= threshold:
                    conflicts.append((*pair, score))
                    processed_pairs.add(pair)

        conflicts.sort(key=lambda x: x[2])
        return conflicts

    def get_best_skill_combination(self, category: Optional[str] = None) -> List[str]:
        """Get the best performing skill combination."""
        if not self._interaction_history:
            return []

        best_interaction = max(self._interaction_history, key=lambda x: x["effectiveness"])

        return best_interaction["skill_ids"]

    def get_interaction_strength(self, skill_id_1: str, skill_id_2: str) -> float:
        """Get the interaction strength between two skills."""
        pair_key = tuple(sorted([skill_id_1, skill_id_2]))

        if pair_key not in self._skill_pair_stats:
            return 0.0

        scores = self._skill_pair_stats[pair_key]
        return sum(scores) / len(scores) if scores else 0.0

    def get_interaction_history(self) -> List[Dict]:
        """Get the complete interaction history."""
        return self._interaction_history.copy()

    def clear_history(self) -> None:
        """Clear all interaction history and reset caches."""
        self._interaction_history.clear()
        self._skill_pair_stats.clear()
        self._interaction_matrix = None

    def get_statistics(self) -> Dict:
        """Get overall statistics about recorded interactions."""
        if not self._interaction_history:
            return {
                "total_interactions": 0,
                "unique_skills": 0,
                "unique_skill_pairs": 0,
                "average_effectiveness": 0.0,
                "min_effectiveness": 0.0,
                "max_effectiveness": 0.0,
            }

        all_skills = set()
        all_effectiveness = []

        for interaction in self._interaction_history:
            all_skills.update(interaction["skill_ids"])
            all_effectiveness.append(interaction["effectiveness"])

        return {
            "total_interactions": len(self._interaction_history),
            "unique_skills": len(all_skills),
            "unique_skill_pairs": len(self._skill_pair_stats),
            "average_effectiveness": sum(all_effectiveness) / len(all_effectiveness),
            "min_effectiveness": min(all_effectiveness),
            "max_effectiveness": max(all_effectiveness),
        }
