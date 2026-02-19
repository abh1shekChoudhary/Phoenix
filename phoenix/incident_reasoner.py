from phoenix.incident import Incident


class IncidentReasoner:
    def reason(self, incident: Incident) -> Incident:
        messages = [s.raw_line for s in incident.signals]

        if any("OutOfMemoryError" in m for m in messages):
            incident.category = "INFRA"
            incident.subcategory = "MEMORY_EXHAUSTION"
            incident.confidence = 0.9
            incident.summary = (
                "The application ran out of memory, causing JVM-level failure."
            )
            return incident

        if any("NullPointerException" in m for m in messages):
            incident.category = "CODE"
            incident.subcategory = "NULL_SAFETY"
            incident.confidence = 0.8
            incident.summary = (
                "A null reference was accessed due to missing null checks in code."
            )
            return incident

        if any("RuntimeException" in m for m in messages):
            incident.category = "CODE"
            incident.subcategory = "UNHANDLED_RUNTIME"
            incident.confidence = 0.7
            incident.summary = (
                "An unhandled runtime exception occurred during request processing."
            )
            return incident

        incident.category = "UNKNOWN"
        incident.subcategory = "UNCLASSIFIED"
        incident.confidence = 0.3
        incident.summary = (
            "Phoenix detected abnormal behavior but could not confidently classify it."
        )
        return incident
