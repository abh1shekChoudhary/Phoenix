import json
from phoenix.signals import FailureSignal
from phoenix.classification import FailureClassification
from phoenix.prompts import CLASSIFICATION_PROMPT

# Placeholder for AI client (to be wired later)
def call_ai(prompt: str) -> str:
    """
    TEMPORARY stub.
    Replace with OpenAI / LLM call in next step.
    """
    return json.dumps({
        "category": "UNKNOWN",
        "confidence": 0.0,
        "explanation": "AI not yet connected",
        "requires_code_change": False
    })

class FailureClassifier:
    def classify(self, signal: FailureSignal) -> FailureClassification:
        prompt = CLASSIFICATION_PROMPT + f"\n\nFailure Signal:\n{signal}"

        raw = call_ai(prompt)
        data = json.loads(raw)

        return FailureClassification(
            category=data["category"],
            confidence=float(data["confidence"]),
            explanation=data["explanation"],
            requires_code_change=bool(data["requires_code_change"])
        )
