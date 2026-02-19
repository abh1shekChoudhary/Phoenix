class DecisionPolicy:
    def decide(self, incident):
        if incident.category == "CODE" and incident.confidence >= 0.6:
            return "REQUIRE_HUMAN_REVIEW"

        if incident.category == "INFRA":
            return "SUGGEST_CONFIG_CHECK"

        return "OBSERVE_ONLY"
