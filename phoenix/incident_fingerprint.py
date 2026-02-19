from phoenix.signals import FailureSignal
from typing import Optional
import re


class IncidentFingerprint:
    @staticmethod
    def from_signal(
        category: str,
        subcategory: str,
        signal: FailureSignal
    ) -> str:
        """
        Build a stable fingerprint from classification + stacktrace location
        """

        location = IncidentFingerprint._extract_location(signal.raw_line)

        if location:
            return f"{category}|{subcategory}|{location}"

        return f"{category}|{subcategory}|UNKNOWN_LOCATION"

    @staticmethod
    def _extract_location(line: str) -> Optional[str]:
        """
        Extract Java file + line number if present
        Example:
          at com.example.healer.RiskyController.crash(RiskyController.java:28)
        """

        match = re.search(r"\((\w+\.java):(\d+)\)", line)
        if match:
            file, line_no = match.groups()
            return f"{file}:{line_no}"

        return None
