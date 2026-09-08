"""OpenAI-compatible relay transport used by recorded Gemini 3.7 runs."""

from __future__ import annotations

import json
import os
from typing import Any

import httpx
from pydantic import BaseModel, ConfigDict, Field

from .models import PricingDecision


class OpenAICompatibleModelClient:
    """Return the same paper-order schema through a pinned HTTPS relay."""

    def __init__(
        self,
        *,
        model: str = "gemini-3.7-flash",
        seed: int | None = None,
        reasoning_effort: str = "high",
        api_key: str | None = None,
        base_url: str | None = None,
        timeout_seconds: float = 600.0,
    ) -> None:
        configured_key = (
            api_key or os.environ.get("GEMINI_OPENAI_COMPATIBLE_API_KEY", "")
        ).strip()
        configured_url = (
            base_url or os.environ.get("GEMINI_OPENAI_COMPATIBLE_BASE_URL", "")
        ).strip()
        if not configured_key or not configured_url:
            raise RuntimeError(
                "Set GEMINI_OPENAI_COMPATIBLE_API_KEY and "
                "GEMINI_OPENAI_COMPATIBLE_BASE_URL for relay transport."
            )
        if not configured_url.startswith("https://"):
            raise ValueError("The relay base URL must use HTTPS.")

        class DecisionSchema(BaseModel):
            model_config = ConfigDict(extra="forbid")

            price: float = Field(ge=1.0, le=3.0)
            justification: str
            used_competitor_info: bool
            notes: str

        self._schema: type[BaseModel] = DecisionSchema
        self._base_url = configured_url.rstrip("/")
        self._client = httpx.AsyncClient(
            headers={
                "Authorization": f"Bearer {configured_key}",
                "Content-Type": "application/json",
            },
            timeout=httpx.Timeout(timeout_seconds),
            follow_redirects=True,
        )
        self.model = model
        self.seed = seed
        self.reasoning_effort = reasoning_effort

    async def generate(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
    ) -> PricingDecision:
        payload: dict[str, Any] = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "reasoning_effort": self.reasoning_effort,
            "seed": self.seed,
            "response_format": {
                "type": "json_schema",
                "json_schema": {
                    "name": "pricing_decision",
                    "strict": True,
                    "schema": self._schema.model_json_schema(),
                },
            },
        }
        response = await self._client.post(
            f"{self._base_url}/chat/completions",
            json=payload,
        )
        response.raise_for_status()
        body = response.json()
        choices = body.get("choices", [])
        if not choices:
            raise RuntimeError("Relay returned no completion choices.")
        content = choices[0].get("message", {}).get("content")
        if not content:
            raise RuntimeError("Relay returned no pricing-decision text.")
        if not isinstance(content, str):
            content = json.dumps(content, ensure_ascii=False)

        parsed = self._schema.model_validate_json(content)
        usage = body.get("usage", {})
        details = usage.get("completion_tokens_details", {})
        return PricingDecision(
            price=parsed.price,
            justification=parsed.justification,
            used_competitor_info=parsed.used_competitor_info,
            notes=parsed.notes,
            api_metadata={
                "provider": "openai-compatible-relay",
                "transport": "chat-completions",
                "model_requested": self.model,
                "model_returned": body.get("model"),
                "request_id": body.get("id"),
                "reasoning_effort_requested": self.reasoning_effort,
                "temperature_requested": None,
                "seed_requested": self.seed,
                "usage": {
                    "input_tokens": usage.get("prompt_tokens"),
                    "output_tokens": usage.get("completion_tokens"),
                    "thought_tokens": details.get("reasoning_tokens"),
                    "total_tokens": usage.get("total_tokens"),
                },
            },
        )

    async def close(self) -> None:
        await self._client.aclose()
