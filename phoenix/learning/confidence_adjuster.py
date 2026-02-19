class ConfidenceAdjuster:
    """
    Dynamically adjusts resolution confidence
    based on historical strategy performance.
    """

    MIN_SAMPLE_SIZE = 3

    def __init__(self, repository):
        self.repository = repository

    # --------------------------------------------------

    def adjust(
        self,
        base_confidence: float,
        fingerprint: str,
        strategy_version: int,
    ) -> float:

        success, fail = self.repository.get_stats(
            fingerprint,
            strategy_version,
            scope="fingerprints",
        )

        total = success + fail

        if total < self.MIN_SAMPLE_SIZE:
            return base_confidence

        success_rate = success / total

        # Weighted adjustment
        adjusted = base_confidence * (0.5 + success_rate)

        return min(max(adjusted, 0.0), 1.0)
