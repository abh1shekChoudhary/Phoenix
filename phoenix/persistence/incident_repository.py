from pathlib import Path
from datetime import datetime

from phoenix.incident import Incident
from phoenix.persistence.incident_store import IncidentStore
from phoenix.persistence.incident_state import IncidentState
from phoenix.resolution.resolution_plan import ResolutionPlan, ResolutionAction


class IncidentRepository:
    def __init__(self, storage_path: Path):
        self.store = IncidentStore(storage_path)

    def persist(self, incident: Incident):
        record = {
            "id": incident.id,
            "state": incident.state.name,
            "category": incident.category,
            "subcategory": incident.subcategory,
            "confidence": incident.confidence,
            "decision": incident.decision,
            "summary": incident.summary,
            "context_summary": incident.context_summary,
            "resolution_plan": self._serialize_resolution_plan(
                incident.resolution_plan
            ),
            "updated_at": datetime.utcnow().isoformat(),
        }

        self.store.save_incident(incident.id, record)

    def _serialize_resolution_plan(
        self, plan: ResolutionPlan | None
    ) -> dict | None:
        if not plan:
            return None

        return {
            "problem_summary": plan.problem_summary,
            "likely_root_cause": plan.likely_root_cause,
            "confidence": plan.confidence,
            "safe_to_auto_apply": plan.safe_to_auto_apply,
            "notes": plan.notes,
            "actions": [
                self._serialize_action(action)
                for action in plan.actions
            ],
        }

    def _serialize_action(self, action: ResolutionAction) -> dict:
        return {
            "description": action.description,
            "affected_files": action.affected_files,
            "risk_level": action.risk_level,
            "requires_human_approval": action.requires_human_approval,
        }
