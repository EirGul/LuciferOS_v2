from lucifer_os.audit.trace import AuditTrace
from lucifer_os.permissions.engine import PermissionEngine
from lucifer_os.permissions.risk import RiskLevel


def test_permission_engine_allows_low_risk_without_confirmation():
    engine = PermissionEngine()

    decision = engine.evaluate(RiskLevel.SAFE_LOCAL)

    assert decision.allowed is True
    assert decision.requires_confirmation is False
    assert decision.risk_level == RiskLevel.SAFE_LOCAL
    assert decision.reason


def test_permission_engine_blocks_higher_risk_until_confirmation():
    engine = PermissionEngine()

    decision = engine.evaluate(RiskLevel.CHANGES_LOCAL)

    assert decision.allowed is False
    assert decision.requires_confirmation is True
    assert decision.risk_level == RiskLevel.CHANGES_LOCAL
    assert decision.reason


def test_permission_engine_requires_confirmation_for_external_or_irreversible():
    engine = PermissionEngine()

    decision = engine.evaluate(RiskLevel.EXTERNAL_OR_IRREVERSIBLE)

    assert decision.allowed is False
    assert decision.requires_confirmation is True
    assert decision.risk_level == RiskLevel.EXTERNAL_OR_IRREVERSIBLE


def test_audit_trace_records_events_with_same_trace_id():
    trace = AuditTrace()

    first = trace.record(
        event_type='intent_detected',
        message='Detected user intent.',
        metadata={'intent': 'status'},
    )
    second = trace.record(
        event_type='permission_checked',
        message='Permission evaluated.',
        metadata={'risk_level': '1'},
    )

    events = trace.events()

    assert len(events) == 2
    assert first.trace_id == trace.trace_id
    assert second.trace_id == trace.trace_id
    assert first.trace_id == second.trace_id
    assert events[0].metadata['intent'] == 'status'
    assert events[1].metadata['risk_level'] == '1'
    assert events[0].timestamp
    assert events[1].timestamp


def test_audit_trace_returns_copy_of_events():
    trace = AuditTrace()
    trace.record(event_type='test', message='Test event.')

    events = trace.events()
    events.clear()

    assert len(trace.events()) == 1
