from phoenix.incident import Incident
from phoenix.resolution.problem_type import ProblemDomain, ProblemType
from phoenix.resolution.resolution_plan import ResolutionPlan, ResolutionAction
from phoenix.resolution.action_policy import ActionPolicy


class ResolutionBuilder:
    """
    Strategy-aware resolution builder.
    """

    def build(self, incident: Incident) -> ResolutionPlan:
        domain = self._infer_domain(incident)
        problem = self._infer_problem_type(incident)

        actions = []

        if domain == ProblemDomain.CODE and problem == ProblemType.UNHANDLED_RUNTIME:

            if incident.strategy_version == 1:
                description = (
                    "Wrap RuntimeException in controller using try/catch "
                    "and return proper HTTP 500 response."
                )

            elif incident.strategy_version == 2:
                description = (
                    "Introduce @ControllerAdvice global exception handler "
                    "to centralize RuntimeException handling."
                )

            elif incident.strategy_version == 3:
                description = (
                    "Implement structured error handling with custom "
                    "error response model and centralized exception strategy."
                )

            else:
                description = "Manual intervention required."

            actions.append(
                ResolutionAction(
                    description=description,
                    affected_files=self._guess_files(incident),
                    risk_level="LOW",
                    requires_human_approval=True,
                )
            )

        return ResolutionPlan(
            problem_summary=f"{domain.name} / {problem.name}",
            likely_root_cause=incident.summary or "Unhandled exception detected",
            actions=actions,
            confidence=incident.confidence,
            safe_to_auto_apply=ActionPolicy.allow_auto_fix(domain, problem),
            notes=f"Generated under Strategy V{incident.strategy_version}",
        )

    # -----------------------------------------------------

    def _infer_domain(self, incident: Incident) -> ProblemDomain:
        if incident.category == "CODE":
            return ProblemDomain.CODE
        if incident.category == "INFRA":
            return ProblemDomain.INFRA
        return ProblemDomain.UNKNOWN

    def _infer_problem_type(self, incident: Incident) -> ProblemType:
        try:
            return ProblemType[incident.subcategory]
        except KeyError:
            return ProblemType.UNCLASSIFIED

    def _guess_files(self, incident: Incident):
        if incident.context_summary:
            return ["(see context summary)"]
        return []
