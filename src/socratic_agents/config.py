"""Configuration system for governed agents."""

from dataclasses import dataclass, field
from typing import Any, Dict, Optional
from pathlib import Path
import yaml


@dataclass
class GovernanceConfig:
    """Configuration for governance system."""

    constitution_path: Optional[str] = None
    constitution_dict: Optional[Dict[str, Any]] = None
    llm_provider: str = "anthropic"
    require_human_approval: bool = False
    enable_precedent_storage: bool = True
    audit_logging: bool = True

    @classmethod
    def from_file(cls, path: str) -> "GovernanceConfig":
        """Load governance config from file."""
        config_file = Path(path)
        if not config_file.exists():
            raise FileNotFoundError(f"Config file not found: {path}")

        with open(config_file) as f:
            data = yaml.safe_load(f)

        return cls(**data)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "GovernanceConfig":
        """Create governance config from dictionary."""
        return cls(**data)

    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary."""
        return {
            "constitution_path": self.constitution_path,
            "constitution_dict": self.constitution_dict,
            "llm_provider": self.llm_provider,
            "require_human_approval": self.require_human_approval,
            "enable_precedent_storage": self.enable_precedent_storage,
            "audit_logging": self.audit_logging,
        }


@dataclass
class AgentConfig:
    """Configuration for individual agents."""

    name: str
    agent_type: str
    enabled: bool = True
    require_governance: bool = True
    capabilities: list = field(default_factory=list)
    parameters: Dict[str, Any] = field(default_factory=dict)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "AgentConfig":
        """Create agent config from dictionary."""
        return cls(**data)

    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary."""
        return {
            "name": self.name,
            "agent_type": self.agent_type,
            "enabled": self.enabled,
            "require_governance": self.require_governance,
            "capabilities": self.capabilities,
            "parameters": self.parameters,
        }


@dataclass
class OrchestratorConfig:
    """Configuration for orchestrator."""

    governance: GovernanceConfig = field(default_factory=GovernanceConfig)
    agents: list = field(default_factory=list)
    enable_agent_bus: bool = True
    enable_api: bool = False
    api_host: str = "0.0.0.0"
    api_port: int = 8000
    debug: bool = False

    @classmethod
    def from_file(cls, path: str) -> "OrchestratorConfig":
        """Load orchestrator config from file."""
        config_file = Path(path)
        if not config_file.exists():
            raise FileNotFoundError(f"Config file not found: {path}")

        with open(config_file) as f:
            data = yaml.safe_load(f)

        # Parse governance config
        if "governance" in data:
            data["governance"] = GovernanceConfig.from_dict(data["governance"])

        # Parse agent configs
        if "agents" in data:
            data["agents"] = [AgentConfig.from_dict(a) for a in data["agents"]]

        return cls(**data)

    @classmethod
    def from_dict(cls, data: Dict[str, Any]) -> "OrchestratorConfig":
        """Create orchestrator config from dictionary."""
        if "governance" in data and isinstance(data["governance"], dict):
            data["governance"] = GovernanceConfig.from_dict(data["governance"])

        if "agents" in data and isinstance(data["agents"], list):
            data["agents"] = [
                AgentConfig.from_dict(a) if isinstance(a, dict) else a for a in data["agents"]
            ]

        return cls(**data)

    def to_dict(self) -> Dict[str, Any]:
        """Convert config to dictionary."""
        return {
            "governance": (
                self.governance.to_dict()
                if isinstance(self.governance, GovernanceConfig)
                else self.governance
            ),
            "agents": [a.to_dict() if isinstance(a, AgentConfig) else a for a in self.agents],
            "enable_agent_bus": self.enable_agent_bus,
            "enable_api": self.enable_api,
            "api_host": self.api_host,
            "api_port": self.api_port,
            "debug": self.debug,
        }
