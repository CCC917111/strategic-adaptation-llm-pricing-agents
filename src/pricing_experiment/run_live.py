"""Run one cell of the hidden-demand pricing experiment."""

from __future__ import annotations

import argparse
import asyncio
import json
from pathlib import Path

from pricing_agents import (
    PromptConfig,
    PromptFactory,
    ResponseOrder,
    RetryingModelClient,
    create_agent_pair,
)
from pricing_agents.gemini_client import GeminiModelClient
from pricing_market import LogitMarket, MarketConfig
from pricing_regulator import OversightMode, Regulator

from .convergence import ConvergenceConfig, convergence_diagnostics
from .persistence import ExperimentStore
from .runner import GameRunner


DEMAND_SHIFT_MAX = 0.17328679513998632

INDUSTRY_CONTEXTS = {
    "retail": (
        "Industry context: consumer retail, where purchasing is frequent and "
        "customer choices are readily comparable."
    ),
    "software": (
        "Industry context: B2B software, where purchasing is organizational "
        "and product evaluation is more involved."
    ),
}

MARKET_CONTEXTS = {
    "mature": (
        "Market context: this is a mature, established market operating "
        "under stable category conditions."
    ),
    "expanding": (
        "Market context: the market is in an expansion phase. The category "
        "is broadening beyond its established base, with adoption spreading "
        "to additional customers."
    ),
}


async def run(args: argparse.Namespace) -> None:
    if args.provider != "gemini":
        raise ValueError("This runner currently supports Gemini only.")
    if args.minimum_rounds < args.demand_ramp_end_round + args.window:
        raise ValueError(
            "minimum_rounds must include one full analysis window after the "
            "demand ramp ends."
        )

    demand_shift_max = DEMAND_SHIFT_MAX if args.market == "expanding" else 0.0
    scenario_context = (
        f"{INDUSTRY_CONTEXTS[args.industry]} "
        f"{MARKET_CONTEXTS[args.market]}"
    )
    convergence = ConvergenceConfig(
        minimum_rounds=args.minimum_rounds,
        check_every=args.check_every,
        window=args.window,
        coefficient_of_variation=args.coefficient_of_variation,
        mean_shift=args.mean_shift,
    )
    config = {
        "provider": "gemini",
        "model": args.model,
        "mode": "passive",
        "requested_rounds": args.rounds,
        "seed": args.seed,
        "round_delay_seconds": args.round_delay,
        "max_attempts": args.max_attempts,
        "base_retry_delay_seconds": args.base_retry_delay,
        "response_order": "paper",
        "api_method": args.api_method,
        "feature_context": {"scenario": scenario_context, "firms": ["", ""]},
        "market_demand": {
            "type": "hidden_common_product_utility_intercept_shift",
            "market_size": 1.0,
            "market_size_growth": 0.0,
            "ramp_end_round": args.demand_ramp_end_round,
            "demand_shift_max": demand_shift_max,
            "visible_to_agents": False,
        },
        "early_stopping": {
            "enabled": True,
            "maximum_rounds": args.rounds,
            **convergence.to_dict(),
        },
    }
    store = ExperimentStore(Path(args.output))
    restored = store.initialize(config, resume=args.resume)

    raw_client = GeminiModelClient(
        model=args.model,
        seed=args.seed,
        thinking_level=args.thinking_level,
        temperature=args.temperature,
        response_order=ResponseOrder.PAPER,
        api_method=args.api_method,
        store=False,
    )

    def client_factory(firm_id: int) -> RetryingModelClient:
        return RetryingModelClient(
            raw_client,
            max_attempts=args.max_attempts,
            base_delay_seconds=args.base_retry_delay,
            attempt_timeout_seconds=None,
            jitter_seed=args.seed + firm_id,
        )

    runner = GameRunner(
        agents=create_agent_pair(
            client_factory,
            prompts=PromptFactory(
                PromptConfig(
                    response_order=ResponseOrder.PAPER,
                    scenario_context=scenario_context,
                )
            ),
        ),
        market=LogitMarket(
            MarketConfig(
                demand_shift_max=demand_shift_max,
                demand_shift_ramp_end_round=args.demand_ramp_end_round,
            )
        ),
        regulator=Regulator(OversightMode.PASSIVE),
    )
    runner.restore(restored)

    try:
        stopping: dict[str, object] | None = None
        while len(runner.rounds) < args.rounds:
            result = await runner.run_round()
            store.append_round(result)
            print(
                json.dumps(
                    {
                        "round": result.round_index,
                        "executed_prices": result.executed_prices,
                        "profits": [
                            firm.profit for firm in result.market_outcome.firms
                        ],
                    }
                ),
                flush=True,
            )
            diagnostic = convergence_diagnostics(
                [row.executed_prices for row in runner.rounds], convergence
            )
            if diagnostic is not None and diagnostic["stable"]:
                stopping = {
                    "reason": "converged",
                    **diagnostic,
                    "environment_plateau_round": args.demand_ramp_end_round,
                    "post_plateau_rounds_observed": (
                        result.round_index - args.demand_ramp_end_round
                    ),
                }
                break
            if args.round_delay > 0:
                await asyncio.sleep(args.round_delay)
        store.finish(stopping=stopping or {"reason": "maximum_rounds"})
    except Exception as exc:
        store.fail(exc)
        raise
    finally:
        await raw_client.close()


def parser() -> argparse.ArgumentParser:
    result = argparse.ArgumentParser()
    result.add_argument("--provider", default="gemini")
    result.add_argument("--model", default="gemini-3.5-flash-lite")
    result.add_argument(
        "--api-method",
        choices=("generate_content", "interactions", "auto"),
        default="generate_content",
    )
    result.add_argument("--thinking-level")
    result.add_argument("--temperature", type=float)
    result.add_argument("--market", choices=tuple(MARKET_CONTEXTS), required=True)
    result.add_argument("--industry", choices=tuple(INDUSTRY_CONTEXTS), required=True)
    result.add_argument("--rounds", type=int, default=100)
    result.add_argument("--minimum-rounds", type=int, default=60)
    result.add_argument("--demand-ramp-end-round", type=int, default=40)
    result.add_argument("--check-every", type=int, default=5)
    result.add_argument("--window", type=int, default=20)
    result.add_argument("--coefficient-of-variation", type=float, default=0.03)
    result.add_argument("--mean-shift", type=float, default=0.01)
    result.add_argument("--seed", type=int, default=0)
    result.add_argument("--output", required=True)
    result.add_argument("--resume", action="store_true")
    result.add_argument("--round-delay", type=float, default=2.0)
    result.add_argument("--max-attempts", type=int, default=1)
    result.add_argument("--base-retry-delay", type=float, default=2.0)
    return result


def main() -> None:
    asyncio.run(run(parser().parse_args()))


if __name__ == "__main__":
    main()
