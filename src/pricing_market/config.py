"""Configuration for the stationary reference market."""

from dataclasses import dataclass


@dataclass(frozen=True, slots=True)
class MarketConfig:
    number_of_firms: int = 2
    marginal_cost: float = 1.0
    minimum_price: float = 1.0
    maximum_price: float = 3.0
    market_size: float = 1.0
    quality: float = 2.0
    temperature: float = 0.25
    paper_nash_price: float = 1.473
    paper_monopoly_price: float = 1.802

    def __post_init__(self) -> None:
        if self.number_of_firms != 2:
            raise ValueError("The reference experiment requires exactly two firms.")
        if self.minimum_price >= self.maximum_price:
            raise ValueError("minimum_price must be below maximum_price.")
        if self.temperature <= 0:
            raise ValueError("temperature must be positive.")
        if self.market_size <= 0:
            raise ValueError("market_size must be positive.")
        if not self.minimum_price <= self.marginal_cost <= self.maximum_price:
            raise ValueError("marginal_cost must lie within the price range.")
