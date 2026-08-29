"""Regular-logit demand and profit calculations with an outside option."""

from dataclasses import dataclass
from math import exp
from typing import Sequence

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
    """A differentiated-products Bertrand market with regular-logit demand."""

    def __init__(self, config: MarketConfig | None = None) -> None:
        self.config = config or MarketConfig()

    def evaluate(
        self,
        prices: Sequence[float],
        *,
        round_index: int | None = None,
    ) -> MarketOutcome:
        """Return market shares, quantities, and profits for posted prices."""

        if len(prices) != self.config.number_of_firms:
            raise ValueError(
                f"Expected {self.config.number_of_firms} prices, got {len(prices)}."
            )
        for price in prices:
            self._validate_price(price)

        # Subtracting the largest utility is unnecessary in the reported price
        # range, but this form remains numerically stable for future configs.
        utilities = [
            (self.config.quality - price) / self.config.temperature
            for price in prices
        ]
        shift = max(0.0, *utilities)
        product_weights = [exp(utility - shift) for utility in utilities]
        outside_weight = exp(-shift)
        denominator = outside_weight + sum(product_weights)

        shares = [weight / denominator for weight in product_weights]
        outside_share = outside_weight / denominator
        market_size = self.config.market_size_at(round_index)
        firms = tuple(
            FirmOutcome(
                price=price,
                share=share,
                quantity=market_size * share,
                profit=(price - self.config.marginal_cost)
                * market_size
                * share,
            )
            for price, share in zip(prices, shares, strict=True)
        )
        return MarketOutcome(
            firms=firms,
            outside_share=outside_share,
            market_size=market_size,
        )

    def best_response(
        self,
        rival_price: float,
        *,
        tolerance: float = 1e-10,
    ) -> float:
        """Numerically maximize firm 0's profit against one rival price."""

        self._validate_price(rival_price)

        def objective(own_price: float) -> float:
            return self.evaluate((own_price, rival_price)).firms[0].profit

        return self._golden_section_maximize(objective, tolerance=tolerance)

    def standalone_monopoly_price(self, *, tolerance: float = 1e-10) -> float:
        """Maximize profit for one product facing only the outside option."""

        def objective(price: float) -> float:
            utility = (
                self.config.quality - price
            ) / self.config.temperature
            shift = max(0.0, utility)
            product_weight = exp(utility - shift)
            outside_weight = exp(-shift)
            share = product_weight / (outside_weight + product_weight)
            return (
                (price - self.config.marginal_cost)
                * self.config.market_size
                * share
            )

        return self._golden_section_maximize(objective, tolerance=tolerance)

    def symmetric_nash_price(self, *, tolerance: float = 1e-9) -> float:
        """Solve p = best_response(p) for the symmetric two-firm equilibrium."""

        lower = self.config.minimum_price
        upper = self.config.maximum_price

        def fixed_point_error(price: float) -> float:
            return self.best_response(price) - price

        lower_error = fixed_point_error(lower)
        upper_error = fixed_point_error(upper)
        if lower_error * upper_error > 0:
            raise RuntimeError("Could not bracket a symmetric Nash equilibrium.")

        while upper - lower > tolerance:
            midpoint = (lower + upper) / 2
            error = fixed_point_error(midpoint)
            if error > 0:
                lower = midpoint
            else:
                upper = midpoint
        return (lower + upper) / 2

    def _golden_section_maximize(
        self,
        objective,
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
