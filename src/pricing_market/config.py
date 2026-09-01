"""Configuration for the differentiated-products logit market."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class MarketConfig:
    """Economic parameters and the hidden common demand-shift schedule."""

    number_of_firms: int = 2
    marginal_cost: float = 1.0
    minimum_price: float = 1.0
    maximum_price: float = 3.0
    market_size: float = 1.0
    market_growth_rate: float = 0.0
    quality: float = 2.0
    temperature: float = 0.25
    demand_shift_max: float = 0.0
    demand_shift_ramp_end_round: int = 40

    paper_nash_price: float = 1.473
    paper_monopoly_price: float = 1.802

    def __post_init__(self) -> None:
        if self.number_of_firms != 2:
            raise ValueError("This experiment requires exactly two firms.")
        if self.minimum_price >= self.maximum_price:
            raise ValueError("minimum_price must be below maximum_price.")
        if self.temperature <= 0:
            raise ValueError("temperature must be positive.")
        if self.market_size <= 0:
            raise ValueError("market_size must be positive.")
        if self.market_growth_rate <= -1:
            raise ValueError("market_growth_rate must be greater than -1.")
        if self.demand_shift_ramp_end_round < 2:
            raise ValueError("demand_shift_ramp_end_round must be at least 2.")
        if not self.minimum_price <= self.marginal_cost <= self.maximum_price:
            raise ValueError("marginal_cost must lie within the price range.")

    def market_size_at(self, round_index: int | None = None) -> float:
        """Return potential-market size for a round."""

        if round_index is None:
            return self.market_size
        self._validate_round(round_index)
        return self.market_size * (1 + self.market_growth_rate) ** (round_index - 1)

    def demand_shift_at(self, round_index: int | None = None) -> float:
        """Return the common hidden utility shift for a round.

        Round 1 has no shift. The shift rises linearly and reaches its maximum
        at ``demand_shift_ramp_end_round``.
        """

        if round_index is None:
            round_index = 1
        self._validate_round(round_index)
        progress = min(
            (round_index - 1) / (self.demand_shift_ramp_end_round - 1),
            1.0,
        )
        return self.demand_shift_max * progress

    @staticmethod
    def _validate_round(round_index: int) -> None:
        if round_index < 1:
            raise ValueError("round_index must be positive.")
