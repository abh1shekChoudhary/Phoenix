from datetime import datetime, timedelta
from phoenix.incident import Incident


class IncidentMerger:
    MERGE_WINDOW_SECONDS = 300  # 5 minutes

    def should_merge(self, existing: Incident, incoming: Incident) -> bool:
        """
        Decide if two incidents represent the same real-world failure
        """

        if existing.fingerprint != incoming.fingerprint:
            return False

        # Do not merge closed incidents
        if existing.state.name in {"CLOSED", "EXECUTED"}:
            return False

        # Time-based guard
        age = datetime.utcnow() - existing.last_updated
        if age > timedelta(seconds=self.MERGE_WINDOW_SECONDS):
            return False

        return True

    def merge(self, target: Incident, source: Incident) -> Incident:
        """
        Merge source incident into target incident
        """

        for signal in source.signals:
            target.add_signal(signal)

        # Progressive confidence
        target.confidence = min(1.0, max(target.confidence, source.confidence))

        # Progressive enrichment flags
        target.has_stacktrace |= source.has_stacktrace
        target.has_context |= source.has_context
        target.confidence_ready |= source.confidence_ready

        target.last_updated = datetime.utcnow()

        return target
