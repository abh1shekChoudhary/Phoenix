from dataclasses import dataclass
from typing import List

@dataclass
class ContextFile:
    path: str
    reason: str
    score: float
    summary: str | None = None
    content: str | None = None

@dataclass
class FailureContext:
    files: List[ContextFile]
    token_budget: int
