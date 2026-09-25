"""Regular-logit demand for the stationary reference market."""

from dataclasses import dataclass
from math import exp
from typing import Callable, Sequence

from .config import MarketConfig


@dataclass(frozen=True, slots=True)
class FirmOutcome:
    price: float
    share: float
    quantity: float
    profit: float


@dataclass(frozen=True, slots=True)
class MarketOutcome:
    firms: tuple[FirmOutcome, ...]
    outside_share: float
    market_size: float = 1.0


class LogitMarket:
    """A differentiated-products Bertrand market with an outside option."""

    def __init__(self, config: MarketConfig | None = None) -> None:
        self.config = config or MarketConfig()

    def evaluate(
        self,
        prices: Sequence[float],
        *,
        round_index: int | None = None,
    ) -> MarketOutcome:
        if len(prices) != self.config.number_of_firms:
            raise ValueError(f"Expected two prices, got {len(prices)}.")
        for price in prices:
            self._validate_price(price)

        utilities = [
            (self.config.quality - price) / self.config.temperature
            for price in prices
        ]
        normalization = max(0.0, *utilities)
        product_weights = [exp(value - normalization) for value in utilities]
        outside_weight = exp(-normalization)
        denominator = outside_weight + sum(product_weights)
        shares = [weight / denominator for weight in product_weights]
        market_size = self.market_size_at(round_index)
        firms = tuple(
            FirmOutcome(
                price=price,
                share=share,
                quantity=market_size * share,
                profit=(price - self.config.marginal_cost) * market_size * share,
            )
            for price, share in zip(prices, shares, strict=True)
        )
        return MarketOutcome(
            firms=firms,
            outside_share=outside_weight / denominator,
            market_size=market_size,
        )

    def market_size_at(self, round_index: int | None = None) -> float:
        """Stationary size; dynamic markets override this settlement input."""
        return self.config.market_size

    def best_response(
        self,
        rival_price: float,
        *,
        round_index: int | None = None,
        tolerance: float = 1e-10,
    ) -> float:
        self._validate_price(rival_price)

        def objective(own_price: float) -> float:
            return self.evaluate(
                (own_price, rival_price), round_index=round_index
            ).firms[0].profit

        return self._golden_section_maximize(objective, tolerance=tolerance)

    def symmetric_nash_price(
        self,
        *,
        round_index: int | None = None,
        tolerance: float = 1e-9,
    ) -> float:
        lower = self.config.minimum_price
        upper = self.config.maximum_price

        def fixed_point_error(price: float) -> float:
            return self.best_response(price, round_index=round_index) - price

        if fixed_point_error(lower) * fixed_point_error(upper) > 0:
            raise RuntimeError("Could not bracket a symmetric Nash equilibrium.")
        while upper - lower > tolerance:
            midpoint = (lower + upper) / 2
            if fixed_point_error(midpoint) > 0:
                lower = midpoint
            else:
                upper = midpoint
        return (lower + upper) / 2

    def symmetric_joint_profit_price(
        self,
        *,
        round_index: int | None = None,
        tolerance: float = 1e-10,
    ) -> float:
        def objective(price: float) -> float:
            outcome = self.evaluate((price, price), round_index=round_index)
            return sum(firm.profit for firm in outcome.firms)

        return self._golden_section_maximize(objective, tolerance=tolerance)

    def standalone_monopoly_price(
        self,
        *,
        round_index: int | None = None,
        tolerance: float = 1e-10,
    ) -> float:
        del round_index
        market_size = self.config.market_size

        def objective(price: float) -> float:
            utility = (
                self.config.quality - price
            ) / self.config.temperature
            normalization = max(0.0, utility)
            product_weight = exp(utility - normalization)
            outside_weight = exp(-normalization)
            share = product_weight / (outside_weight + product_weight)
            return (price - self.config.marginal_cost) * market_size * share

        return self._golden_section_maximize(objective, tolerance=tolerance)

    def _golden_section_maximize(
        self,
        objective: Callable[[float], float],
        *,
        tolerance: float,
    ) -> float:
        lower = self.config.minimum_price
        upper = self.config.maximum_price
        ratio = (5**0.5 - 1) / 2
        left = upper - ratio * (upper - lower)
        right = lower + ratio * (upper - lower)
        left_value = objective(left)
        right_value = objective(right)
        while upper - lower > tolerance:
            if left_value < right_value:
                lower = left
                left = right
                left_value = right_value
                right = lower + ratio * (upper - lower)
                right_value = objective(right)
            else:
                upper = right
                right = left
                right_value = left_value
                left = upper - ratio * (upper - lower)
                left_value = objective(left)
        return (lower + upper) / 2

    def _validate_price(self, price: float) -> None:
        if not self.config.minimum_price <= price <= self.config.maximum_price:
            raise ValueError(
                f"Price {price} is outside "
                f"[{self.config.minimum_price}, {self.config.maximum_price}]."
            )
