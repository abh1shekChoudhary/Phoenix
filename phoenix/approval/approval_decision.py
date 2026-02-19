from enum import Enum


class ApprovalDecision(Enum):
    APPROVE = "approve"
    REJECT = "reject"
    REQUEST_MORE_INFO = "request_more_info"
