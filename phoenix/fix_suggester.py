from phoenix.fix_suggestion import FixSuggestion
from phoenix.incident import Incident


class FixSuggester:
    """
    Suggests minimal, human-reviewable fixes for CODE incidents.
    NO automatic changes.
    """

    def suggest(self, incident: Incident) -> FixSuggestion:
        # Phase 11: deterministic stub (no real AI yet)

        return FixSuggestion(
            description=(
                "Handle the RuntimeException explicitly in the controller or "
                "remove the intentional crash logic. Consider returning a proper "
                "HTTP error response instead of throwing a raw exception."
            ),
            affected_files=[
                "RiskyController.java"
            ],
            risk_level="LOW",
            confidence=0.7
        )
