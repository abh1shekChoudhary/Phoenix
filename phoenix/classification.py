from dataclasses import dataclass
from typing import Literal

FailureCategory = Literal[
    "TRANSIENT",
    "INFRA",
    "CONFIG",
    "CODE",
    "LOGIC",
    "UNKNOWN"
]

@dataclass
class FailureClassification:
    category: FailureCategory
    confidence: float
    explanation: str
    requires_code_change: bool
