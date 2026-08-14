import json
import re
from typing import Any

TOKEN_PATTERNS = [
    re.compile(r"(?i)(new_bbs_serviceToken(?:%3D|=|\"\s*:\s*\")?)([^;\s\"&]+)"),
    re.compile(r"(?i)(authorization\s*[:=]\s*)(\S+)"),
]

def mask_token(token: str) -> str:
    if not token:
        return ""
    if len(token) <= 8:
        return "****"
    return f"{token[:4]}****{token[-3:]}"

def redact_text(value: Any) -> str:
    text = value if isinstance(value, str) else json.dumps(value, ensure_ascii=False, default=str)
    for pattern in TOKEN_PATTERNS:
        text = pattern.sub(lambda m: m.group(1) + mask_token(m.group(2)), text)
    return text
