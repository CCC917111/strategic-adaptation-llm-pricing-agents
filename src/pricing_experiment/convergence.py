"""Paper-aligned online convergence checks for pricing runs."""

from __future__ import annotations

from dataclasses import asdict, dataclass
from statistics import fmean, pstdev
from typing import Sequence


@dataclass(frozen=True, slots=True)
class ConvergenceConfig:
    minimum_rounds: int = 40
    check_every: int = 5
    window: int = 20
    coefficient_of_variation: float = 0.03
    mean_shift: float = 0.01

    def __post_init__(self) -> None:
        if self.minimum_rounds < self.window:
            raise ValueError("minimum_rounds must be at least window.")
        if self.check_every < 1:
            raise ValueError("check_every must be positive.")
        if self.window < 2 or self.window % 2:
            raise ValueError("window must be a positive even number.")
        if self.coefficient_of_variation < 0 or self.mean_shift < 0:
            raise ValueError("convergence tolerances cannot be negative.")

    def to_dict(self) -> dict[str, int | float]:
        return asdict(self)


def convergence_diagnostics(
    executed_prices: Sequence[tuple[float, float]],
    config: ConvergenceConfig | None = None,
) -> dict[str, object] | None:
    """Return diagnostics at a scheduled checkpoint, otherwise ``None``.

    The paper checks from round 40 onward in five-round increments, using the
    latest 20 rounds.  Both firms must independently satisfy the CV and
    half-window mean-shift thresholds.
    """

    c = config or ConvergenceConfig()
    rounds = len(executed_prices)
    if rounds < c.minimum_rounds:
        return None
    if (rounds - c.minimum_rounds) % c.check_every:
        return None

    half = c.window // 2
    firms: list[dict[str, float | int | bool]] = []
    for firm_id in range(2):
        values = [
            float(pair[firm_id]) for pair in executed_prices[-c.window :]
        ]
        mean_price = fmean(values)
        cv = pstdev(values) / mean_price if mean_price else float("inf")
        previous_mean = fmean(values[:half])
        recent_mean = fmean(values[half:])
        shift = abs(recent_mean - previous_mean)
        firms.append(
            {
                "firm_id": firm_id,
                "mean_price": mean_price,
                "coefficient_of_variation": cv,
                "mean_shift": shift,
                "stable": (
                    cv <= c.coefficient_of_variation
                    and shift <= c.mean_shift
                ),
            }
        )
    return {
        "round": rounds,
        "window": c.window,
        "stable": all(bool(item["stable"]) for item in firms),
        "firms": firms,
    }

