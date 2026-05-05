#!/usr/bin/env python3
"""Utility to refactor agents to use dependency injection instead of orchestrator coupling."""

import re
import sys
from pathlib import Path

AGENTS_DIR = Path(__file__).parent / "src" / "socratic_agents"

SOCRATIC_SYSTEM_IMPORTS = {
    "from socratic_system.database": "# Removed: database service injected",
    "from socratic_system.models": "# Removed: models passed as data",
    "from socratic_system.utils": "# Removed: utilities injected as services",
    "from socratic_system.subscription": "# Removed: auth service injected",
    "from socratic_system.parsers": "# Removed: parsers injected",
    "from socratic_system.services": "# Removed: services injected",
    "from socratic_system.core": "# Removed: core logic injected",
}

ORCHESTRATOR_PATTERNS = {
    r"self\.orchestrator\.database\.": "await self.database_service.",
    r"self\.orchestrator\.claude_client\.": "await self.llm_service.",
    r"self\.orchestrator\.vector_db\.": "await self.vector_db_service.",
    r"self\.orchestrator\.process_request\(": "await self.agent_bus.send_request(",
    r"self\.orchestrator\.config\.": "# config.",
}

def refactor_imports(content: str) -> str:
    """Remove socratic_system imports and add service imports."""
    lines = content.split("\n")
    new_lines = []
    has_interfaces_import = False

    for line in lines:
        skip = False
        for pattern, replacement in SOCRATIC_SYSTEM_IMPORTS.items():
            if pattern in line and "from socratic_system" in line:
                new_lines.append(f"# {replacement}: {line.strip()}")
                skip = True
                break

        if not skip:
            new_lines.append(line)

    # Add service interfaces import if not present
    result = "\n".join(new_lines)
    if "from .interfaces import" not in result and "from socratic_agents.interfaces import" not in result:
        # Find the right place to add it (after other local imports)
        lines = result.split("\n")
        for i, line in enumerate(lines):
            if line.startswith("from ."):
                # Insert before first local import
                lines.insert(i, "from .interfaces import DatabaseService, LLMService, VectorDatabaseService, FileSystemService, AuthService, EventEmitterService")
                break
        result = "\n".join(lines)

    return result

def refactor_init_method(content: str, agent_name: str) -> str:
    """Update __init__ to accept injected services."""
    # Pattern for old __init__
    old_pattern = r'def __init__\(self, orchestrator[^)]*\):\s+super\(\)\.__init__\("' + agent_name + r'", orchestrator\)'

    new_init = f'''def __init__(
        self,
        name: str = "{agent_name}",
        database_service: Optional[DatabaseService] = None,
        llm_service: Optional[LLMService] = None,
        vector_db_service: Optional[VectorDatabaseService] = None,
        file_service: Optional[FileSystemService] = None,
        auth_service: Optional[AuthService] = None,
        agent_bus: Optional[Any] = None,
    ):
        super().__init__(name, agent_bus)
        self.database_service = database_service
        self.llm_service = llm_service
        self.vector_db_service = vector_db_service
        self.file_service = file_service
        self.auth_service = auth_service'''

    # More flexible pattern matching
    content = re.sub(
        r'def __init__\(self, orchestrator[^)]*\):\s+super\(\)\.__init__\("[^"]*", orchestrator\)[^\n]*',
        new_init,
        content,
        flags=re.DOTALL
    )

    return content

def refactor_process_method(content: str) -> str:
    """Make process method async if it calls services."""
    # Check if method calls any services
    if re.search(r'(self\.orchestrator\.|await self\.(llm|database|vector_db|file|auth))', content):
        # Make process async
        content = re.sub(
            r'def process\(self, request[^)]*\) -> Dict:',
            'async def process(self, request: Dict[str, Any]) -> Dict[str, Any]:',
            content
        )

    return content

def refactor_orchestrator_calls(content: str) -> str:
    """Replace orchestrator calls with service calls."""
    for pattern, replacement in ORCHESTRATOR_PATTERNS.items():
        content = re.sub(pattern, replacement, content)

    return content

def add_type_hints(content: str) -> str:
    """Add necessary type hints."""
    if "from typing import" not in content:
        if "from __future__" in content:
            # Add after future import
            content = re.sub(
                r'from __future__ import [^\n]*\n',
                lambda m: m.group(0) + 'from typing import Optional, Any, Dict\n',
                content,
                count=1
            )
        else:
            # Add after docstring
            content = re.sub(
                r'("""\n[^"]*\n""")\n',
                r'\1\n\nfrom typing import Optional, Any, Dict\n',
                content,
                count=1
            )
    else:
        # Ensure we have the right imports
        if "Optional" not in content:
            content = re.sub(
                r'from typing import ([^\n]*)',
                lambda m: f'from typing import Optional, Any, Dict, {m.group(1)}' if 'Optional' not in m.group(1) else m.group(0),
                content,
                count=1
            )

    return content

def refactor_agent_file(agent_file: Path) -> str:
    """Refactor a single agent file."""
    content = agent_file.read_text()
    agent_name = agent_file.stem

    # Apply refactorings in order
    content = refactor_imports(content)
    content = refactor_init_method(content, agent_name)
    content = refactor_process_method(content)
    content = refactor_orchestrator_calls(content)
    content = add_type_hints(content)

    return content

def main():
    """Refactor all agent files."""
    agent_files = sorted(AGENTS_DIR.glob("*.py"))

    # Filter to only agent files
    agent_files = [f for f in agent_files if f.stem not in [
        "__init__", "base", "models", "config", "governance", "events",
        "orchestrator", "agent_bus", "client", "api_app", "api_routes"
    ]]

    print(f"Found {len(agent_files)} agents to refactor:")
    for agent_file in agent_files:
        print(f"  - {agent_file.name}")

    print("\nRefactoring agents...")
    for agent_file in agent_files:
        try:
            refactored = refactor_agent_file(agent_file)
            agent_file.write_text(refactored)
            print(f"  ✓ {agent_file.name}")
        except Exception as e:
            print(f"  ✗ {agent_file.name}: {e}")

    print("\nRefactoring complete!")

if __name__ == "__main__":
    main()
