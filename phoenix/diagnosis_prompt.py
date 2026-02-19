from phoenix.incident import Incident


def build_diagnosis_prompt(incident: Incident) -> str:
    return f"""
You are a senior backend engineer diagnosing a production incident.

Incident classification:
- Category: {incident.category}
- Subcategory: {incident.subcategory}
- Confidence: {incident.confidence}

Incident summary:
{incident.summary}

Relevant code context:
{incident.context_summary or "No code context available"}

Instructions:
1. Identify the most likely root cause.
2. State whether a code change is required.
3. Be concise and factual. No speculation.

Respond in this format:

ROOT_CAUSE:
<one sentence>

EXPLANATION:
<short paragraph>

REQUIRES_CODE_CHANGE:
true|false

CONFIDENCE:
<number between 0 and 1>
""".strip()
