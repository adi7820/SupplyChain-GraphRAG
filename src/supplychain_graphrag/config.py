from openai.types.responses.responses_client_event import ContextManagement
from typing import Any
import yaml
from dataclasses import dataclass
from dotenv import load_dotenv
from pathlib import Path
import os

PROJECT_ROOT = Path(__file__).resolve().parent.parent.parent
load_dotenv(PROJECT_ROOT / ".env")

_PLACEHOLDERS = ("your-", "changeme", "xxx", "<", "replace-me")

def _is_placeholder(value: str) -> bool:
    v = value.strip().strip('"').strip("'").lower()
    return len(v) < 8 or any(marker in v for marker in _PLACEHOLDERS)

class ConfigError(RuntimeError):
    """Raised with an actionable message when setup is incomplete."""

class Config:
    def __init__(self, path: Path | str | None = None) -> None:
        self.root = PROJECT_ROOT
        cfg_path = Path(path) if path else PROJECT_ROOT / "configs" / "base.yaml"
        with open(cfg_path, "r", encoding="utf-8") as fh:
            self._data: dict[str, Any] = yaml.safe_load(fh)

    def section(self, name: str) -> dict[str, Any]:
        return self._data[name]

    @property
    def llm(self) -> dict[str, Any]:
        return self._data["llm"]

    @property
    def openrouter_api_key(self) -> str:
        key = (os.getenv("OPENROUTER_API_KEY") or "").strip().strip("'").strip('"')
        if not key or _is_placeholder(key):
            raise ConfigError(
                "OPENROUTER_API_KEY is missing or still the placeholder from "
                ".env.example.\n"
                "  1. Get a free key: https://openrouter.ai/keys\n"
                "  2. copy .env.example .env   (Linux/macOS: cp)\n"
                "  3. Replace 'your-openrouter-api-key-here' with the real value.\n"
                "Note: `python run.py test` runs the full unit suite with no key."
            )
        return key

    @property
    def base_url(self) -> str:
        env_url = (os.getenv("OPENROUTER_BASE_URL") or "").strip().strip("'").strip('"')
        return env_url or self._data.get("base_url", "https://openrouter.ai/api/v1")

_cached: Config | None = None

def get_config() -> Config:
    global _cached
    if _cached is None:
        _cached = Config()
    return _cached


def require_api_key(value: str, name: str) -> str:
    if not value:
        raise RuntimeError(f"Missing API key for {name}")

    if any(p in value.lower() for p in _PLACEHOLDERS):
        raise RuntimeError(f"Placeholder API key for {name}")
    return value


if __name__ == "__main__":
    print(require_api_key("Hello", "TEST"))