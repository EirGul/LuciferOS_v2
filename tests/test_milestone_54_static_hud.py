from pathlib import Path


HUD_ROOT = Path('hud')


def test_static_hud_files_exist():
    assert (HUD_ROOT / 'index.html').is_file()
    assert (HUD_ROOT / 'style.css').is_file()
    assert (HUD_ROOT / 'app.js').is_file()


def test_static_hud_index_references_assets_and_controls():
    html = (HUD_ROOT / 'index.html').read_text(encoding='utf-8')

    assert 'LuciferOS HUD' in html
    assert 'style.css' in html
    assert 'app.js' in html
    assert 'healthButton' in html
    assert 'healthBadge' in html
    assert 'healthProvider' in html
    assert 'chatInput' in html
    assert 'voiceOutput' in html
    assert 'visualOutput' in html
    assert 'traceOutput' in html


def test_static_hud_app_targets_local_api():
    js = (HUD_ROOT / 'app.js').read_text(encoding='utf-8')

    assert 'http://127.0.0.1:8787' in js
    assert '/health' in js
    assert '/chat' in js
    assert 'static-hud' in js


def test_static_hud_app_renders_health_as_cards_not_raw_json():
    js = (HUD_ROOT / 'app.js').read_text(encoding='utf-8')

    assert 'function renderHealth(data)' in js
    assert 'healthStatus.textContent' in js
    assert 'healthProvider.textContent' in js
    assert 'healthAdapter.textContent' in js
    assert 'healthOutput' not in js
    assert 'chatOutput' not in js


def test_static_hud_app_renders_chat_as_response_cards():
    js = (HUD_ROOT / 'app.js').read_text(encoding='utf-8')

    assert 'function renderChat(data)' in js
    assert 'voiceOutput.textContent' in js
    assert 'visualOutput.textContent' in js
    assert 'traceOutput.textContent' in js


def test_static_hud_css_contains_card_and_badge_styles():
    css = (HUD_ROOT / 'style.css').read_text(encoding='utf-8')

    assert '.badge-online' in css
    assert '.badge-offline' in css
    assert '.status-card' in css
    assert '.response-card' in css
