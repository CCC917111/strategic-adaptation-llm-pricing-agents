"""Configuration for the differentiated-products logit market."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class MarketConfig:
    """Parameters held fixed across all experimental treatments.

    ``quality`` and ``temperature`` are inferred from the two price benchmarks
    reported in the paper because the paper does not state them explicitly.
    The values 2.0 and 0.25 reproduce those benchmarks under the standard
    regular-logit demand model.
    """

    number_of_firms: int = 2
    marginal_cost: float = 1.0
    minimum_price: float = 1.0
    maximum_price: float = 3.0
    market_size: float = 1.0
    market_growth_rate: float = 0.0
    quality: float = 2.0
    temperature: float = 0.25

    paper_nash_price: float = 1.473
    paper_monopoly_price: float = 1.802

    def __post_init__(self) -> None:
        if self.number_of_firms != 2:
            raise ValueError("The reported experiment requires exactly two firms.")
        if self.minimum_price >= self.maximum_price:
            raise ValueError("minimum_price must be below maximum_price.")
        if self.temperature <= 0:
            raise ValueError("temperature must be positive.")
        if self.market_size <= 0:
            raise ValueError("market_size must be positive.")
        if self.market_growth_rate <= -1:
            raise ValueError("market_growth_rate must be greater than -1.")
        if not self.minimum_price <= self.marginal_cost <= self.maximum_price:
            raise ValueError("marginal_cost must lie within the allowed price range.")

    def market_size_at(self, round_index: int | None = None) -> float:
        """Return the exogenous potential-market size for a market round."""

        if round_index is None:
            return self.market_size
        if round_index < 1:
            raise ValueError("round_index must be positive.")
        return self.market_size * (1 + self.market_growth_rate) ** (
            round_index - 1
        )
