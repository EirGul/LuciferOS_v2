from dataclasses import dataclass
from typing import Literal


PlanType = Literal['respond', 'execute_command', 'handle_confirmation', 'ask_clarification']


@dataclass(frozen=True)
class Plan:
    type: PlanType
    intent_name: str
    risk_level: int
    requires_permission: bool
    description: str
