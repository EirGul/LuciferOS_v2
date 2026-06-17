from dataclasses import dataclass
from enum import IntEnum


class RiskLevel(IntEnum):
    CONVERSATION = 0
    SAFE_LOCAL = 1
    CHANGES_LOCAL = 2
    EXTERNAL_OR_IRREVERSIBLE = 3
    ADMIN_OR_TRUSTED_PROJECT = 4


@dataclass(frozen=True)
class PermissionDecision:
    allowed: bool
    requires_confirmation: bool
    risk_level: RiskLevel
    reason: str
