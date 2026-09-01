"""Gemini adapter used by the pricing-agent experiment.

The completed hidden-demand runs used ``GenerateContent`` with Gemini 3.5
Flash-Lite. The API method is explicit so a model-name heuristic cannot silently
change the experiment. API keys are read only from the process environment.
"""

from __future__ import annotations

import os
from typing import Any

from .models import PricingDecision
from .prompts import PromptTreatment, ResponseOrder


class GeminiModelClient:
    """Return schema-validated decisions through the Google Gen AI SDK."""

    def __init__(
        self,
        *,
        model: str | None = None,
        seed: int | None = None,
        thinking_level: str | None = None,
        temperature: float | None = None,
        response_order: ResponseOrder = ResponseOrder.PAPER,
        prompt_treatment: PromptTreatment = PromptTreatment.PAPER,
        api_method: str = "generate_content",
        store: bool = False,
    ) -> None:
        try:
            from google import genai
            from pydantic import BaseModel, Field
        except ImportError as exc:
            raise RuntimeError(
                "Install Gemini support with `python -m pip install -e '.[gemini]'`."
            ) from exc

        api_key = os.environ.get("GEMINI_API_KEY", "").strip()
        if not api_key:
            raise RuntimeError("GEMINI_API_KEY is not set.")

        price_field = Field(ge=1.0, le=3.0)
        justification_field = Field(description="Public justification, one or two sentences.")
        disclosure_field = Field(
            description="Whether the rival's prices materially influenced the decision."
        )
        notes_field = Field(description="Updated private scratchpad for future rounds.")
        neutral = prompt_treatment is PromptTreatment.NO_OVERSIGHT_NO_COLLUSION

        if response_order is ResponseOrder.PRICE_LAST and neutral:
            class DecisionSchema(BaseModel):
                justification: str = justification_field
                notes: str = notes_field
                price: float = price_field
        elif response_order is ResponseOrder.PRICE_LAST:
            class DecisionSchema(BaseModel):
                justification: str = justification_field
                used_competitor_info: bool = disclosure_field
                notes: str = notes_field
                price: float = price_field
        elif neutral:
            class DecisionSchema(BaseModel):
                price: float = price_field
                justification: str = justification_field
                notes: str = notes_field
        else:
            class DecisionSchema(BaseModel):
                price: float = price_field
                justification: str = justification_field
                used_competitor_info: bool = disclosure_field
                notes: str = notes_field

        self._client = genai.Client(api_key=api_key)
        self._schema = DecisionSchema
        self.model = model or os.environ.get(
            "GEMINI_MODEL", "gemini-3.5-flash-lite"
        )
        self.seed = seed
        self.thinking_level = thinking_level
        self.temperature = temperature
        if api_method not in {"generate_content", "interactions", "auto"}:
            raise ValueError(
                "api_method must be generate_content, interactions, or auto."
            )
        self.api_method = api_method
        self.store = store

    async def generate(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
    ) -> PricingDecision:
        method = self.api_method
        if method == "auto":
            method = (
                "generate_content"
                if self.model.startswith(("gemini-2.5", "gemini-3.5", "gemini-3.7"))
                else "interactions"
            )
        if method == "generate_content":
            return await self._generate_content(system_prompt, user_prompt)
        return await self._generate_interaction(system_prompt, user_prompt)

    async def _generate_content(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> PricingDecision:
        config: dict[str, Any] = {
            "system_instruction": system_prompt,
            "seed": self.seed,
            "response_mime_type": "application/json",
            "response_schema": self._schema,
        }
        if self.thinking_level is not None:
            config["thinking_config"] = {"thinking_level": self.thinking_level}
        if self.temperature is not None:
            config["temperature"] = self.temperature

        response = await self._client.aio.models.generate_content(
            model=self.model,
            contents=user_prompt,
            config=config,
        )
        if not response.text:
            raise RuntimeError("Gemini returned no pricing-decision text.")
        parsed = self._schema.model_validate_json(response.text)
        usage = response.usage_metadata
        return self._decision(
            parsed,
            {
                "provider": "gemini",
                "model_requested": self.model,
                "model_returned": str(response.model_version or self.model),
                "api_method": "generate_content",
                "store": False,
                "thinking_level_requested": self.thinking_level,
                "temperature_requested": self.temperature,
                "usage": {
                    "input_tokens": getattr(usage, "prompt_token_count", None),
                    "output_tokens": getattr(usage, "candidates_token_count", None),
                    "thought_tokens": getattr(usage, "thoughts_token_count", None),
                    "total_tokens": getattr(usage, "total_token_count", None),
                },
            },
        )

    async def _generate_interaction(
        self,
        system_prompt: str,
        user_prompt: str,
    ) -> PricingDecision:
        generation_config: dict[str, Any] = {}
        if self.seed is not None:
            generation_config["seed"] = self.seed
        if self.thinking_level is not None:
            generation_config["thinking_level"] = self.thinking_level
        if self.temperature is not None:
            generation_config["temperature"] = self.temperature

        interaction = await self._client.aio.interactions.create(
            model=self.model,
            input=user_prompt,
            system_instruction=system_prompt,
            generation_config=generation_config or None,
            response_format={
                "type": "text",
                "mime_type": "application/json",
                "schema": self._schema.model_json_schema(),
            },
            store=self.store,
        )
        if not interaction.output_text:
            raise RuntimeError("Gemini returned no pricing-decision text.")
        parsed = self._schema.model_validate_json(interaction.output_text)
        usage = interaction.usage
        return self._decision(
            parsed,
            {
                "provider": "gemini",
                "model_requested": self.model,
                "model_returned": str(interaction.model),
                "api_method": "interactions",
                "interaction_id": interaction.id if self.store else None,
                "store": self.store,
                "thinking_level_requested": self.thinking_level,
                "temperature_requested": self.temperature,
                "usage": {
                    "input_tokens": getattr(usage, "total_input_tokens", None),
                    "output_tokens": getattr(usage, "total_output_tokens", None),
                    "thought_tokens": getattr(usage, "total_thought_tokens", None),
                    "total_tokens": getattr(usage, "total_tokens", None),
                },
            },
        )

    @staticmethod
    def _decision(parsed: Any, metadata: dict[str, Any]) -> PricingDecision:
        return PricingDecision(
            price=parsed.price,
            justification=parsed.justification,
            used_competitor_info=getattr(parsed, "used_competitor_info", False),
            notes=parsed.notes,
            api_metadata=metadata,
        )

    async def close(self) -> None:
        await self._client.aio.aclose()
