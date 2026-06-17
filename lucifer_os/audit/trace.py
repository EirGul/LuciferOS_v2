from dataclasses import dataclass, field
from datetime import datetime, UTC
from uuid import uuid4


@dataclass(frozen=True)
class AuditEvent:
    event_type: str
    message: str
    trace_id: str
    timestamp: str
    metadata: dict[str, str] = field(default_factory=dict)


class AuditTrace:
    def __init__(self):
        self.trace_id = str(uuid4())
        self._events: list[AuditEvent] = []

    def record(self, event_type: str, message: str, metadata: dict[str, str] | None = None) -> AuditEvent:
        event = AuditEvent(
            event_type=event_type,
            message=message,
            trace_id=self.trace_id,
            timestamp=datetime.now(UTC).isoformat(),
            metadata=metadata or {},
        )
        self._events.append(event)
        return event

    def events(self) -> list[AuditEvent]:
        return list(self._events)
