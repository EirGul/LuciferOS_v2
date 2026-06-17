from lucifer_os.core.core import CoreRequest, LuciferCore


def test_core_routes_conversation_to_offline_provider():
    core = LuciferCore()

    result = core.handle(CoreRequest(text="Hei Lucifer, fungerer du?"))

    assert result.intent.type == "conversation"
    assert result.intent.name == "free_chat"
    assert result.plan.type == "respond"
    assert result.permission.allowed is True
    assert result.response.risk_level == 0
    assert result.response.requires_confirmation is False
    assert result.response.trace_id == result.trace_id
    assert len(result.audit_events) >= 4
    assert result.audit_events[0].trace_id == result.trace_id