"""Official Google Gen AI transport for the Gemini 3.7 reference run."""

from __future__ import annotations

import os
from typing import Any

from .models import PricingDecision


class GeminiModelClient:
    """Return paper-order, schema-validated decisions via GenerateContent."""

    def __init__(
        self,
        *,
        model: str = "gemini-3.7-flash",
        seed: int | None = None,
        thinking_level: str = "high",
        api_key: str | None = None,
    ) -> None:
        try:
            from google import genai
            from pydantic import BaseModel, ConfigDict, Field
        except ImportError as exc:
            raise RuntimeError(
                "Install Gemini support with `python -m pip install -e '.[gemini]'`."
            ) from exc

        configured_key = (api_key or os.environ.get("GEMINI_API_KEY", "")).strip()
        if not configured_key:
            raise RuntimeError("GEMINI_API_KEY is not set.")
        if thinking_level not in {"low", "medium", "high"}:
            raise ValueError("thinking_level must be low, medium, or high.")

        class DecisionSchema(BaseModel):
            model_config = ConfigDict(extra="forbid")

            price: float = Field(ge=1.0, le=3.0)
            justification: str
            used_competitor_info: bool
            notes: str

        self._client = genai.Client(api_key=configured_key)
        self._schema: type[BaseModel] = DecisionSchema
        self.model = model
        self.seed = seed
        self.thinking_level = thinking_level

    async def generate(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
    ) -> PricingDecision:
        config: dict[str, Any] = {
            "system_instruction": system_prompt,
            "seed": self.seed,
            "thinking_config": {"thinking_level": self.thinking_level},
            "response_mime_type": "application/json",
            "response_schema": self._schema,
        }
        response = await self._client.aio.models.generate_content(
            model=self.model,
            contents=user_prompt,
            config=config,
        )
        if not response.text:
            raise RuntimeError("Gemini returned no pricing-decision text.")

        parsed = self._schema.model_validate_json(response.text)
        usage = response.usage_metadata
        return PricingDecision(
            price=parsed.price,
            justification=parsed.justification,
            used_competitor_info=parsed.used_competitor_info,
            notes=parsed.notes,
            api_metadata={
                "provider": "google",
                "transport": "google-genai-generate-content",
                "model_requested": self.model,
                "model_returned": str(response.model_version or self.model),
                "response_id": response.response_id,
                "thinking_level_requested": self.thinking_level,
                "temperature_requested": None,
                "seed_requested": self.seed,
                "usage": {
                    "input_tokens": getattr(usage, "prompt_token_count", None),
                    "output_tokens": getattr(usage, "candidates_token_count", None),
                    "thought_tokens": getattr(usage, "thoughts_token_count", None),
                    "total_tokens": getattr(usage, "total_token_count", None),
                },
            },
        )

    async def close(self) -> None:
        await self._client.aio.aclose()
