"""Unified ID generation for Socratic Agents"""

import uuid
from datetime import datetime, timezone
from typing import Optional


class ProjectIDGenerator:
    """Unified project ID generation"""

    FORMAT = "uuid"

    @classmethod
    def generate(cls, owner: Optional[str] = None) -> str:
        """Generate a project ID consistently"""
        if cls.FORMAT == "uuid":
            return cls._generate_uuid()
        elif cls.FORMAT == "timestamp":
            return cls._generate_timestamp(owner)
        else:
            raise ValueError(f"Unknown format: {cls.FORMAT}")

    @staticmethod
    def _generate_uuid() -> str:
        return f"proj_{str(uuid.uuid4())}"

    @staticmethod
    def _generate_timestamp(owner: Optional[str] = None) -> str:
        timestamp = int(datetime.now(timezone.utc).timestamp() * 1000)
        if owner:
            return f"proj_{owner}_{timestamp}"
        return f"proj_{timestamp}"


class UserIDGenerator:
    """Unified user ID generation"""

    @staticmethod
    def generate(username: Optional[str] = None) -> str:
        if username:
            return username
        return f"user_{str(uuid.uuid4())}"
