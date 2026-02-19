import re
from typing import Optional

JAVA_STACKTRACE_PATTERN = re.compile(
    r"at\s+([\w\.]+)\.(\w+)\((\w+\.java):(\d+)\)"
)

def extract_java_location(line: str) -> Optional[dict]:
    match = JAVA_STACKTRACE_PATTERN.search(line)
    if not match:
        return None

    return {
        "full_class": match.group(1),
        "method": match.group(2),
        "file": match.group(3),
        "line": int(match.group(4))
    }
