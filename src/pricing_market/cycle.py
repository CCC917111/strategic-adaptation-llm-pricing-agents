"""Arm2: a deterministic cycle in market size, not in price sensitivity."""

from dataclasses import dataclass
from math import cos, isfinite, pi, sin

from .config import MarketConfig
from .market import LogitMarket


@dataclass(frozen=True, slots=True)
class CycleConfig:
    baseline: float = 100.0
    amplitude: float = 0.5
    period: int = 40

    def __post_init__(self) -> None:
        if not isfinite(self.baseline) or self.baseline <= 0:
            raise ValueError("baseline must be finite and positive.")
        if not isfinite(self.amplitude) or not 0 <= self.amplitude < 1:
            raise ValueError("amplitude must lie in [0, 1).")
        if isinstance(self.period, bool) or not isinstance(self.period, int) or self.period < 4:
            raise ValueError("period must be an integer of at least four rounds.")

    def state(self, round_index: int) -> dict[str, int | float | str]:
        if isinstance(round_index, bool) or not isinstance(round_index, int) or round_index < 1:
            raise ValueError("round_index must be a positive integer.")
        # Index the first observation at t=0; never advance phase on an API retry.
        t = round_index - 1
        angle = 2 * pi * (t % self.period) / self.period
        slope = cos(angle)
        phase = "turning" if abs(slope) < 1e-12 else ("expansion" if slope > 0 else "contraction")
        if self.amplitude == 0:
            phase = "stationary"
        return {
            "round_index": round_index,
            "t": t,
            "cycle": t // self.period + 1,
            "phase": phase,
            "market_size": self.baseline * (1 + self.amplitude * sin(angle)),
        }


class CyclicLogitMarket(LogitMarket):
    """Shared beta(t) scales both firms' sales; shares and static optima stay fixed."""

    def __init__(self, cycle: CycleConfig | None = None) -> None:
        self.cycle = cycle or CycleConfig()
        super().__init__(MarketConfig(market_size=self.cycle.baseline))

    def market_size_at(self, round_index: int | None = None) -> float:
        # Benchmark helpers with no round refer to the baseline-sized market.
        if round_index is None:
            return self.cycle.baseline
        return float(self.cycle.state(round_index)["market_size"])
