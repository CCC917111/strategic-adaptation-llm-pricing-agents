"""Optional, provider-neutral transport for structured chat completions."""

from __future__ import annotations

import json
import math
import os
from datetime import datetime, timezone
from pathlib import Path
from typing import Any
from urllib.parse import urlsplit

from .models import PricingDecision


class OpenAICompatibleModelClient:
    """Use an explicitly configured HTTPS endpoint; never follow redirects.

    An optional local receipt records request/response JSON, not HTTP headers.
    Receipts include agent text and should not be published automatically.
    """

    def __init__(
        self,
        *,
        model: str,
        api_key: str | None = None,
        base_url: str | None = None,
        seed: int | None = None,
        reasoning_effort: str | None = None,
        temperature: float | None = None,
        timeout_seconds: float = 600.0,
        receipt_path: Path | None = None,
    ) -> None:
        try:
            import httpx
            from pydantic import BaseModel, ConfigDict, Field
        except ImportError as exc:
            raise RuntimeError(
                "Install compatible support with `python -m pip install -e '.[compatible]'`."
            ) from exc

        configured_key = (
            api_key or os.environ.get("GEMINI_OPENAI_COMPATIBLE_API_KEY", "")
        ).strip()
        configured_base_url = (
            base_url or os.environ.get("GEMINI_OPENAI_COMPATIBLE_BASE_URL", "")
        ).strip()
        if not configured_key:
            raise RuntimeError("GEMINI_OPENAI_COMPATIBLE_API_KEY is not set.")
        if not configured_base_url:
            raise RuntimeError("GEMINI_OPENAI_COMPATIBLE_BASE_URL is not set.")
        try:
            parsed_url = urlsplit(configured_base_url)
            valid_url = (
                parsed_url.scheme == "https"
                and bool(parsed_url.hostname)
                and parsed_url.username is None
                and parsed_url.password is None
                and not parsed_url.query
                and not parsed_url.fragment
                and "?" not in configured_base_url
                and "#" not in configured_base_url
                and not any(character.isspace() for character in configured_base_url)
            )
            parsed_url.port  # Validate a supplied port before making any request.
        except ValueError:
            valid_url = False
        if not valid_url:
            raise ValueError(
                "The API base URL must be HTTPS without credentials, query, or fragment."
            )
        if temperature is not None and (
            not math.isfinite(temperature) or temperature < 0
        ):
            raise ValueError("temperature must be finite and non-negative.")
        if timeout_seconds <= 0 or not math.isfinite(timeout_seconds):
            raise ValueError("timeout_seconds must be finite and positive.")

        # Keep the field order and schema identical to the historical PAPER
        # transport. Text limits are validated locally, not added to its schema.
        class PricingDecisionSchema(BaseModel):
            model_config = ConfigDict(extra="forbid")

            price: float = Field(ge=1.0, le=3.0)
            justification: str
            used_competitor_info: bool
            notes: str

        self._schema: type[BaseModel] = PricingDecisionSchema
        self._base_url = configured_base_url.rstrip("/")
        self._receipt_path = Path(receipt_path) if receipt_path is not None else None
        self._client = httpx.AsyncClient(
            headers={
                "Authorization": f"Bearer {configured_key}",
                "Content-Type": "application/json",
            },
            timeout=httpx.Timeout(timeout_seconds),
            follow_redirects=False,
        )
        self.model = model
        self.seed = seed
        self.reasoning_effort = reasoning_effort
        self.temperature = temperature

    def _record_receipt(
        self,
        *,
        payload: dict[str, Any],
        status: int | None,
        body: Any = None,
        failure: str | None = None,
    ) -> None:
        if self._receipt_path is None:
            return
        record: dict[str, Any] = {
            "recorded_at_utc": datetime.now(timezone.utc).isoformat(),
            "http_status": status,
            "request": payload,
        }
        if body is not None:
            record["response"] = body
        if failure is not None:
            record["failure"] = failure
        self._receipt_path.parent.mkdir(parents=True, exist_ok=True)
        with self._receipt_path.open("a", encoding="utf-8") as handle:
            handle.write(json.dumps(record, ensure_ascii=False) + "\n")

    async def generate(
        self, *, system_prompt: str, user_prompt: str
    ) -> PricingDecision:
        import httpx

        payload: dict[str, Any] = {
            "model": self.model,
            "messages": [
                {"role": "system", "content": system_prompt},
                {"role": "user", "content": user_prompt},
            ],
            "response_format": {
                "type": "json_schema",
                "json_schema": {
                    "name": "pricing_decision",
                    "strict": True,
                    "schema": self._schema.model_json_schema(),
                },
            },
        }
        for name, value in (
            ("seed", self.seed),
            ("reasoning_effort", self.reasoning_effort),
            ("temperature", self.temperature),
        ):
            if value is not None:
                payload[name] = value

        try:
            response = await self._client.post(
                f"{self._base_url}/chat/completions", json=payload
            )
        except httpx.RequestError as exc:
            self._record_receipt(
                payload=payload, status=None, failure=type(exc).__name__
            )
            raise RuntimeError(
                f"Chat-completions connection request failed ({type(exc).__name__})."
            ) from None
        if not response.is_success:
            self._record_receipt(
                payload=payload, status=response.status_code, failure="http_status"
            )
            category = "api_error" if response.status_code >= 500 else "request failed"
            raise RuntimeError(f"Chat-completions {category} (HTTP {response.status_code}).")
        try:
            body = response.json()
        except ValueError:
            self._record_receipt(
                payload=payload, status=response.status_code, failure="invalid_json"
            )
            raise RuntimeError("Chat completions returned invalid JSON.") from None
        self._record_receipt(payload=payload, status=response.status_code, body=body)
        if not isinstance(body, dict):
            raise RuntimeError("Response validation failed: invalid response object.")
        choices = body.get("choices")
        if not isinstance(choices, list) or not choices or not isinstance(choices[0], dict):
            raise RuntimeError("Response validation failed: no completion choices.")
        message = choices[0].get("message")
        if not isinstance(message, dict) or not message.get("content"):
            raise RuntimeError("Response validation failed: no pricing-decision text.")
        content = message["content"]
        if not isinstance(content, str):
            content = json.dumps(content, ensure_ascii=False)
        parsed = self._schema.model_validate_json(content)
        if not parsed.justification.strip():
            raise ValueError("Decision validation failed: justification cannot be empty.")
        if len(parsed.notes) > 2000:
            raise ValueError("Decision validation failed: notes exceed 2000 characters.")

        usage = body.get("usage") or {}
        if not isinstance(usage, dict):
            usage = {}
        completion_details = usage.get("completion_tokens_details") or {}
        if not isinstance(completion_details, dict):
            completion_details = {}
        return PricingDecision(
            price=parsed.price,
            justification=parsed.justification,
            used_competitor_info=parsed.used_competitor_info,
            notes=parsed.notes,
            api_metadata={
                "provider": "openai-compatible",
                "status": "completed",
                "transport": "openai_chat_completions",
                "base_url": self._base_url,
                "model_requested": self.model,
                "model_returned": body.get("model"),
                "request_id": body.get("id"),
                "reasoning_effort_requested": self.reasoning_effort,
                "temperature_requested": self.temperature,
                "seed_requested": self.seed,
                "usage": {
                    "input_tokens": usage.get("prompt_tokens"),
                    "output_tokens": usage.get("completion_tokens"),
                    "thought_tokens": completion_details.get("reasoning_tokens"),
                    "total_tokens": usage.get("total_tokens"),
                },
            },
        )

    async def close(self) -> None:
        await self._client.aclose()
