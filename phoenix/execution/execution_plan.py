# phoenix/execution/execution_plan.py

from dataclasses import dataclass, field
from typing import List
from phoenix.execution.execution_action import ExecutionAction


@dataclass
class ExecutionPlan:
    incident_id: str
    safe_to_execute: bool
    actions: List[ExecutionAction] = field(default_factory=list)

    summary: str = ""
    confidence: float = 0.0
