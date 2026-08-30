"""Provider-independent model client interfaces and deterministic test clients."""

from collections import deque
from typing import Protocol

from .models import PricingDecision


class ModelClient(Protocol):
    async def generate(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
    ) -> PricingDecision:
        """Generate one structured pricing decision."""


class ScriptedModelClient:
    """Return predefined outputs without network calls or API charges."""

    def __init__(self, decisions: list[PricingDecision]) -> None:
        if not decisions:
            raise ValueError("At least one scripted decision is required.")
        self._decisions = deque(decisions)
        self.calls: list[tuple[str, str]] = []

    async def generate(
        self,
        *,
        system_prompt: str,
        user_prompt: str,
    ) -> PricingDecision:
        self.calls.append((system_prompt, user_prompt))
        if not self._decisions:
            raise RuntimeError("ScriptedModelClient has no decisions remaining.")
        return self._decisions.popleft()

