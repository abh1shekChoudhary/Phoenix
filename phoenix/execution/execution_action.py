# phoenix/execution/execution_action.py

from dataclasses import dataclass
from typing import List, Optional


@dataclass
class ExecutionAction:
    action_type: str              # e.g. GENERATE_PATCH, RUN_TESTS
    description: str
    affected_files: List[str]

    command: Optional[str] = None # simulated shell command
    artifact: Optional[str] = None  # generated output (patch, report)

    risk_level: str = "LOW"
    dry_run: bool = True
