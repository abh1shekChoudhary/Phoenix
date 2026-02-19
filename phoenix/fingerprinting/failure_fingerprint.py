import hashlib
import re


def build_failure_fingerprint(signal):
    """
    Build a stable fingerprint based on:
    - Exception class
    - First application stack frame
    """

    raw = signal.raw_line

    # Extract exception type
    exception_match = re.search(r"([\w\.]+Exception)", raw)
    exception = exception_match.group(1) if exception_match else "UnknownException"

    # Extract first app stack frame if present
    stack_match = re.search(r"at ([\w\.]+)\(", raw)
    frame = stack_match.group(1) if stack_match else ""

    base = f"{exception}:{frame}"

    return hashlib.sha256(base.encode()).hexdigest()
