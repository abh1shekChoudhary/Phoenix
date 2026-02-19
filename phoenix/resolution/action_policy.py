from phoenix.resolution.problem_type import ProblemDomain, ProblemType


class ActionPolicy:
    """
    Decides what Phoenix is ALLOWED to do.
    Policy ALWAYS beats AI.
    """

    @staticmethod
    def allow_auto_fix(domain: ProblemDomain, problem: ProblemType) -> bool:
        # Absolutely forbidden domains
        if domain in {
            ProblemDomain.SECURITY,
            ProblemDomain.DATA,
            ProblemDomain.INFRA,
        }:
            return False

        # Even in CODE, only trivial cases allowed later
        return False  # 🔒 Phase 12 rule: no auto-fix yet

    @staticmethod
    def allow_suggestion(domain: ProblemDomain) -> bool:
        return True

    @staticmethod
    def max_risk_allowed(domain: ProblemDomain) -> str:
        if domain == ProblemDomain.CODE:
            return "MEDIUM"
        return "LOW"
