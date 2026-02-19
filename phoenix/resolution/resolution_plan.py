from dataclasses import dataclass, field
from typing import List, Optional


@dataclass
class ResolutionAction:
    description: str
    affected_files: List[str]
    risk_level: str  # LOW | MEDIUM | HIGH
    requires_human_approval: bool = True


@dataclass
class ResolutionPlan:
    problem_summary: str
    likely_root_cause: str

    actions: List[ResolutionAction] = field(default_factory=list)

    confidence: float = 0.0
    safe_to_auto_apply: bool = False
    notes: Optional[str] = None
