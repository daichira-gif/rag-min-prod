from __future__ import annotations
from typing import Tuple

DANGEROUS_PHRASES = [
    "ignore previous instructions",
    "disregard prior instructions",
    "system prompt",
    "you are now",
]

def is_potential_injection(text: str) -> Tuple[bool, str]:
    lower = text.lower()
    for p in DANGEROUS_PHRASES:
        if p in lower:
            return True, p
    return False, ""
