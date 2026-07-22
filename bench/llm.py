"""Multi-model LLM client — unified interface over OpenAI-compatible + Anthropic APIs.

Usage:
    llm = LLMClient(config)
    text, usage = await llm.chat("deepseek-v4-pro", system="...", user="...",
                                  temperature=0.7, seed=42)
"""

import os
import time
import asyncio
from dataclasses import dataclass, field
from typing import Optional


@dataclass
class Usage:
    input_tokens: int = 0
    output_tokens: int = 0
    cached_input_tokens: int = 0


# ── Retryable HTTP status codes ──────────────────────────────────────

RETRYABLE_STATUS = {408, 429, 500, 502, 503, 504}
NON_RETRYABLE_STATUS = {400, 401, 403, 404, 422}

MAX_RETRIES = 5
RETRY_BASE_DELAY = 1.0       # 1, 2, 4, 8, 16
MAX_CONSECUTIVE_API_ERRORS = 10


class LLMClient:
    """Unified chat interface for multiple model providers."""

    def __init__(self, config: dict):
        """
        Args:
            config: the full config dict (parsed from config.yaml).
                    Must have a 'models' key with per-model settings.
        """
        self.models = config.get("models", {})
        self._key_cache: dict[str, str] = {}  # env_var -> value cache

    # ── Public API ──────────────────────────────────────────────────

    async def chat(
        self,
        model_key: str,
        system: str,
        user: str,
        temperature: float = 0.7,
        seed: "int | None" = None,
    ) -> tuple[str, Usage]:
        """Send a single-turn chat and return (text, usage).

        Args:
            model_key: key into config.models (e.g. "deepseek-v4-pro")
            system: system message content
            user: user message content
            temperature: sampling temperature
            seed: random seed (may be ignored by some providers)

        Returns:
            (response_text, Usage)

        Raises:
            ValueError: if model_key is unknown
            RuntimeError: if all retries exhausted
        """
        cfg = self.models.get(model_key)
        if cfg is None:
            raise ValueError(f"Unknown model key: {model_key}. Known: {list(self.models)}")

        provider = cfg.get("provider", "openai_compatible")

        if provider == "openai_compatible":
            return await self._chat_openai_compatible(cfg, system, user, temperature, seed)
        elif provider == "anthropic":
            return await self._chat_anthropic(cfg, system, user, temperature, seed)
        else:
            raise ValueError(f"Unknown provider: {provider}")

    # ── OpenAI-compatible (DeepSeek, etc.) ──────────────────────────

    async def _chat_openai_compatible(
        self, cfg: dict, system: str, user: str,
        temperature: float, seed: "int | None",
    ) -> tuple[str, Usage]:
        from openai import AsyncOpenAI

        api_key = self._get_api_key(cfg)
        client = AsyncOpenAI(
            api_key=api_key,
            base_url=cfg["base_url"],
            max_retries=0,  # we do our own retry logic
        )

        messages = [
            {"role": "system", "content": system},
            {"role": "user", "content": user},
        ]

        extra_body = dict(cfg.get("extra_body", {}))
        kwargs = {
            "model": cfg["model_name"],
            "messages": messages,
            "temperature": temperature,
            "max_tokens": cfg.get("max_output_tokens", 16384),
        }
        if seed is not None:
            kwargs["seed"] = seed
        if extra_body:
            kwargs["extra_body"] = extra_body

        last_error = None
        for attempt in range(MAX_RETRIES + 1):
            try:
                response = await client.chat.completions.create(**kwargs)
                text = response.choices[0].message.content or ""

                # Handle empty content (DeepSeek reasoning mode quirk)
                if not text:
                    # Try reasoning_content if available
                    reasoning = getattr(
                        response.choices[0].message, "reasoning_content", None
                    )
                    if reasoning:
                        text = reasoning
                    else:
                        if attempt < 2:
                            delay = RETRY_BASE_DELAY * (2 ** attempt)
                            await asyncio.sleep(delay)
                            continue
                        # After 2 retries, return empty — caller handles parse_error

                cached = 0
                if hasattr(response.usage, "prompt_cache_hit_tokens"):
                    cached = response.usage.prompt_cache_hit_tokens or 0
                elif hasattr(response.usage, "prompt_tokens_details"):
                    details = response.usage.prompt_tokens_details
                    if details and hasattr(details, "cached_tokens"):
                        cached = details.cached_tokens or 0
                usage = Usage(
                    input_tokens=getattr(response.usage, "prompt_tokens", 0) or 0,
                    output_tokens=getattr(response.usage, "completion_tokens", 0) or 0,
                    cached_input_tokens=cached,
                )
                return text, usage

            except Exception as e:
                last_error = e
                status = _extract_status(e)
                if status in NON_RETRYABLE_STATUS:
                    raise RuntimeError(
                        f"Non-retryable API error (status {status}): {e}"
                    ) from e
                if attempt < MAX_RETRIES:
                    delay = RETRY_BASE_DELAY * (2 ** attempt)
                    await asyncio.sleep(delay)
                else:
                    raise RuntimeError(
                        f"API call failed after {MAX_RETRIES} retries: {last_error}"
                    ) from last_error

        raise RuntimeError(f"API call failed: {last_error}")

    # ── Anthropic ───────────────────────────────────────────────────

    async def _chat_anthropic(
        self, cfg: dict, system: str, user: str,
        temperature: float, seed: "int | None",
    ) -> tuple[str, Usage]:
        from anthropic import AsyncAnthropic

        api_key = self._get_api_key(cfg)
        client = AsyncAnthropic(api_key=api_key, max_retries=0)

        system_content = system
        # If cache_system_prefix is enabled, wrap system in cache_control
        if cfg.get("cache_system_prefix"):
            system_content = [
                {
                    "type": "text",
                    "text": system,
                    "cache_control": {"type": "ephemeral"},
                }
            ]

        kwargs = {
            "model": cfg["model_name"],
            "system": system_content,
            "messages": [{"role": "user", "content": user}],
            "temperature": temperature,
            "max_tokens": cfg.get("max_output_tokens", 16384),
        }

        last_error = None
        for attempt in range(MAX_RETRIES + 1):
            try:
                response = await client.messages.create(**kwargs)
                text = "".join(
                    block.text for block in response.content if block.type == "text"
                )
                usage = Usage(
                    input_tokens=response.usage.input_tokens or 0,
                    output_tokens=response.usage.output_tokens or 0,
                    cached_input_tokens=getattr(response.usage, "cache_read_input_tokens", 0) or 0,
                )
                return text, usage

            except Exception as e:
                last_error = e
                status = _extract_status(e)
                if status in NON_RETRYABLE_STATUS:
                    raise RuntimeError(
                        f"Non-retryable API error (status {status}): {e}"
                    ) from e
                if attempt < MAX_RETRIES:
                    delay = RETRY_BASE_DELAY * (2 ** attempt)
                    await asyncio.sleep(delay)
                else:
                    raise RuntimeError(
                        f"API call failed after {MAX_RETRIES} retries: {last_error}"
                    ) from last_error

        raise RuntimeError(f"API call failed: {last_error}")

    # ── Helpers ─────────────────────────────────────────────────────

    def _get_api_key(self, cfg: dict) -> str:
        # Direct key in config takes precedence
        if "api_key" in cfg:
            return cfg["api_key"]

        env_var = cfg.get("api_key_env")
        if not env_var:
            raise ValueError(f"Model config missing 'api_key' or 'api_key_env': {cfg}")
        if env_var not in self._key_cache:
            key = os.environ.get(env_var)
            if not key:
                raise RuntimeError(
                    f"Environment variable {env_var} is not set. "
                    f"Set it or configure api_key in config.yaml for this model."
                )
            self._key_cache[env_var] = key
        return self._key_cache[env_var]


def _extract_status(exc: Exception) -> "int | None":
    """Try to extract HTTP status code from various exception types."""
    if hasattr(exc, "status_code"):
        return exc.status_code
    if hasattr(exc, "status"):
        return exc.status
    # Check nested __cause__ or __context__
    cause = exc.__cause__ or exc.__context__
    if cause is not None:
        return _extract_status(cause)
    return None
