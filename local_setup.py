"""Load local notebook configuration without making an API request."""

import os
from pathlib import Path
from urllib.parse import urlparse

from dotenv import load_dotenv
from openai import OpenAI

PROJECT_ROOT = Path(__file__).resolve().parent
DEFAULT_BASE_URL = "https://openai.vocareum.com/v1"


def create_client(env_file: Path | None = None) -> OpenAI:
    """Read .env, preserve exported variables, and construct an SDK client.

    Constructing the client does not send a request. The caller owns the client
    and should close it when finished. Error messages never include the key.
    """
    load_dotenv(env_file if env_file is not None else PROJECT_ROOT / ".env", override=False)
    api_key = os.environ.get("OPENAI_API_KEY", "").strip()
    if not api_key or api_key in {"**********", "your_api_key_here"}:
        raise ValueError("Set OPENAI_API_KEY in the project .env file before running API cells.")

    base_url = os.environ.get("OPENAI_BASE_URL", DEFAULT_BASE_URL).strip().rstrip("/")
    parsed = urlparse(base_url)
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password:
        raise ValueError("OPENAI_BASE_URL must be an HTTPS API URL without embedded credentials.")
    if api_key.startswith("voc-") and parsed.hostname != "openai.vocareum.com":
        raise ValueError("A Vocareum key requires OPENAI_BASE_URL=https://openai.vocareum.com/v1.")

    return OpenAI(api_key=api_key, base_url=base_url, timeout=60.0, max_retries=1)
