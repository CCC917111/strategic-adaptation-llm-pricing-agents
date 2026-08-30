"""Stateful pricing agent built on a provider-independent model client."""

from collections.abc import Callable

from .clients import ModelClient
from .models import AgentState, AgentTurn, PricingDecision
from .prompts import PromptFactory


class PricingAgent:
    """One firm's agent and its private persistent notes."""

    def __init__(
        self,
        *,
        firm_id: int,
        client: ModelClient,
        prompts: PromptFactory | None = None,
    ) -> None:
        if firm_id not in (0, 1):
            raise ValueError("firm_id must be 0 or 1.")
        self.state = AgentState(firm_id=firm_id)
        self.client = client
        self.prompts = prompts or PromptFactory()

    async def decide(self, turn: AgentTurn) -> PricingDecision:
        decision = await self.client.generate(
            system_prompt=self.prompts.system_prompt(),
            user_prompt=self.prompts.user_prompt(self.state, turn),
        )
        self._validate(decision)
        self.state.notes = decision.notes
        return decision

    def _validate(self, decision: PricingDecision) -> None:
        c = self.prompts.config
        if not c.minimum_price <= decision.price <= c.maximum_price:
            raise ValueError(
                f"Agent {self.state.firm_id} proposed out-of-range price "
                f"{decision.price}."
            )
        if not decision.justification.strip():
            raise ValueError("Agent justification cannot be empty.")
        if len(decision.notes) > c.max_notes_chars:
            raise ValueError(
                f"Agent notes exceed {c.max_notes_chars} characters."
            )


def create_agent_pair(
    client_factory: Callable[[int], ModelClient],
    *,
    prompts: PromptFactory | None = None,
) -> tuple[PricingAgent, PricingAgent]:
    """Create two agents with independent clients and private note state."""

    prompt_factory = prompts or PromptFactory()
    return (
        PricingAgent(
            firm_id=0,
            client=client_factory(0),
            prompts=prompt_factory,
        ),
        PricingAgent(
            firm_id=1,
            client=client_factory(1),
            prompts=prompt_factory,
        ),
    )

