class TokenBudget:
    def __init__(self, max_tokens: int):
        self.max_tokens = max_tokens
        self.used_tokens = 0

    def can_spend(self, tokens: int) -> bool:
        return self.used_tokens + tokens <= self.max_tokens

    def spend(self, tokens: int):
        if not self.can_spend(tokens):
            raise RuntimeError("Token budget exceeded")
        self.used_tokens += tokens

    def remaining(self) -> int:
        return self.max_tokens - self.used_tokens
