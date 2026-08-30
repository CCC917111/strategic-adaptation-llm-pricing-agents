"""Typed state passed into and returned by a pricing agent."""

from dataclasses import dataclass
from typing import Any


@dataclass(frozen=True, slots=True)
class OversightFeedback:
    status: str
    reasons: tuple[str, ...]
    proposed_price: float
    executed_price: float


@dataclass(frozen=True, slots=True)
class ObservedRound:
    round_index: int
    own_price: float
    rival_price: float
    own_quantity: float
    own_profit: float
    oversight: OversightFeedback | None = None


@dataclass(frozen=True, slots=True)
class RevisionRequest:
    proposed_price: float
    previous_justification: str
    reasons: tuple[str, ...]


@dataclass(frozen=True, slots=True)
class AgentTurn:
    round_index: int
    history: tuple[ObservedRound, ...] = ()
    revision: RevisionRequest | None = None


@dataclass(frozen=True, slots=True)
class PricingDecision:
    price: float
    justification: str
    used_competitor_info: bool
    notes: str
    api_metadata: dict[str, Any] | None = None


@dataclass(slots=True)
class AgentState:
    firm_id: int
    notes: str = ""
