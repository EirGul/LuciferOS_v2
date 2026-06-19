from __future__ import annotations

from dataclasses import dataclass

from lucifer_os.memory.models import MemoryScope, MemoryType


@dataclass(frozen=True, slots=True)
class MemoryWriteRequest:
    content: str
    type: MemoryType
    scope: MemoryScope
    source: str = "user"


@dataclass(frozen=True, slots=True)
class MemoryUpdateRequest:
    memory_id: str
    content: str
    type: MemoryType
    scope: MemoryScope
    source: str = "user"


@dataclass(frozen=True, slots=True)
class MemoryDeleteRequest:
    memory_id: str
    source: str = "user"


@dataclass(frozen=True, slots=True)
class MemoryDecision:
    allowed: bool
    requires_confirmation: bool
    audit_reason: str


class MemoryPolicy:
    HIGH_IMPACT_TYPES = frozenset({
        MemoryType.RELATIONSHIP,
        MemoryType.USER_INSTRUCTION,
        MemoryType.COMMAND_ALIAS,
    })

    HIGH_IMPACT_SCOPES = frozenset({
        MemoryScope.GLOBAL,
        MemoryScope.TOOL_SPECIFIC,
    })

    def evaluate_write(self, request: MemoryWriteRequest) -> MemoryDecision:
        content = request.content.strip()

        if not content:
            return MemoryDecision(
                allowed=False,
                requires_confirmation=False,
                audit_reason="Memory write rejected: empty content.",
            )

        if request.type in self.HIGH_IMPACT_TYPES or request.scope in self.HIGH_IMPACT_SCOPES:
            return MemoryDecision(
                allowed=True,
                requires_confirmation=True,
                audit_reason="Memory write allowed but requires confirmation due to high-impact type or scope.",
            )

        return MemoryDecision(
            allowed=True,
            requires_confirmation=False,
            audit_reason="Memory write allowed.",
        )

    def evaluate_update(self, request: MemoryUpdateRequest) -> MemoryDecision:
        if not request.memory_id.strip():
            return MemoryDecision(
                allowed=False,
                requires_confirmation=False,
                audit_reason="Memory update rejected: empty memory id.",
            )

        if not request.content.strip():
            return MemoryDecision(
                allowed=False,
                requires_confirmation=False,
                audit_reason="Memory update rejected: empty content.",
            )

        if request.type in self.HIGH_IMPACT_TYPES or request.scope in self.HIGH_IMPACT_SCOPES:
            return MemoryDecision(
                allowed=True,
                requires_confirmation=True,
                audit_reason="Memory update allowed but requires confirmation due to high-impact type or scope.",
            )

        return MemoryDecision(
            allowed=True,
            requires_confirmation=False,
            audit_reason="Memory update allowed.",
        )

    def evaluate_delete(self, request: MemoryDeleteRequest) -> MemoryDecision:
        if not request.memory_id.strip():
            return MemoryDecision(
                allowed=False,
                requires_confirmation=False,
                audit_reason="Memory delete rejected: empty memory id.",
            )

        return MemoryDecision(
            allowed=True,
            requires_confirmation=True,
            audit_reason="Memory delete allowed but requires confirmation.",
        )
