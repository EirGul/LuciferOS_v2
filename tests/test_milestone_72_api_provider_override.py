from lucifer_os.interfaces.api_server import resolve_api_provider_name


def test_api_provider_override_defaults_to_none_when_env_is_missing(monkeypatch):
    monkeypatch.delenv("LUCIFER_PROVIDER", raising=False)

    assert resolve_api_provider_name() is None


def test_api_provider_override_reads_lucifer_provider_env(monkeypatch):
    monkeypatch.setenv("LUCIFER_PROVIDER", "ollama")

    assert resolve_api_provider_name() == "ollama"


def test_api_provider_override_normalizes_env_value(monkeypatch):
    monkeypatch.setenv("LUCIFER_PROVIDER", "  OLLAMA  ")

    assert resolve_api_provider_name() == "ollama"


def test_api_provider_override_explicit_argument_wins_over_env(monkeypatch):
    monkeypatch.setenv("LUCIFER_PROVIDER", "ollama")

    assert resolve_api_provider_name("offline") == "offline"


def test_api_provider_override_empty_explicit_argument_becomes_none(monkeypatch):
    monkeypatch.setenv("LUCIFER_PROVIDER", "ollama")

    assert resolve_api_provider_name("   ") is None
