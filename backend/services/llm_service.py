"""
Access Navigator AI - Multi-Provider LLM Service
================================================
Supports Groq, Gemini, and OpenAI with streaming,
automatic fallback, and structured JSON output.
"""
import os
import json
import asyncio
from typing import AsyncGenerator, Optional, Dict, Any, List
from core.config import settings


class LLMProvider:
    """Abstract LLM provider interface."""

    async def generate(self, system_prompt: str, user_prompt: str, json_mode: bool = True) -> str:
        raise NotImplementedError

    async def generate_stream(self, system_prompt: str, user_prompt: str) -> AsyncGenerator[str, None]:
        raise NotImplementedError


class GroqProvider(LLMProvider):
    """Groq LLM provider with ultra-fast inference."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.model = settings.GROQ_MODEL
        self.fallback_model = settings.GROQ_FALLBACK_MODEL
        self.base_url = "https://api.groq.com/openai/v1"

    async def generate(self, system_prompt: str, user_prompt: str, json_mode: bool = True) -> str:
        import aiohttp

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
        }

        if json_mode:
            payload["response_format"] = {"type": "json_object"}

        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(f"{self.base_url}/chat/completions", headers=headers, json=payload) as resp:
                    if resp.status != 200:
                        error_text = await resp.text()
                        print(f"Groq primary model error: {error_text}")
                        # Fallback model
                        payload["model"] = self.fallback_model
                        async with session.post(f"{self.base_url}/chat/completions", headers=headers, json=payload) as resp2:
                            if resp2.status != 200:
                                raise Exception(f"Groq fallback also failed: {await resp2.text()}")
                            data = await resp2.json()
                            return data["choices"][0]["message"]["content"]
                    data = await resp.json()
                    return data["choices"][0]["message"]["content"]
            except Exception as e:
                print(f"Groq error: {e}")
                raise

    async def generate_stream(self, system_prompt: str, user_prompt: str) -> AsyncGenerator[str, None]:
        import aiohttp

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

        async with aiohttp.ClientSession() as session:
            try:
                async with session.post(f"{self.base_url}/chat/completions", headers=headers, json=payload) as resp:
                    async for line in resp.content:
                        line = line.decode("utf-8").strip()
                        if line.startswith("data: ") and line != "data: [DONE]":
                            try:
                                chunk = json.loads(line[6:])
                                delta = chunk["choices"][0]["delta"].get("content", "")
                                if delta:
                                    yield delta
                            except:
                                continue
            except Exception as e:
                print(f"Groq streaming error: {e}")
                yield f"[Error: {str(e)}]"


class GeminiProvider(LLMProvider):
    """Google Gemini provider."""

    def __init__(self, api_key: str):
        self.api_key = api_key
        self.model = settings.GEMINI_MODEL

    async def generate(self, system_prompt: str, user_prompt: str, json_mode: bool = True) -> str:
        import aiohttp

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

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as resp:
                if resp.status != 200:
                    error_text = await resp.text()
                    raise Exception(f"Gemini error: {error_text}")
                data = await resp.json()
                return data["candidates"][0]["content"]["parts"][0]["text"]

    async def generate_stream(self, system_prompt: str, user_prompt: str) -> AsyncGenerator[str, None]:
        import aiohttp

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

        async with aiohttp.ClientSession() as session:
            async with session.post(url, headers=headers, json=payload) as resp:
                async for line in resp.content:
                    line = line.decode("utf-8").strip()
                    if line.startswith("data: ") and line != "data: [DONE]":
                        try:
                            chunk = json.loads(line[6:])
                            text = chunk["candidates"][0]["content"]["parts"][0].get("text", "")
                            if text:
                                yield text
                        except:
                            continue


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

    def _get_provider(self, preferred: Optional[str] = None) -> LLMProvider:
        if preferred and preferred in self.providers:
            return self.providers[preferred]
        if settings.PRIMARY_LLM in self.providers:
            return self.providers[settings.PRIMARY_LLM]
        if self.providers:
            return list(self.providers.values())[0]
        raise Exception("No LLM provider configured. Set GROQ_API_KEY or GEMINI_API_KEY.")

    async def generate(
        self,
        system_prompt: str,
        user_prompt: str,
        json_mode: bool = True,
        provider: Optional[str] = None,
    ) -> Dict[str, Any]:
        """Generate structured response with automatic fallback."""
        llm = self._get_provider(provider)
        provider_name = provider or settings.PRIMARY_LLM

        try:
            response_text = await llm.generate(system_prompt, user_prompt, json_mode)

            if json_mode:
                try:
                    parsed = json.loads(response_text)
                    return {"success": True, "data": parsed, "provider": provider_name, "raw": response_text}
                except json.JSONDecodeError:
                    # Try to extract JSON from text
                    try:
                        start = response_text.index("{")
                        end = response_text.rindex("}") + 1
                        parsed = json.loads(response_text[start:end])
                        return {"success": True, "data": parsed, "provider": provider_name, "raw": response_text}
                    except:
                        return {"success": False, "data": None, "provider": provider_name, "raw": response_text, "error": "JSON parse failed"}
            else:
                return {"success": True, "data": response_text, "provider": provider_name}

        except Exception as e:
            # Try fallback provider
            fallback = settings.FALLBACK_LLM
            if fallback != provider_name and fallback in self.providers:
                try:
                    fallback_llm = self.providers[fallback]
                    response_text = await fallback_llm.generate(system_prompt, user_prompt, json_mode)
                    if json_mode:
                        parsed = json.loads(response_text)
                        return {"success": True, "data": parsed, "provider": fallback, "raw": response_text, "fallback_used": True}
                    return {"success": True, "data": response_text, "provider": fallback, "fallback_used": True}
                except:
                    pass
            return {"success": False, "error": str(e), "provider": provider_name}

    async def generate_stream(
        self,
        system_prompt: str,
        user_prompt: str,
        provider: Optional[str] = None,
    ) -> AsyncGenerator[str, None]:
        """Stream response tokens."""
        llm = self._get_provider(provider)
        async for token in llm.generate_stream(system_prompt, user_prompt):
            yield token


# Global LLM service
llm_service = LLMService()
