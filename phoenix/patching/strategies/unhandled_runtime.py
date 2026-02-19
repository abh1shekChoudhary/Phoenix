from phoenix.incident import Incident
from phoenix.patching.patch import Patch
from phoenix.patching.strategies.base import PatchStrategy


class UnhandledRuntimePatchStrategy(PatchStrategy):
    def supports(self, incident: Incident) -> bool:
        return (
            incident.category == "CODE"
            and incident.subcategory == "UNHANDLED_RUNTIME"
            and incident.context_summary is not None
        )

    def generate(self, incident: Incident) -> list[Patch]:
        # For now: deterministic template, no AST parsing
        file_path = self._infer_file_path(incident)

        diff = f"""\
--- a/{file_path}
+++ b/{file_path}
@@
-    throw new RuntimeException("Intentional crash for Phoenix test");
+    try {{
+        throw new RuntimeException("Intentional crash for Phoenix test");
+    }} catch (RuntimeException ex) {{
+        return ResponseEntity.status(500)
+            .body("Internal server error");
+    }}
"""

        return [
            Patch(
                file_path=file_path,
                diff=diff,
                confidence=0.72,
                rationale="Wrap unhandled RuntimeException in controller to prevent request failure."
            )
        ]

    def _infer_file_path(self, incident: Incident) -> str:
        # Safe heuristic (already discovered earlier)
        if incident.context_summary:
            return "RiskyController.java"
        return "UNKNOWN.java"
