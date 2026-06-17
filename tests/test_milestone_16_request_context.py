from lucifer_os.core.core import CoreRequest, LuciferCore


def test_core_request_has_safe_defaults():
    request = CoreRequest(text='Hei Lucifer')

    assert request.text == 'Hei Lucifer'
    assert request.interface == 'cli'
    assert request.session_id is None
    assert request.metadata == {}


def test_core_request_accepts_interface_session_and_metadata():
    request = CoreRequest(
        text='Hei Lucifer',
        interface='voice',
        session_id='session-1',
        metadata={'source': 'test'},
    )

    assert request.interface == 'voice'
    assert request.session_id == 'session-1'
    assert request.metadata == {'source': 'test'}


def test_core_audit_records_request_context():
    core = LuciferCore()

    result = core.handle(
        CoreRequest(
            text='Hei Lucifer',
            interface='voice',
            session_id='session-1',
            metadata={'source': 'test'},
        )
    )

    request_events = [event for event in result.audit_events if event.event_type == 'request_received']

    assert request_events
    assert request_events[0].metadata['text'] == 'Hei Lucifer'
    assert request_events[0].metadata['interface'] == 'voice'
    assert request_events[0].metadata['session_id'] == 'session-1'
    assert request_events[0].metadata['request_metadata'] == "{'source': 'test'}"
