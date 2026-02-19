from phoenix.incident import Incident
from phoenix.signals import FailureSignal
from phoenix.fingerprinting.failure_fingerprint import build_failure_fingerprint


class IncidentManager:
    def __init__(self):
        self.active_incidents: list[Incident] = []

    def ingest(self, signal: FailureSignal):
        """
        Returns: (incident, is_new)
        """

        fingerprint = build_failure_fingerprint(signal)

        # Try to merge into existing incident
        for incident in self.active_incidents:
            if incident.failure_fingerprint == fingerprint:
                incident.add_signal(signal)
                incident.reoccurrence_count += 1
                incident.failure_fingerprint = fingerprint
                return incident, False

        # Create new incident
        new_incident = Incident()
        new_incident.add_signal(signal)
        new_incident.failure_fingerprint = fingerprint
        new_incident.reoccurrence_count = 1

        self.active_incidents.append(new_incident)

        return new_incident, True
