import math
from phoenix.learning.strategy_performance_repository import (
    StrategyPerformanceRepository,
)


class StrategyOptimizer:
    """
    Multi-Armed Bandit (UCB1) based strategy selector.
    """

    def __init__(self, repository: StrategyPerformanceRepository):
        self.repository = repository

    # ---------------------------------------------------------

    def get_best_strategy(self, fingerprint: str, max_version: int = 3) -> int:
        """
        Returns best strategy using UCB1 scoring.
        """

        stats = self.repository.get_stats_for_fingerprint(fingerprint)

        # If no history, default to V1
        if not stats:
            return 1

        total_attempts = 0

        for v in range(1, max_version + 1):
            key = f"{fingerprint}|V{v}"
            data = stats.get(key, {"success": 0, "fail": 0})
            total_attempts += data["success"] + data["fail"]

        if total_attempts == 0:
            return 1

        best_score = -1
        best_version = 1

        for v in range(1, max_version + 1):
            key = f"{fingerprint}|V{v}"
            data = stats.get(key, {"success": 0, "fail": 0})

            attempts = data["success"] + data["fail"]

            # Encourage exploration for unused strategies
            if attempts == 0:
                return v

            win_rate = data["success"] / attempts

            exploration_bonus = math.sqrt(
                2 * math.log(total_attempts) / attempts
            )

            score = win_rate + exploration_bonus

            if score > best_score:
                best_score = score
                best_version = v

        return best_version
