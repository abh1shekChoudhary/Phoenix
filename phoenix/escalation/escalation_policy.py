from datetime import datetime
from phoenix.incident import Incident


class EscalationPolicy:
    """
    Determines if an incident should escalate
    based on recurrence and fix history.
    """

    REPEAT_THRESHOLD = 3
    SYSTEMIC_THRESHOLD = 5

    def evaluate(self, incident: Incident) -> Incident:
        if incident.reoccurrence_count >= self.SYSTEMIC_THRESHOLD:
            incident.escalation_level = "SYSTEMIC"
            incident.decision = "REQUIRE_HUMAN_REVIEW"
            return incident

        if (
            incident.reoccurrence_count >= self.REPEAT_THRESHOLD
            and incident.fix_attempted
        ):
            incident.escalation_level = "REPEATED_FAILURE"
            incident.decision = "REQUIRE_HUMAN_REVIEW"

        return incident
