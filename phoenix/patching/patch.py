from dataclasses import dataclass
from typing import List


@dataclass
class Patch:
    file_path: str
    diff: str                 # unified diff text
    confidence: float
    rationale: str
