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


def test_static_hud_has_face_layout_foundation():
    html = (HUD_ROOT / 'index.html').read_text(encoding='utf-8')
    css = (HUD_ROOT / 'style.css').read_text(encoding='utf-8')

    assert 'Lucifer Face' in html
    assert 'face-stage' in html
    assert 'face-core' in html
    assert '.face-panel' in css
    assert '.face-stage' in css
    assert '.face-core' in css
    assert '.mouth' in css


def test_static_hud_uses_layout_sections_without_changing_js_contract():
    html = (HUD_ROOT / 'index.html').read_text(encoding='utf-8')

    assert 'hud-topbar' in html
    assert 'hud-grid' in html
    assert 'healthButton' in html
    assert 'healthBadge' in html
    assert 'healthStatus' in html
    assert 'healthProvider' in html
    assert 'healthAdapter' in html
    assert 'chatInput' in html
    assert 'chatButton' in html
    assert 'voiceOutput' in html
    assert 'visualOutput' in html
    assert 'traceOutput' in html


def test_static_hud_face_has_state_contract():
    html = (HUD_ROOT / 'index.html').read_text(encoding='utf-8')
    js = (HUD_ROOT / 'app.js').read_text(encoding='utf-8')
    css = (HUD_ROOT / 'style.css').read_text(encoding='utf-8')

    assert 'id="faceCore"' in html
    assert 'face-idle' in html
    assert 'function setFaceState(state)' in js
    assert '"online"' in js
    assert '"offline"' in js
    assert '"speaking"' in js
    assert '"error"' in js
    assert 'face-core face-' in js
    assert '.face-idle' in css
    assert '.face-online' in css
    assert '.face-offline' in css
    assert '.face-speaking' in css
    assert '.face-error' in css


def test_static_hud_has_speaking_pulse_animation():
    css = (HUD_ROOT / 'style.css').read_text(encoding='utf-8')

    assert '@keyframes speakingPulse' in css
    assert '@keyframes mouthTalk' in css
    assert 'animation: speakingPulse' in css
    assert 'animation: mouthTalk' in css
    assert '.face-speaking .mouth' in css


def test_static_hud_returns_face_to_online_after_speaking():
    js = (HUD_ROOT / 'app.js').read_text(encoding='utf-8')

    assert 'SPEAKING_RETURN_DELAY_MS' in js
    assert 'function returnFaceToOnlineAfterSpeaking()' in js
    assert 'window.setTimeout' in js
    assert 'setFaceState("online")' in js
    assert 'returnFaceToOnlineAfterSpeaking();' in js


def test_static_hud_face_has_thinking_state():
    js = (HUD_ROOT / 'app.js').read_text(encoding='utf-8')
    css = (HUD_ROOT / 'style.css').read_text(encoding='utf-8')

    assert '"thinking"' in js
    assert 'setFaceState("thinking")' in js
    assert 'Thinking...' in js
    assert '.face-thinking' in css
    assert '@keyframes thinkingGlow' in css
    assert '#ffd660' in css


def test_static_hud_face_states_have_distinct_colors():
    css = (HUD_ROOT / 'style.css').read_text(encoding='utf-8')

    assert '--face-online: #4da3ff;' in css
    assert '--face-thinking: #ffd660;' in css
    assert '--face-speaking: #b45cff;' in css
    assert '--face-offline: #6f8799;' in css
    assert '--face-error: #ff4d5e;' in css
    assert '.face-core.face-online' in css
    assert '.face-core.face-thinking' in css
    assert '.face-core.face-speaking' in css
    assert '.face-core.face-offline' in css
    assert '.face-core.face-error' in css


def test_static_hud_face_design_contract_is_documented_in_css():
    css = (HUD_ROOT / 'style.css').read_text(encoding='utf-8')

    assert 'Lucifer face design contract' in css
    assert '--face-online: #4da3ff;' in css
    assert '--face-thinking: #ffd660;' in css
    assert '--face-speaking: #b45cff;' in css
    assert '--face-chat: #38f2a1;' in css
    assert '--face-offline: #6f8799;' in css
    assert '--face-error: #ff4d5e;' in css


def test_static_hud_shows_runtime_provider_badges():
    html = (HUD_ROOT / 'index.html').read_text(encoding='utf-8')
    js = (HUD_ROOT / 'app.js').read_text(encoding='utf-8')
    css = (HUD_ROOT / 'style.css').read_text(encoding='utf-8')

    assert 'providerBadge' in html
    assert 'adapterBadge' in html
    assert 'runtime-badges' in html
    assert 'const providerBadge' in js
    assert 'const adapterBadge' in js
    assert 'function setRuntimeBadges' in js
    assert 'data.provider_name' in js
    assert 'data.adapter_name' in js
    assert '.runtime-badges' in css
    assert '.badge-provider-ollama' in css
