from pathlib import Path
from phoenix.context import ContextFile, FailureContext
from phoenix.signals import FailureSignal
from phoenix.java_stacktrace import extract_java_location
from phoenix.java_indexer import JavaProjectIndex

class JavaContextResolver:
    def __init__(self, project_root: Path, token_budget: int = 4000):
        self.project_root = project_root
        self.index = JavaProjectIndex(project_root)
        self.index.build()
        self.token_budget = token_budget

    def resolve_from_stacktrace(self, stacktrace: list[str]) -> FailureContext:
        files: dict[str, ContextFile] = {}

        for line in stacktrace:
            location = extract_java_location(line)
            if not location:
                continue

            java_file = self.index.find(location["file"])
            if not java_file:
                continue

            if location["file"] not in files:
                files[location["file"]] = ContextFile(
                    path=str(java_file),
                    reason="Mentioned in stack trace",
                    score=1.0
                )

        return FailureContext(
            files=list(files.values()),
            token_budget=self.token_budget
        )
