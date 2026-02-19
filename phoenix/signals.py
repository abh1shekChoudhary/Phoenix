from dataclasses import dataclass
from datetime import datetime
from typing import List, Optional

@dataclass
class FailureSignal:
    timestamp: datetime
    signal_type: str
    raw_line: str
    context: List[str]
    confidence: float
    source: str = "log"
