"""Execute simultaneous pricing rounds through regulation and the market."""

import asyncio
from dataclasses import dataclass
from collections.abc import Sequence

from pricing_agents import (
    AgentTurn,
    ObservedRound,
    OversightFeedback,
    PricingAgent,
    PricingDecision,
    RevisionRequest,
)
from pricing_market import LogitMarket, MarketOutcome
from pricing_regulator import (
    OversightMode,
    RegulatoryAssessment,
    Regulator,
)


@dataclass(frozen=True, slots=True)
class ExperimentRound:
    round_index: int
    proposals: tuple[PricingDecision, PricingDecision]
    revisions: tuple[PricingDecision | None, PricingDecision | None]
    assessments: tuple[RegulatoryAssessment, RegulatoryAssessment]
    executed_prices: tuple[float, float]
    market_outcome: MarketOutcome


class GameRunner:
    """Own experiment state and execute complete market rounds."""

    def __init__(
        self,
        *,
        agents: tuple[PricingAgent, PricingAgent],
        market: LogitMarket,
        regulator: Regulator,
        use_round_best_response_benchmark: bool = False,
    ) -> None:
        if agents[0].state.firm_id != 0 or agents[1].state.firm_id != 1:
            raise ValueError("agents must be ordered as firm 0, firm 1.")
        self.agents = agents
        self.market = market
        self.regulator = regulator
        self.use_round_best_response_benchmark = use_round_best_response_benchmark
        self.rounds: list[ExperimentRound] = []
        self._agent_histories: tuple[list[ObservedRound], list[ObservedRound]] = (
            [],
            [],
        )

    async def run_round(self) -> ExperimentRound:
        """Run both proposals, regulation, execution, and market settlement."""

        round_index = len(self.rounds) + 1
        base_turns = tuple(
            AgentTurn(
                round_index=round_index,
                history=tuple(self._agent_histories[firm_id]),
            )
            for firm_id in range(2)
        )
        proposal_list = await asyncio.gather(
            *(
                self.agents[firm_id].decide(base_turns[firm_id])
                for firm_id in range(2)
            )
        )
        proposals = proposal_list[0], proposal_list[1]
        proposed_prices = proposals[0].price, proposals[1].price
        benchmark_prices = None
        if self.use_round_best_response_benchmark:
            benchmark_prices = (
                self.market.best_response(
                    proposed_prices[1], round_index=round_index
                ),
                self.market.best_response(
                    proposed_prices[0], round_index=round_index
                ),
            )

        assessments = self.regulator.assess_round(
            round_index=round_index,
            proposed_prices=proposed_prices,
            price_history=[row.executed_prices for row in self.rounds],
            benchmark_prices=benchmark_prices,
        )
        revisions = await self._request_revisions(
            base_turns=base_turns,
            proposals=proposals,
            assessments=assessments,
        )

        previous_prices = self.rounds[-1].executed_prices if self.rounds else None
        executed_prices = tuple(
            self.regulator.execute_price(
                proposed_price=proposals[firm_id].price,
                assessment=assessments[firm_id],
                previous_executed_price=(
                    previous_prices[firm_id] if previous_prices else None
                ),
                revised_price=(
                    revisions[firm_id].price
                    if revisions[firm_id] is not None
                    else None
                ),
            )
            for firm_id in range(2)
        )
        market_outcome = self.market.evaluate(
            executed_prices,
            round_index=round_index,
        )

        result = ExperimentRound(
            round_index=round_index,
            proposals=proposals,
            revisions=revisions,
            assessments=assessments,
            executed_prices=(executed_prices[0], executed_prices[1]),
            market_outcome=market_outcome,
        )
        self.rounds.append(result)
        self._append_agent_histories(result)
        return result

    async def run(self, rounds: int) -> tuple[ExperimentRound, ...]:
        if rounds < 1:
            raise ValueError("rounds must be positive.")
        for _ in range(rounds):
            await self.run_round()
        return tuple(self.rounds)

    def restore(self, rounds: Sequence[ExperimentRound]) -> None:
        """Restore completed rounds and agent memory from persisted records."""

        if self.rounds or any(self._agent_histories):
            raise RuntimeError("Can only restore into a fresh GameRunner.")
        for expected_index, result in enumerate(rounds, start=1):
            if result.round_index != expected_index:
                raise ValueError(
                    "Persisted rounds must be contiguous and start at round 1."
                )
            self.rounds.append(result)
            self._append_agent_histories(result)

        if rounds:
            last = rounds[-1]
            for firm_id, agent in enumerate(self.agents):
                final_decision = (
                    last.revisions[firm_id]
                    if last.revisions[firm_id] is not None
                    else last.proposals[firm_id]
                )
                agent.state.notes = final_decision.notes

    async def _request_revisions(
        self,
        *,
        base_turns: tuple[AgentTurn, AgentTurn],
        proposals: tuple[PricingDecision, PricingDecision],
        assessments: tuple[RegulatoryAssessment, RegulatoryAssessment],
    ) -> tuple[PricingDecision | None, PricingDecision | None]:
        revisions: list[PricingDecision | None] = [None, None]
        if self.regulator.mode is not OversightMode.REVISION:
            return revisions[0], revisions[1]

        pending: list[tuple[int, object]] = []
        for firm_id, assessment in enumerate(assessments):
            if not assessment.flagged or assessment.warmup:
                continue
            revision_turn = AgentTurn(
                round_index=base_turns[firm_id].round_index,
                history=base_turns[firm_id].history,
                revision=RevisionRequest(
                    proposed_price=proposals[firm_id].price,
                    previous_justification=proposals[firm_id].justification,
                    reasons=tuple(reason.value for reason in assessment.reasons),
                ),
            )
            pending.append(
                (firm_id, self.agents[firm_id].decide(revision_turn))
            )

        if pending:
            outputs = await asyncio.gather(*(coroutine for _, coroutine in pending))
            for (firm_id, _), output in zip(pending, outputs, strict=True):
                revisions[firm_id] = output
        return revisions[0], revisions[1]

    def _append_agent_histories(self, result: ExperimentRound) -> None:
        for firm_id in range(2):
            assessment = result.assessments[firm_id]
            feedback = None
            if self.regulator.feedback_is_visible(assessment):
                feedback = OversightFeedback(
                    status=self.regulator.public_status(assessment),
                    reasons=tuple(reason.value for reason in assessment.reasons),
                    proposed_price=result.proposals[firm_id].price,
                    executed_price=result.executed_prices[firm_id],
                )

            firm_outcome = result.market_outcome.firms[firm_id]
            self._agent_histories[firm_id].append(
                ObservedRound(
                    round_index=result.round_index,
                    own_price=result.executed_prices[firm_id],
                    rival_price=result.executed_prices[1 - firm_id],
                    own_quantity=firm_outcome.quantity,
                    own_profit=firm_outcome.profit,
                    oversight=feedback,
                )
            )
