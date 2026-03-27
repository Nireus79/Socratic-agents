"""Serialization utilities for socratic-agents package."""

from datetime import datetime
from typing import Any, Dict, Optional


def parse_iso_datetime(value: Any) -> Optional[datetime]:
    """
    Parse ISO format datetime string to datetime object.

    Args:
        value: Value to parse (datetime, ISO string, or None)

    Returns:
        datetime object or None
    """
    if value is None:
        return None
    if isinstance(value, datetime):
        return value
    if isinstance(value, str):
        return datetime.fromisoformat(value)
    return None


def ensure_iso_datetime(data: Dict[str, Any], *date_fields: str) -> Dict[str, Any]:
    """
    Convert ISO datetime strings in dict to datetime objects.

    Args:
        data: Dictionary potentially containing datetime strings
        *date_fields: Field names to parse as datetimes

    Returns:
        Updated dictionary with parsed datetimes (doesn't modify original)
    """
    result = dict(data)
    for field in date_fields:
        if field in result:
            result[field] = parse_iso_datetime(result[field])
    return result
