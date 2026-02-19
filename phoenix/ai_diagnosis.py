from dataclasses import dataclass
from typing import Optional


@dataclass
class AIDiagnosis:
    summary: str                  # Human-readable explanation
    likely_root_cause: str         # Short label
    requires_code_change: bool
    confidence: float              # 0.0 – 1.0
    risk_notes: Optional[str] = None
