from typing import Optional
from datetime import datetime
from phoenix.signals import FailureSignal
from phoenix.log_buffer import LogBuffer

class FailureDetector:
    def __init__(self):
        pass

    def detect(self, line: str, buffer: LogBuffer) -> Optional[FailureSignal]:
        """
        Inspect a log line and decide if it represents a failure signal.
        """
        # Startup failure (Spring Boot / common JVM apps)
        if "APPLICATION FAILED TO START" in line:
            return FailureSignal(
                timestamp=datetime.utcnow(),
                signal_type="STARTUP_FAILURE",
                raw_line=line,
                context=buffer.snapshot(),
                confidence=0.9
            )

        # Generic uncaught exception
        if "Exception" in line or "ERROR" in line:
            return FailureSignal(
                timestamp=datetime.utcnow(),
                signal_type="RUNTIME_ERROR",
                raw_line=line,
                context=buffer.snapshot(),
                confidence=0.6
            )

        return None
