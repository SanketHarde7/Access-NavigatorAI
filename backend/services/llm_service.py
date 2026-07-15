from __future__ import annotations
"""
Access Navigator AI - Multi-Provider LLM Service
================================================
Supports Groq, Gemini, and OpenAI with streaming,
automatic fallback, and structured JSON output.
"""
import json
import logging
from typing import AsyncGenerator, Optional, Dict, Any

import aiohttp

from core.config import settings

logger = logging.getLogger("access_navigator.llm")


class LLMProviderError(Exception):
    """Base provider error with safe, non-secret diagnostic context."""

    def __init__(self, provider: str, message: str, status_code: int | None = None):
        super().__init__(message)
        self.provider = provider
        self.status_code = status_code


class LLMRateLimitError(LLMProviderError):
    """Raised when a provider rejects traffic because of quota/rate limits."""


class LLMAuthenticationError(LLMProviderError):
    """Raised when a provider key is missing, invalid, or unauthorized."""


class LLMResponseError(LLMProviderError):
    """Raised when a provider response is malformed or missing required fields."""


class LLMProvider:
    """Abstract LLM provider interface."""

    name = "unknown"

    async def generate(self, system_prompt: str, user_prompt: str, json_mode: bool = True) -> str:
        raise NotImplementedError

    async def generate_stream(self, system_prompt: str, user_prompt: str) -> AsyncGenerator[str, None]:
        raise NotImplementedError


def _sanitize_error_text(text: str, limit: int = 500) -> str:
    """Keep logs actionable while avoiding accidental API-key or prompt leakage."""
    sanitized = text
    for secret in (settings.GROQ_API_KEY, settings.GEMINI_API_KEY):
        if secret:
            sanitized = sanitized.replace(secret, "[redacted]")
    return sanitized[:limit]


def _provider_error(provider: str, status: int, body: str) -> LLMProviderError:
    safe_body = _sanitize_error_text(body)
    message = f"{provider} API returned HTTP {status}: {safe_body}"
    if status == 429:
        return LLMRateLimitError(provider, message, status)
    if status in {401, 403}:
        return LLMAuthenticationError(provider, message, status)
    return LLMProviderError(provider, message, status)


class GroqProvider(LLMProvider):
    """Groq LLM provider with ultra-fast inference."""

    name = "groq"

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.model = settings.GROQ_MODEL
        self.fallback_model = settings.GROQ_FALLBACK_MODEL
        self.base_url = "https://api.groq.com/openai/v1"

    async def _post_completion(self, session: aiohttp.ClientSession, headers: dict[str, str], payload: dict[str, Any]) -> str:
        async with session.post(f"{self.base_url}/chat/completions", headers=headers, json=payload) as resp:
            if resp.status != 200:
                raise _provider_error(self.name, resp.status, await resp.text())
            data = await resp.json()
        try:
            return data["choices"][0]["message"]["content"]
        except (KeyError, IndexError, TypeError) as exc:
            raise LLMResponseError(self.name, "Groq response missing choices[0].message.content") from exc

    async def generate(self, system_prompt: str, user_prompt: str, json_mode: bool = True) -> str:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload: dict[str, Any] = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": settings.LLM_TEMPERATURE,
            "max_tokens": settings.LLM_MAX_TOKENS,
        }

        if json_mode:
            system_prompt += "\nOutput in JSON format."
            payload["messages"][0]["content"] = system_prompt
            payload["response_format"] = {"type": "json_object"}

        timeout = aiohttp.ClientTimeout(total=30)
        try:
            async with aiohttp.ClientSession(timeout=timeout) as session:
                try:
                    return await self._post_completion(session, headers, payload)
                except LLMRateLimitError:
                    # Fallback precision: only same-provider rate limits switch to the smaller Groq fallback model before service-level fallback runs.
                    logger.warning("Groq primary model rate-limited; retrying fallback model", extra={"provider": self.name, "model": self.model})
                    payload["model"] = self.fallback_model
                    return await self._post_completion(session, headers, payload)
        except (aiohttp.ClientError, TimeoutError) as exc:
            logger.warning("Groq transport failure", extra={"provider": self.name, "error_type": type(exc).__name__})
            raise LLMProviderError(self.name, f"Groq transport failure: {type(exc).__name__}") from exc

    async def generate_stream(self, system_prompt: str, user_prompt: str) -> AsyncGenerator[str, None]:
        headers = {
            "Authorization": f"Bearer {self.api_key}",
            "Content-Type": "application/json",
        }

        payload = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "temperature": settings.LLM_TEMPERATURE,
            "max_tokens": settings.LLM_MAX_TOKENS,
            "stream": True,
        }

        timeout = aiohttp.ClientTimeout(total=60)
        try:
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(f"{self.base_url}/chat/completions", headers=headers, json=payload) as resp:
                    if resp.status != 200:
                        raise _provider_error(self.name, resp.status, await resp.text())
                    async for line in resp.content:
                        line_text = line.decode("utf-8").strip()
                        if line_text.startswith("data: ") and line_text != "data: [DONE]":
                            try:
                                chunk = json.loads(line_text[6:])
                                delta = chunk["choices"][0]["delta"].get("content", "")
                            except (json.JSONDecodeError, KeyError, IndexError, TypeError) as exc:
                                logger.debug("Skipped malformed Groq stream chunk", extra={"provider": self.name, "error_type": type(exc).__name__})
                                continue
                            if delta:
                                yield delta
        except (LLMProviderError, aiohttp.ClientError, TimeoutError) as exc:
            logger.warning("Groq streaming degraded", extra={"provider": self.name, "error_type": type(exc).__name__})
            yield f"[LLM stream unavailable: {type(exc).__name__}]"


class GeminiProvider(LLMProvider):
    """Google Gemini provider."""

    name = "gemini"

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.model = settings.GEMINI_MODEL

    async def generate(self, system_prompt: str, user_prompt: str, json_mode: bool = True) -> str:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:generateContent?key={self.api_key}"
        headers = {"Content-Type": "application/json"}
        payload = {
            "system_instruction": {"parts": [{"text": system_prompt}]},
            "contents": [{"role": "user", "parts": [{"text": user_prompt}]}],
            "generationConfig": {
                "temperature": settings.LLM_TEMPERATURE,
                "maxOutputTokens": settings.LLM_MAX_TOKENS,
                "responseMimeType": "application/json" if json_mode else "text/plain",
            },
        }

        timeout = aiohttp.ClientTimeout(total=30)
        try:
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(url, headers=headers, json=payload) as resp:
                    if resp.status != 200:
                        raise _provider_error(self.name, resp.status, await resp.text())
                    data = await resp.json()
            return data["candidates"][0]["content"]["parts"][0]["text"]
        except (KeyError, IndexError, TypeError) as exc:
            raise LLMResponseError(self.name, "Gemini response missing candidates[0].content.parts[0].text") from exc
        except (aiohttp.ClientError, TimeoutError) as exc:
            logger.warning("Gemini transport failure", extra={"provider": self.name, "error_type": type(exc).__name__})
            raise LLMProviderError(self.name, f"Gemini transport failure: {type(exc).__name__}") from exc

    async def generate_stream(self, system_prompt: str, user_prompt: str) -> AsyncGenerator[str, None]:
        url = f"https://generativelanguage.googleapis.com/v1beta/models/{self.model}:streamGenerateContent?alt=sse&key={self.api_key}"
        headers = {"Content-Type": "application/json"}
        payload = {
            "system_instruction": {"parts": [{"text": system_prompt}]},
            "contents": [{"role": "user", "parts": [{"text": user_prompt}]}],
            "generationConfig": {
                "temperature": settings.LLM_TEMPERATURE,
                "maxOutputTokens": settings.LLM_MAX_TOKENS,
            },
        }

        timeout = aiohttp.ClientTimeout(total=60)
        try:
            async with aiohttp.ClientSession(timeout=timeout) as session:
                async with session.post(url, headers=headers, json=payload) as resp:
                    if resp.status != 200:
                        raise _provider_error(self.name, resp.status, await resp.text())
                    async for line in resp.content:
                        line_text = line.decode("utf-8").strip()
                        if line_text.startswith("data: ") and line_text != "data: [DONE]":
                            try:
                                chunk = json.loads(line_text[6:])
                                text = chunk["candidates"][0]["content"]["parts"][0].get("text", "")
                            except (json.JSONDecodeError, KeyError, IndexError, TypeError) as exc:
                                logger.debug("Skipped malformed Gemini stream chunk", extra={"provider": self.name, "error_type": type(exc).__name__})
                                continue
                            if text:
                                yield text
        except (LLMProviderError, aiohttp.ClientError, TimeoutError) as exc:
            logger.warning("Gemini streaming degraded", extra={"provider": self.name, "error_type": type(exc).__name__})
            yield f"[LLM stream unavailable: {type(exc).__name__}]"


class LLMService:
    """
    Unified LLM service with multi-provider support,
    automatic fallback, and streaming capabilities.
    """

    def __init__(self):
        self.providers: Dict[str, LLMProvider] = {}
        self._init_providers()

    def _init_providers(self):
        if settings.GROQ_API_KEY:
            self.providers["groq"] = GroqProvider(settings.GROQ_API_KEY)
        if settings.GEMINI_API_KEY:
            self.providers["gemini"] = GeminiProvider(settings.GEMINI_API_KEY)

    def get_available_providers(self) -> Dict[str, bool]:
        return {name: True for name in self.providers}

    def _get_provider_entry(self, preferred: Optional[str] = None) -> tuple[str, LLMProvider]:
        if preferred and preferred in self.providers:
            return preferred, self.providers[preferred]
        if settings.PRIMARY_LLM in self.providers:
            return settings.PRIMARY_LLM, self.providers[settings.PRIMARY_LLM]
        if self.providers:
            name = next(iter(self.providers))
            return name, self.providers[name]
        raise LLMProviderError("none", "No LLM provider configured. Set GROQ_API_KEY or GEMINI_API_KEY.")

    @staticmethod
    def _parse_json_response(response_text: str, provider_name: str) -> Dict[str, Any]:
        try:
            return json.loads(response_text)
        except json.JSONDecodeError:
            try:
                start = response_text.index("{")
                end = response_text.rindex("}") + 1
                return json.loads(response_text[start:end])
            except (ValueError, json.JSONDecodeError) as exc:
                raise LLMResponseError(provider_name, "JSON parse failed for provider response") from exc

    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        json_mode: bool = True,
        provider: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generate structured response with automatic fallback."""
        provider_name = provider or settings.PRIMARY_LLM
        try:
            provider_name, llm = self._get_provider_entry(provider)
            response_text = await llm.generate(system_prompt, user_prompt, json_mode)
            data = self._parse_json_response(response_text, provider_name) if json_mode else response_text
            return {"success": True, "data": data, "provider": provider_name, "raw": response_text}
        except LLMProviderError as primary_error:
            logger.warning(
                "Primary LLM provider failed; evaluating fallback",
                extra={"provider": provider_name, "error_type": type(primary_error).__name__, "status_code": primary_error.status_code},
            )
            fallback = settings.FALLBACK_LLM
            if fallback != provider_name and fallback in self.providers:
                try:
                    response_text = await self.providers[fallback].generate(system_prompt, user_prompt, json_mode)
                    data = self._parse_json_response(response_text, fallback) if json_mode else response_text
                    return {"success": True, "data": data, "provider": fallback, "raw": response_text, "fallback_used": True}
                except LLMProviderError as fallback_error:
                    logger.error(
                        "Fallback LLM provider failed",
                        extra={"provider": fallback, "error_type": type(fallback_error).__name__, "status_code": fallback_error.status_code},
                    )
                    return {"success": False, "error": f"Primary failed: {primary_error} | Fallback {fallback} also failed: {fallback_error}", "provider": provider_name}
            return {"success": False, "error": str(primary_error), "provider": provider_name}

    async def generate_stream(
        self,
        system_prompt: str,
        user_prompt: str,
        provider: Optional[str] = None,
    ) -> AsyncGenerator[str, None]:
        """Stream response tokens with provider-specific degradation messages."""
        try:
            provider_name, llm = self._get_provider_entry(provider)
        except LLMProviderError as exc:
            logger.warning("LLM stream requested without a configured provider", extra={"error_type": type(exc).__name__})
            yield "[LLM stream unavailable: no provider configured]"
            return

        logger.debug("Starting LLM stream", extra={"provider": provider_name})
        async for token in llm.generate_stream(system_prompt, user_prompt):
            yield token


# Global LLM service
llm_service = LLMService()
