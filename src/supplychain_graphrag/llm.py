from openai import OpenAI
from .config import cfg, require_api_key


client = OpenAI(
  base_url=cfg.base_url,
  api_key=require_api_key(cfg.api_key, "OpenRouter"),
)

if __name__ == "__main__":
    print("ok")