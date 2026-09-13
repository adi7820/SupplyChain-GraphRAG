import hashlib
from hmac import digest
from .config import Config, get_config
import logging
from openai import OpenAI
from pathlib import Path
from typing import Any
import time
import os
log = logging.getLogger(__name__)

_USD_PER_1M_INPUT = 0.00
_USD_PER_1M_OUTPUT = 0.00

class Usage:
  def __init__(self) -> None:
    self.input_tokens = 0
    self.output_tokens = 0
    self.calls = 0
    self.embed_calls = 0
    self.embed_cache_hits = 0

  def add(self, resp: Any) -> None:
    self.calls += 1
    meta = getattr(resp, "usage_metadata", None)
    if meta is None:
      return
    self.input_tokens += getattr(meta, "prompt_token_count", 0) or 0
    self.output_tokens += getattr(meta, "candidates_token_count", 0) or 0

def _is_retryable(exc: Exception) -> bool:
  text = f"{type(exc).__name__} {exc}".lower()
  return any(
      marker in text
      for marker in (
          # HTTP-level
          "429", "resource_exhausted", "503", "unavailable", "500",
          "internal", "deadline", "timeout",
          # Transport-level: the connection failed, the request never landed
          "remoteprotocolerror", "server disconnected", "connectionerror",
          "connecterror", "connection reset", "connection aborted",
          "readerror", "writeerror", "protocolerror", "incomplete read",
          "ssl", "eof occurred",
      )
  )

class LLMClient:
  def __init__(self, config: Config | None = None, cache_dir: Path | None = None):
    self.config = config or get_config()
    self.usage = Usage()
    self.client = OpenAI(
      base_url=self.config.base_url,
      api_key=self.config.openrouter_api_key,
    )

  def _call(self, prompt: str, cfg: dict, attempts: int = 4) -> Any:
    last: Exception | None = None
    if cfg.get("system_instruction"):
      messages = [
        {"role": "system", "content": cfg["system_instruction"]},
        {"role": "user", "content": prompt},
      ]
    else:
      messages = [
        {"role": "user", "content": prompt},
      ]
    for attempt in range(attempts):
      try:
        resp = self.client.chat.completions.create(
          model=self.config.llm["model"],
          messages=messages,
          extra_body={"reasoning": {"enabled": False}}
          
        )
        # self.usage.add
        return resp.choices[0].message.content
      except Exception as e:
        last = e
        if not _is_retryable(e) or attempt == attempts - 1:
            raise
        delay = 2 ** attempt
        log.warning("LLM call failed (%s); retrying in %ss",
                    type(e).__name__, delay)
        time.sleep(delay)

    raise RuntimeError("unreachable retry loop exit") from last
    

  def generate(self, prompt: str, *, system: str | None = None, temperature: float | None = None) -> str:
    cfg = {
      "temperature": self.config.llm["temperature"] if temperature is None else temperature,
      "max_tokens": self.config.llm["max_output_tokens"],
      "system_instruction": system
    }
    
    resp = self._call(prompt, cfg)

    return (resp or "").strip()

  def _cache_key(self, text: str, task: str, model: str, dims: int) -> Path:
    digest = hashlib.sha256(
      f"{model}|{dims}|{task}|{text}".encode("utf-8")
    ).hexdigest()
    return self.cache_dir / f"{digest}.pkl"

if __name__ == "__main__":
    client = LLMClient()
    print(client.generate("Hello, how are you?"))