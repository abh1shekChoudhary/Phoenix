class StrategyManager:

    def evaluate(self, incident):
        """
        Returns:
            "UPGRADE"  → strategy upgraded
            "LOCK"     → lock system
            None       → no change
        """

        count = incident.post_fix_reoccurrence_count

        # Upgrade to V2
        if count >= 3 and incident.strategy_version == 1:
            incident.strategy_version = 2
            return "UPGRADE"

        # Upgrade to V3
        if count >= 5 and incident.strategy_version == 2:
            incident.strategy_version = 3
            return "UPGRADE"

        # Hard lock
        if count >= 7 and incident.strategy_version == 3:
            incident.strategy_locked = True
            return "LOCK"

        return None
