"""Configuration behavior, including actionable failures and key precedence."""

import pytest

from local_setup import create_client


@pytest.fixture(autouse=True)
def clear_provider_environment(monkeypatch):
    for name in ("OPENAI_API_KEY", "OPENAI_BASE_URL", "OPENAI_ORG_ID", "OPENAI_PROJECT_ID"):
        monkeypatch.delenv(name, raising=False)


@pytest.mark.parametrize("value", ["", "   ", "**********", "your_api_key_here"])
def test_missing_or_placeholder_key_is_rejected_without_exposure(tmp_path, value):
    env_file = tmp_path / ".env"
    env_file.write_text(f"OPENAI_API_KEY={value}\n", encoding="utf-8")
    with pytest.raises(ValueError, match="Set OPENAI_API_KEY"):
        create_client(env_file)


def test_course_key_defaults_to_vocareum(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("OPENAI_API_KEY=voc-unit-test\n", encoding="utf-8")
    with create_client(env_file) as client:
        assert str(client.base_url) == "https://openai.vocareum.com/v1/"
        assert client.api_key == "voc-unit-test"


def test_exported_configuration_overrides_dotenv(tmp_path, monkeypatch):
    env_file = tmp_path / ".env"
    env_file.write_text("OPENAI_API_KEY=from-file\nOPENAI_BASE_URL=https://openai.vocareum.com/v1\n", encoding="utf-8")
    monkeypatch.setenv("OPENAI_API_KEY", "exported-test-key")
    monkeypatch.setenv("OPENAI_BASE_URL", "https://api.openai.com/v1")
    with create_client(env_file) as client:
        assert client.api_key == "exported-test-key"
        assert str(client.base_url) == "https://api.openai.com/v1/"


@pytest.mark.parametrize("base_url", ["http://api.openai.com/v1", "", "not-a-url", "https://name:password@example.com/v1"])
def test_invalid_or_credential_bearing_base_url_is_rejected(tmp_path, base_url):
    env_file = tmp_path / ".env"
    env_file.write_text(f"OPENAI_API_KEY=unit-test\nOPENAI_BASE_URL={base_url}\n", encoding="utf-8")
    with pytest.raises(ValueError, match="HTTPS API URL"):
        create_client(env_file)


def test_course_key_cannot_be_sent_to_personal_endpoint(tmp_path):
    env_file = tmp_path / ".env"
    env_file.write_text("OPENAI_API_KEY=voc-private-test-value\nOPENAI_BASE_URL=https://api.openai.com/v1\n", encoding="utf-8")
    with pytest.raises(ValueError, match="Vocareum key requires") as error:
        create_client(env_file)
    assert "voc-private-test-value" not in str(error.value)
