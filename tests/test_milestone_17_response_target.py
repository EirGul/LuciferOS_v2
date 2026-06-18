from lucifer_os.core.core import CoreRequest, LuciferCore
from lucifer_os.response.target import normalize_response_channel


def test_normalize_response_channel_accepts_known_interfaces():
    assert normalize_response_channel('cli') == 'cli'
    assert normalize_response_channel('voice') == 'voice'
    assert normalize_response_channel('hud') == 'hud'
    assert normalize_response_channel('api') == 'api'


def test_normalize_response_channel_normalizes_case_and_spacing():
    assert normalize_response_channel('  VOICE  ') == 'voice'


def test_normalize_response_channel_falls_back_to_cli_for_unknown_interface():
    assert normalize_response_channel('unknown') == 'cli'


def test_core_sets_visual_channel_from_request_interface_voice():
    core = LuciferCore()

    result = core.handle(CoreRequest(text='Hei Lucifer', interface='voice'))

    assert result.response.visual_channel == 'voice'


def test_core_sets_visual_channel_from_request_interface_hud():
    core = LuciferCore()

    result = core.handle(CoreRequest(text='Hei Lucifer', interface='hud'))

    assert result.response.visual_channel == 'hud'


def test_core_sets_visual_channel_from_request_interface_api():
    core = LuciferCore()

    result = core.handle(CoreRequest(text='Hei Lucifer', interface='api'))

    assert result.response.visual_channel == 'api'


def test_core_falls_back_to_cli_for_unknown_interface():
    core = LuciferCore()

    result = core.handle(CoreRequest(text='Hei Lucifer', interface='unknown'))

    assert result.response.visual_channel == 'cli'
