from dataclasses import dataclass
from typing import List


@dataclass
class FixSuggestion:
    description: str
    affected_files: List[str]
    risk_level: str        # LOW | MEDIUM | HIGH
    confidence: float
