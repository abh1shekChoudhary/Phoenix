# phoenix/execution/execution_plan_builder.py

from phoenix.execution.execution_plan import ExecutionPlan
from phoenix.execution.execution_action import ExecutionAction
from phoenix.resolution.resolution_plan import ResolutionPlan


class ExecutionPlanBuilder:
    def build(
        self,
        *,
        incident_id: str,
        resolution: ResolutionPlan,
    ) -> ExecutionPlan:
        actions = []

        for action in resolution.actions:
            exec_action = ExecutionAction(
                action_type="GENERATE_PATCH",
                description=action.description,
                affected_files=action.affected_files,
                artifact=(
                    f"{action.affected_files[0]}-fix.patch"
                    if action.affected_files
                    else None
                ),
                risk_level=action.risk_level,
                dry_run=True,
            )
            actions.append(exec_action)

        return ExecutionPlan(
            incident_id=incident_id,
            safe_to_execute=resolution.safe_to_auto_apply,
            actions=actions,
            summary=resolution.problem_summary,
            confidence=resolution.confidence,
        )
