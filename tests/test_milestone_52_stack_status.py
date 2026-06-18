from lucifer_os.interfaces.stack_status import build_stack_status


def test_stack_status_mentions_core_cli_command():
    status = build_stack_status()

    assert 'LuciferOS stack status' in status
    assert 'py -m lucifer_os.interfaces.cli "Hei Lucifer"' in status


def test_stack_status_mentions_api_commands():
    status = build_stack_status()

    assert 'start_lucifer_api.bat' in status
    assert 'py -m lucifer_os.interfaces.cli --api-health' in status
    assert 'py -m lucifer_os.interfaces.cli --api "Hei Lucifer"' in status


def test_stack_status_mentions_hud_preview_commands():
    status = build_stack_status()

    assert 'py -m lucifer_os.interfaces.hud_preview health' in status
    assert 'py -m lucifer_os.interfaces.hud_preview chat "Hei Lucifer"' in status
    assert 'check_lucifer_hud_preview.bat' in status


def test_stack_status_mentions_recommended_development_order():
    status = build_stack_status()

    assert 'Recommended development order:' in status
    assert 'py -m pytest' in status
    assert 'start_lucifer_api.bat' in status
