from dataclasses import dataclass, field
from enum import Enum
from typing import Any

class ResultKind(str, Enum):
    VALID="VALID"; EXPIRED="EXPIRED"; INVALID="INVALID"; AUTHORIZED="ALREADY AUTHORIZED"
    SUCCESS="SUCCESS"; QUOTA_FULL="QUOTA FULL"; BLOCKED="ACCOUNT BLOCKED"
    NOT_ELIGIBLE="NOT ELIGIBLE"; NETWORK_ERROR="NETWORK ERROR"; UNKNOWN="UNKNOWN RESPONSE"

@dataclass
class ApiResult:
    kind: ResultKind
    message: str
    terminal: bool = False
    verify: bool = False
    deadline: str = ""
    raw: dict[str, Any] = field(default_factory=dict)
