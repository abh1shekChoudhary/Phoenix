from phoenix.incident import Incident


def build_fix_prompt(incident: Incident) -> str:
    return f"""
You are a senior backend engineer suggesting a fix.

Incident:
{incident.summary}

Relevant code context:
{incident.context_summary or "No code context available"}

Instructions:
1. Suggest the minimal code change to prevent this failure.
2. Mention which file(s) are affected.
3. Estimate risk level.
4. Do NOT propose large refactors.

Respond in this format:

FIX:
<description>

FILES:
<comma separated list>

RISK:
LOW|MEDIUM|HIGH

CONFIDENCE:
<number between 0 and 1>
""".strip()
