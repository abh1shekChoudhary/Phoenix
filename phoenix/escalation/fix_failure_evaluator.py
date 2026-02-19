from phoenix.escalation.escalation_level import EscalationLevel


WARNING_THRESHOLD = 2
STRATEGY_UPGRADE_THRESHOLD = 3
CRITICAL_THRESHOLD = 5


class FixFailureEvaluator:
    def evaluate(
        self,
        incident,
        signal_timestamp: float,
        current_fingerprint: str,
    ) -> bool:

        # No fix attempted yet
        if not incident.fix_attempted:
            return False

        if not incident.last_fix_attempt_at:
            return False

        # Failure happened before fix
        if signal_timestamp <= incident.last_fix_attempt_at:
            return False

        # Different failure
        if incident.failure_fingerprint != current_fingerprint:
            return False

        # ---- FIX FAILURE CONFIRMED ----
        incident.post_fix_reoccurrence_count += 1

        count = incident.post_fix_reoccurrence_count

        if count >= CRITICAL_THRESHOLD:
            incident.escalation_level = EscalationLevel.CRITICAL
            incident.auto_resolution_locked = True
            incident.strategy_locked = True

        elif count >= STRATEGY_UPGRADE_THRESHOLD:
            incident.escalation_level = EscalationLevel.HIGH

        elif count >= WARNING_THRESHOLD:
            incident.escalation_level = EscalationLevel.WARNING

        else:
            incident.escalation_level = EscalationLevel.INFO

        return True
