from dataclasses import dataclass, field
from uuid import uuid4
from typing import List, Optional
from datetime import datetime
from time import time

from phoenix.signals import FailureSignal
from phoenix.token_budget import TokenBudget
from phoenix.persistence.incident_state import IncidentState
from phoenix.resolution.resolution_plan import ResolutionPlan


@dataclass
class Incident:
    # ---------- Identity ----------
    id: str = field(default_factory=lambda: str(uuid4()))

    # ---------- Evidence ----------
    signals: List[FailureSignal] = field(default_factory=list)

    # ---------- Classification ----------
    category: str = "UNKNOWN"
    subcategory: str = "UNKNOWN"
    confidence: float = 0.0

    # ---------- Decision ----------
    decision: Optional[str] = None

    # ---------- Narrative ----------
    summary: str = ""
    context_summary: Optional[str] = None

    # ---------- Context ----------
    context_expanded: bool = False
    token_budget: TokenBudget = field(default_factory=lambda: TokenBudget(4000))
    has_stacktrace: bool = False
    has_context: bool = False
    confidence_ready: bool = False

    # ---------- Fingerprinting ----------
    failure_fingerprint: Optional[str] = None
    fix_fingerprint: Optional[str] = None

    # ---------- Recurrence ----------
    reoccurrence_count: int = 0
    post_fix_reoccurrence_count: int = 0

    # ---------- Fix Tracking ----------
    fix_attempted: bool = False
    last_fix_attempt_at: Optional[float] = None

    # ---------- Strategy System ----------
    strategy_version: int = 1
    max_strategy_version: int = 3
    strategy_locked: bool = False

    alternate_strategy_attempted: bool = False
    sandbox_validation_attempted: bool = False

    # ---------- Lifecycle ----------
    state: IncidentState = IncidentState.DETECTED
    created_at: datetime = field(default_factory=datetime.utcnow)
    last_updated: datetime = field(default_factory=datetime.utcnow)

    executed_at: Optional[datetime] = None
    cooldown_until: Optional[datetime] = None

    # ---------- Enrichment ----------
    enrichment_started_at: float = field(default_factory=time)
    last_enriched_at: float = field(default_factory=time)

    # ---------- Resolution ----------
    resolution_plan: Optional[ResolutionPlan] = None

    # ---------- Behavior ----------
    def add_signal(self, signal: FailureSignal):
        self.signals.append(signal)
        self.last_updated = datetime.utcnow()
        self.reoccurrence_count += 1
