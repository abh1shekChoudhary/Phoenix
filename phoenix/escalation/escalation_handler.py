from phoenix.escalation.escalation_level import EscalationLevel
from phoenix.persistence.incident_state import IncidentState


class EscalationHandler:

    def handle(self, incident):

        level = incident.escalation_level

        if level == EscalationLevel.WARNING:
            print(
                f"[PHOENIX] 🟡 Escalation Level: WARNING "
                f"(monitoring closely)"
            )

        elif level == EscalationLevel.CRITICAL:
            print(
                f"[PHOENIX] 🔴 Escalation Level: CRITICAL "
                f"(manual approval required)"
            )
            incident.force_manual_approval = True

        elif level == EscalationLevel.SEVERE:
            print(
                f"[PHOENIX] 🛑 Escalation Level: SEVERE "
                f"(auto-resolution disabled)"
            )
            incident.force_manual_approval = True
            incident.auto_resolution_locked = True
            incident.state = IncidentState.ESCALATED

        return incident
