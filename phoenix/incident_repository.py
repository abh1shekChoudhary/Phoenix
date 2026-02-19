import json
from pathlib import Path
from datetime import datetime

from phoenix.incident import Incident


class IncidentRepository:
    def __init__(self, path: Path):
        self.path = path
        self.path.parent.mkdir(parents=True, exist_ok=True)

        if not self.path.exists():
            self.path.write_text(json.dumps({}, indent=2))

    def _load_store(self):
        try:
            return json.loads(self.path.read_text())
        except Exception:
            return {}

    def _write_store(self, store: dict):
        self.path.write_text(json.dumps(store, indent=2))

    def persist(self, incident: Incident):
        store = self._load_store()

        record = {
            "id": incident.id,
            "state": incident.state.value if incident.state else None,
            "category": incident.category,
            "subcategory": incident.subcategory,
            "confidence": incident.confidence,
            "decision": incident.decision,
            "summary": incident.summary,
            "context_summary": incident.context_summary,
            "reoccurrence_count": incident.reoccurrence_count,
            "failure_fingerprint": incident.failure_fingerprint,
            "escalation_level": (
                incident.escalation_level.value
                if incident.escalation_level
                else None
            ),
            "fix_attempted": incident.fix_attempted,
            "fix_fingerprint": incident.fix_fingerprint,
            "last_fix_attempt_at": incident.last_fix_attempt_at,
            "cooldown_until": (
                incident.cooldown_until.isoformat()
                if getattr(incident, "cooldown_until", None)
                else None
            ),
            "updated_at": datetime.utcnow().isoformat(),
        }

        # Resolution plan (safe serialization)
        if incident.resolution_plan:
            record["resolution_plan"] = {
                "problem_summary": incident.resolution_plan.problem_summary,
                "likely_root_cause": incident.resolution_plan.likely_root_cause,
                "confidence": incident.resolution_plan.confidence,
                "safe_to_auto_apply": incident.resolution_plan.safe_to_auto_apply,
                "notes": incident.resolution_plan.notes,
                "actions": [
                    {
                        "description": a.description,
                        "affected_files": a.affected_files,
                        "risk_level": a.risk_level,
                        "requires_human_approval": a.requires_human_approval,
                    }
                    for a in incident.resolution_plan.actions
                ],
            }

        store[incident.id] = record
        self._write_store(store)
