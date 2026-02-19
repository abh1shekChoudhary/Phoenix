from typing import List

def extract_method(lines: List[str], target_line: int, context: int = 10) -> List[str]:
    start = max(0, target_line - context - 1)
    end = min(len(lines), target_line + context)
    return lines[start:end]
