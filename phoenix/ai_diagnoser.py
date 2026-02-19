from phoenix.ai_diagnosis import AIDiagnosis
from phoenix.incident import Incident
from phoenix.diagnosis_prompt import build_diagnosis_prompt


class AIDiagnoser:
    def diagnose(self, incident: Incident) -> AIDiagnosis:
        prompt = build_diagnosis_prompt(incident)

        # 🔒 Phase 10: NO real AI call yet
        # This is a deterministic placeholder

        return AIDiagnosis(
            summary="Runtime exception thrown during request handling.",
            likely_root_cause="Unhandled runtime exception in controller",
            requires_code_change=True,
            confidence=0.65,
            risk_notes="Repeated failures may affect request stability."
        )
