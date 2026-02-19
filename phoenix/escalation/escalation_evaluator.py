from phoenix.escalation.escalation_level import EscalationLevel


class EscalationEvaluator:
    """
    Determines escalation level based on:
    - Reoccurrence count
    - Whether fix was attempted
    - Whether failure persisted after fix
    """

    def evaluate(self, incident):
        count = incident.reoccurrence_count or 1

        # First occurrence
        if count == 1:
            return EscalationLevel.INFO

        # Recurring before fix attempt
        if count <= 3 and not incident.fix_attempted:
            return EscalationLevel.WARNING

        # Recurring after fix attempt
        if incident.fix_attempted and count >= 3:
            return EscalationLevel.CRITICAL

        # Severe systemic failure
        if incident.fix_attempted and count >= 6:
            return EscalationLevel.SEVERE

        return EscalationLevel.WARNING
