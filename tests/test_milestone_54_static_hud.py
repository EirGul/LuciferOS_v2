from pathlib import Path


HUD_ROOT = Path('hud')


def test_static_hud_files_exist():
    assert (HUD_ROOT / 'index.html').is_file()
    assert (HUD_ROOT / 'style.css').is_file()
    assert (HUD_ROOT / 'app.js').is_file()


def test_static_hud_index_references_assets():
    html = (HUD_ROOT / 'index.html').read_text(encoding='utf-8')

    assert 'LuciferOS HUD' in html
    assert 'style.css' in html
    assert 'app.js' in html
    assert 'healthButton' in html
    assert 'chatInput' in html


def test_static_hud_app_targets_local_api():
    js = (HUD_ROOT / 'app.js').read_text(encoding='utf-8')

    assert 'http://127.0.0.1:8787' in js
    assert '/health' in js
    assert '/chat' in js
    assert 'static-hud' in js
