from typing import List

class StackTraceBuffer:
    def __init__(self):
        self.lines: List[str] = []
        self.active = False

    def start(self, line: str):
        self.lines = [line]
        self.active = True

    def add(self, line: str):
        if self.active:
            self.lines.append(line)

    def stop(self):
        trace = self.lines[:]
        self.lines = []
        self.active = False
        return trace

    def is_active(self) -> bool:
        return self.active
