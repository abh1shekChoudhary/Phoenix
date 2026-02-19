from enum import Enum, auto


class IncidentState(Enum):
    # Initial detection
    DETECTED = auto()

    # Gathering information
    ENRICHING = auto()
    STABLE = auto()
    # Enough info to act
    READY = auto()

    # Reasoning & planning
    ANALYZED = auto()
    PLANNED = auto()

    # Human-in-the-loop
    AWAITING_APPROVAL = auto()

    # Resolution lifecycle
    RESOLVED = auto()
    EXECUTED = auto()
    MONITORING = auto()

    # Terminal states
    CLOSED = auto()


