from phoenix.escalation.escalation_level import EscalationLevel


class FixFailureEvaluator:
    def evaluate(
        self,
        incident,
        signal_timestamp: float,
        current_fingerprint: str,
    ) -> bool:

        if not incident.fix_attempted:
            return False

        if not incident.last_fix_attempt_at:
            return False

        if signal_timestamp <= incident.last_fix_attempt_at:
            return False

        if incident.failure_fingerprint != current_fingerprint:
            return False

        # ---- FIX FAILURE CONFIRMED ----
        incident.post_fix_reoccurrence_count += 1

        count = incident.post_fix_reoccurrence_count

        if count == 1:
            incident.escalation_level = EscalationLevel.WARNING

        elif count == 2:
            incident.escalation_level = EscalationLevel.HIGH

        elif count >= 4:
            incident.escalation_level = EscalationLevel.CRITICAL
            incident.auto_resolution_locked = True
            incident.force_manual_approval = True

        return True
