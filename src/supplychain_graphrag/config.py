from dotenv import load_dotenv
from pathlib import Path

PROJECT_ROOT = Path(__file__).resolve().parent.parent
load_dotenv(PROJECT_ROOT / ".env")

_PLACEHOLDERS = ("your-", "changeme", "xxx", "<", "replace-me")

def require_api_key(value: str, name: str) -> str:
    if not value:
        raise RuntimeError(f"Missing API key for {name}")

    if any(p in value.lower() for p in _PLACEHOLDERS):
        raise RuntimeError(f"Placeholder API key for {name}")
    return value


if __name__ == "__main__":
    print(require_api_key("Hello", "TEST"))