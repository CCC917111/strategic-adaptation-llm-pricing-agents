"""Retry utilities for transient model-provider failures."""

import asyncio
import random
from collections.abc import Callable

from .clients import ModelClient
from .models import PricingDecision


class RetryingModelClient:
    """Retry provider errors with bounded exponential backoff."""

    def __init__(
        self,
        client: ModelClient,
        *,
        max_attempts: int = 5,
        base_delay_seconds: float = 2.0,
        maximum_delay_seconds: float = 60.0,
        attempt_timeout_seconds: float | None = 120.0,
        jitter_seed: int = 0,
        on_retry: Callable[[int, float, Exception], None] | None = None,
    ) -> None:
        if max_attempts < 1:
            raise ValueError("max_attempts must be positive.")
        if base_delay_seconds < 0 or maximum_delay_seconds < 0:
            raise ValueError("Retry delays cannot be negative.")
        if attempt_timeout_seconds is not None and attempt_timeout_seconds <= 0:
            raise ValueError("Attempt timeout must be positive or None.")
        self.client = client
        self.max_attempts = max_attempts
        self.base_delay_seconds = base_delay_seconds
        self.maximum_delay_seconds = maximum_delay_seconds
        self.attempt_timeout_seconds = attempt_timeout_seconds
        self._random = random.Random(jitter_seed)
        self.on_retry = on_retry

    async def generate(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
    ) -> PricingDecision:
        for attempt in range(1, self.max_attempts + 1):
            try:
                return await asyncio.wait_for(
                    self.client.generate(
                        system_prompt=system_prompt,
                        user_prompt=user_prompt,
                    ),
                    timeout=self.attempt_timeout_seconds,
                )
            except Exception as exc:
                if attempt >= self.max_attempts or not self._is_retryable(exc):
                    raise
                exponential = self.base_delay_seconds * (2 ** (attempt - 1))
                delay = min(self.maximum_delay_seconds, exponential)
                delay += self._random.uniform(0, min(1.0, delay * 0.1))
                if self.on_retry is not None:
                    self.on_retry(attempt, delay, exc)
                await asyncio.sleep(delay)
        raise AssertionError("Retry loop exited without returning or raising.")

    @staticmethod
    def _is_retryable(exc: Exception) -> bool:
        text = f"{type(exc).__name__}: {exc}".lower()
        retry_markers = (
            "429",
            "resource_exhausted",
            "rate limit",
            "timeout",
            "timed out",
            "connection",
            "disconnected",
            "remoteprotocolerror",
            "temporarily unavailable",
            "internalservererror",
            "503",
            "504",
            "500",
            "internal server",
            "high demand",
            "api_error",
            "json",
            "validation",
        )
        return any(marker in text for marker in retry_markers)
