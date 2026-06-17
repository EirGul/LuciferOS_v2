from lucifer_os.core.core import CoreRequest, LuciferCore
from lucifer_os.providers.offline import OfflineProvider


def test_core_status_command_uses_instant_diagnostics_path():
    core = LuciferCore(primary_provider=OfflineProvider())

    result = core.handle(CoreRequest(text='status'))

    assert result.intent.type == 'command'
    assert result.intent.name == 'status'
    assert result.plan.type == 'execute_command'
    assert result.permission.allowed is True
    assert result.response.voice_summary == 'LuciferOS kjører. Aktiv provider er offline.'
    assert result.response.visual_channel == 'cli'
    assert result.response.risk_level == 1
    assert result.response.action == 'status'
    assert 'LuciferOS status' in result.response.visual_text
    assert 'Active provider: offline' in result.response.visual_text
    assert 'Default provider: offline' in result.response.visual_text
    assert 'Ollama model: qwen3.5:9b' in result.response.visual_text
    assert result.response.trace_id == result.trace_id
    assert any(event.event_type == 'diagnostics_created' for event in result.audit_events)
    assert not any(event.event_type == 'provider_selected' for event in result.audit_events)
