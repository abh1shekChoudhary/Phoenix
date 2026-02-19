from collections import deque
from typing import List

class LogBuffer:
    def __init__(self, max_size: int = 50):
        self.buffer = deque(maxlen=max_size)

    def add(self, line: str):
        self.buffer.append(line)

    def snapshot(self) -> List[str]:
        return list(self.buffer)
