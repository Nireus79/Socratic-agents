"""Helper utilities for safe orchestrator request execution"""

import logging
from typing import Any, Dict

logger = logging.getLogger(__name__)


def validate_orchestrator_result(
    result: Dict[str, Any], operation: str, log_errors: bool = True
) -> Dict[str, Any]:
    """Validate orchestrator request result"""
    if not isinstance(result, dict):
        error_msg = f"Orchestrator {operation} returned non-dict result: {type(result)}"
        if log_errors:
            logger.error(error_msg)
        raise ValueError(error_msg)

    status = result.get("status")
    if status != "success":
        error_msg = result.get("error", "Unknown error")
        if log_errors:
            logger.error(f"Orchestrator {operation} failed: {error_msg}")
        raise ValueError(f"Orchestrator {operation} failed: {error_msg}")

    return result


def safe_orchestrator_call(
    orchestrator: Any,
    agent: str,
    request_data: Dict[str, Any],
    operation_name: str,
    async_mode: bool = False,
) -> Dict[str, Any]:
    """Execute orchestrator call with validation and error handling"""
    try:
        logger.debug(f"Executing orchestrator {agent} for {operation_name}")

        if async_mode:
            result = orchestrator.process_request_async(agent, request_data)
        else:
            result = orchestrator.process_request(agent, request_data)

        validated = validate_orchestrator_result(result, operation_name)
        logger.debug(f"Orchestrator {operation_name} completed successfully")
        return validated

    except ValueError:
        raise
    except Exception as e:
        error_msg = f"Orchestrator {operation_name} raised exception: {str(e)}"
        logger.error(error_msg)
        raise


def get_or_default(
    result: Dict[str, Any], key: str, default: Any = None, log_missing: bool = True
) -> Any:
    """Safely extract value from orchestrator result"""
    keys = key.split(".")
    current: Any = result

    for k in keys:
        if isinstance(current, dict):
            current = current.get(k)
            if current is None:
                if log_missing:
                    logger.warning(f"Missing orchestrator result key: {k} (full: {key})")
                return default
        else:
            if log_missing:
                logger.warning(f"Cannot traverse orchestrator result at key: {k}")
            return default

    return current
