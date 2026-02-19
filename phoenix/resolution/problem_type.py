from enum import Enum, auto


class ProblemDomain(Enum):
    CODE = auto()
    INFRA = auto()
    CONFIG = auto()
    DEPENDENCY = auto()
    DATA = auto()
    SECURITY = auto()
    UNKNOWN = auto()


class ProblemType(Enum):
    # CODE
    NULL_SAFETY = auto()
    UNHANDLED_RUNTIME = auto()
    INVALID_STATE = auto()
    LOGIC_ERROR = auto()

    # INFRA
    MEMORY_EXHAUSTION = auto()
    CPU_SATURATION = auto()
    DISK_PRESSURE = auto()
    NETWORK_FAILURE = auto()

    # CONFIG
    MISCONFIGURATION = auto()
    MISSING_ENV = auto()
    INVALID_PROPERTY = auto()

    # DEPENDENCY
    VERSION_CONFLICT = auto()
    SERVICE_UNAVAILABLE = auto()

    # DATA
    DATA_CORRUPTION = auto()
    SCHEMA_MISMATCH = auto()

    # SECURITY
    AUTH_FAILURE = auto()
    PERMISSION_DENIED = auto()

    # FALLBACK
    UNCLASSIFIED = auto()
