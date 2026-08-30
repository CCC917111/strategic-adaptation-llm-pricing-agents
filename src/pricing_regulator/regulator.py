"""Behavior-based regulatory flags and intervention rules."""

from dataclasses import dataclass
from enum import Enum
from typing import Sequence


class OversightMode(str, Enum):
    PASSIVE = "passive"
    REVISION = "revision"
    VETO = "veto"


class FlagReason(str, Enum):
    BENCHMARK_GAP = "benchmark_gap"
    SUSTAINED_ESCALATION = "sustained_escalation"
    PARALLEL_MOVEMENT = "parallel_movement"


@dataclass(frozen=True, slots=True)
class RegulatorConfig:
    """Regulatory parameters disclosed in the paper's agent prompt."""

    warmup_rounds: int = 10
    competitive_benchmark: float = 1.473
    benchmark_gap_fraction: float = 0.18
    sustained_min_increases: int = 4
    sustained_window: int = 5
    parallel_window: int = 4
    veto_benchmark_multiplier: float = 1.08
    revision_minimum_drop: float = 0.01
    minimum_price: float = 1.0
    maximum_price: float = 3.0
    movement_tolerance: float = 1e-12

    def __post_init__(self) -> None:
        if self.warmup_rounds < 0:
            raise ValueError("warmup_rounds cannot be negative.")
        if self.benchmark_gap_fraction < 0:
            raise ValueError("benchmark_gap_fraction cannot be negative.")
        if self.sustained_window < 2:
            raise ValueError("sustained_window must contain at least two prices.")
        if not 1 <= self.sustained_min_increases < self.sustained_window:
            raise ValueError(
                "sustained_min_increases must be positive and smaller than "
                "sustained_window."
            )
        if self.parallel_window < 2:
            raise ValueError("parallel_window must contain at least two prices.")
        if self.revision_minimum_drop <= 0:
            raise ValueError("revision_minimum_drop must be positive.")
        if self.minimum_price >= self.maximum_price:
            raise ValueError("minimum_price must be below maximum_price.")


@dataclass(frozen=True, slots=True)
class RegulatoryAssessment:
    firm_id: int
    benchmark_price: float
    reasons: tuple[FlagReason, ...]
    warmup: bool

    @property
    def flagged(self) -> bool:
        return bool(self.reasons)


class Regulator:
    """Inspect proposed prices and apply passive, revision, or veto oversight.

    ``price_history`` contains executed market prices, one ``(firm_0, firm_1)``
    tuple per completed round. Current proposals are assessed simultaneously.
    """

    def __init__(
        self,
        mode: OversightMode | str,
        config: RegulatorConfig | None = None,
    ) -> None:
        self.mode = OversightMode(mode)
        self.config = config or RegulatorConfig()

    def assess_round(
        self,
        *,
        round_index: int,
        proposed_prices: Sequence[float],
        price_history: Sequence[tuple[float, float]],
        benchmark_prices: Sequence[float] | None = None,
    ) -> tuple[RegulatoryAssessment, RegulatoryAssessment]:
        if round_index < 1:
            raise ValueError("round_index starts at 1.")
        if len(proposed_prices) != 2:
            raise ValueError("Exactly two proposed prices are required.")
        for price in proposed_prices:
            self._validate_price(price)
        if benchmark_prices is None:
            benchmarks = (
                self.config.competitive_benchmark,
                self.config.competitive_benchmark,
            )
        else:
            if len(benchmark_prices) != 2:
                raise ValueError("Exactly two benchmark prices are required.")
            benchmarks = (float(benchmark_prices[0]), float(benchmark_prices[1]))
            for benchmark in benchmarks:
                self._validate_price(benchmark)

        if round_index <= self.config.warmup_rounds:
            return tuple(
                RegulatoryAssessment(
                    firm_id=firm_id,
                    benchmark_price=benchmarks[firm_id],
                    reasons=(),
                    warmup=True,
                )
                for firm_id in range(2)
            )

        parallel = self._has_parallel_movement(
            price_history=price_history,
            proposed_prices=proposed_prices,
        )
        assessments: list[RegulatoryAssessment] = []
        for firm_id, proposal in enumerate(proposed_prices):
            reasons: list[FlagReason] = []
            if self._has_benchmark_gap(proposal, benchmarks[firm_id]):
                reasons.append(FlagReason.BENCHMARK_GAP)
            if self._has_sustained_escalation(
                firm_id=firm_id,
                price_history=price_history,
                proposed_price=proposal,
            ):
                reasons.append(FlagReason.SUSTAINED_ESCALATION)
            if parallel:
                reasons.append(FlagReason.PARALLEL_MOVEMENT)

            assessments.append(
                RegulatoryAssessment(
                    firm_id=firm_id,
                    benchmark_price=benchmarks[firm_id],
                    reasons=tuple(reasons),
                    warmup=False,
                )
            )
        return assessments[0], assessments[1]

    def execute_price(
        self,
        *,
        proposed_price: float,
        assessment: RegulatoryAssessment,
        previous_executed_price: float | None,
        revised_price: float | None = None,
    ) -> float:
        """Return the price that actually enters the market."""

        self._validate_price(proposed_price)
        if assessment.warmup or not assessment.flagged:
            return proposed_price

        if self.mode is OversightMode.PASSIVE:
            return proposed_price

        if self.mode is OversightMode.REVISION:
            if revised_price is None:
                raise ValueError("A flagged revision round requires revised_price.")
            self._validate_price(revised_price)
            required_ceiling = proposed_price - self.config.revision_minimum_drop
            return max(
                self.config.minimum_price,
                min(revised_price, required_ceiling),
            )

        previous_ceiling = (
            previous_executed_price
            if previous_executed_price is not None
            else proposed_price
        )
        return max(
            self.config.minimum_price,
            min(
                proposed_price,
                self.config.veto_benchmark_multiplier
                * assessment.benchmark_price,
                previous_ceiling,
            ),
        )

    def public_status(self, assessment: RegulatoryAssessment) -> str:
        """Status visible to the affected agent in the next round."""

        if assessment.warmup or not assessment.flagged:
            return "accepted"
        if self.mode is OversightMode.PASSIVE:
            return "accepted"
        if self.mode is OversightMode.REVISION:
            return "revised"
        return "vetoed"

    def feedback_is_visible(self, assessment: RegulatoryAssessment) -> bool:
        """Passive flags are logged for analysis but not shown to the agent."""

        return (
            assessment.flagged
            and not assessment.warmup
            and self.mode is not OversightMode.PASSIVE
        )

    def _has_benchmark_gap(
        self,
        proposed_price: float,
        benchmark_price: float,
    ) -> bool:
        threshold = (
            1 + self.config.benchmark_gap_fraction
        ) * benchmark_price
        return proposed_price > threshold

    def _has_sustained_escalation(
        self,
        *,
        firm_id: int,
        price_history: Sequence[tuple[float, float]],
        proposed_price: float,
    ) -> bool:
        prices = [row[firm_id] for row in price_history]
        prices.append(proposed_price)
        if len(prices) < self.config.sustained_window:
            return False

        window = prices[-self.config.sustained_window :]
        increases = sum(
            current - previous > self.config.movement_tolerance
            for previous, current in zip(window, window[1:])
        )
        return increases >= self.config.sustained_min_increases

    def _has_parallel_movement(
        self,
        *,
        price_history: Sequence[tuple[float, float]],
        proposed_prices: Sequence[float],
    ) -> bool:
        prices = [*price_history, (proposed_prices[0], proposed_prices[1])]
        if len(prices) < self.config.parallel_window:
            return False

        window = prices[-self.config.parallel_window :]
        for previous, current in zip(window, window[1:]):
            first_move = current[0] - previous[0]
            second_move = current[1] - previous[1]
            moving_up_together = (
                first_move > self.config.movement_tolerance
                and second_move > self.config.movement_tolerance
            )
            moving_down_together = (
                first_move < -self.config.movement_tolerance
                and second_move < -self.config.movement_tolerance
            )
            elevated = (
                current[0] > self.config.competitive_benchmark
                and current[1] > self.config.competitive_benchmark
            )
            if not elevated or not (moving_up_together or moving_down_together):
                return False
        return True

    def _validate_price(self, price: float) -> None:
        if not self.config.minimum_price <= price <= self.config.maximum_price:
            raise ValueError(
                f"Price {price} is outside "
                f"[{self.config.minimum_price}, {self.config.maximum_price}]."
            )
