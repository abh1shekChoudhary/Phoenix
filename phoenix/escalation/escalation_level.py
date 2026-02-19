from enum import Enum


class EscalationLevel(Enum):
    INFO = 0
    WARNING = 1
    HIGH = 2
    CRITICAL = 3

    def __str__(self):
        return self.name
