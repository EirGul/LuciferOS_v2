from dataclasses import dataclass
from typing import Literal


IntentType = Literal['conversation', 'command', 'confirmation', 'unknown']


@dataclass(frozen=True)
class Intent:
    type: IntentType
    name: str
    confidence: float
    raw_text: str
    normalized_text: str
