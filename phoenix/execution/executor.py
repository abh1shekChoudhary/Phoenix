# phoenix/execution/executor.py

from phoenix.execution.execution_plan import ExecutionPlan


class Executor:
    def execute(self, plan: ExecutionPlan):
        print("\n[PHOENIX] ▶ Execution Started (DRY-RUN MODE)")

        for action in plan.actions:
            print(f"[PHOENIX] Action: {action.action_type}")
            print(f"  Description: {action.description}")
            print(f"  Files: {', '.join(action.affected_files)}")
            print(f"  Risk: {action.risk_level}")

            if action.command:
                print(f"  Command (simulated): {action.command}")

            if action.artifact:
                print(f"  Artifact to be generated: {action.artifact}")

            print("  Result: SIMULATED SUCCESS\n")

        print("[PHOENIX] ▶ Execution Complete (No system changes made)")
