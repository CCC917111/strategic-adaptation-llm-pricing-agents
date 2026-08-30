"""Run a durable two-agent Gemini pricing experiment."""

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
from pricing_market import LogitMarket
from pricing_regulator import OversightMode, Regulator

from .convergence import ConvergenceConfig, convergence_diagnostics
from .persistence import ExperimentStore
from .runner import GameRunner


async def run(args: argparse.Namespace) -> None:
    if args.provider != "gemini":
        raise ValueError("This sanitized runner currently supports Gemini only.")
    if args.paper_main:
        if args.rounds != 100 or args.response_order != "paper":
            raise ValueError("--paper-main requires 100 rounds and paper order.")
        if args.temperature is not None:
            raise ValueError("--paper-main leaves temperature unset.")
        args.early_stop_converged = True

    config = {
        "provider": "gemini",
        "model": args.model,
        "mode": args.mode,
        "requested_rounds": args.rounds,
        "seed": args.seed,
        "response_order": args.response_order,
        "thinking_level": args.thinking_level,
        "temperature": args.temperature,
        "experiment_profile": "paper-main" if args.paper_main else "custom",
    }
    store = ExperimentStore(Path(args.output))
    restored = store.initialize(config, resume=args.resume)

    raw_client = GeminiModelClient(
        model=args.model,
        seed=args.seed,
        thinking_level=args.thinking_level,
        temperature=args.temperature,
        response_order=ResponseOrder(args.response_order),
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
                PromptConfig(response_order=ResponseOrder(args.response_order))
            ),
        ),
        market=LogitMarket(),
        regulator=Regulator(OversightMode(args.mode)),
    )
    runner.restore(restored)
    convergence = ConvergenceConfig()

    try:
        stopping = None
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
            if args.early_stop_converged:
                diagnostic = convergence_diagnostics(
                    [row.executed_prices for row in runner.rounds], convergence
                )
                if diagnostic is not None and diagnostic["stable"]:
                    stopping = {"reason": "converged", **diagnostic}
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
    result.add_argument("--model", default="gemini-3.7-flash")
    result.add_argument("--thinking-level", default="high")
    result.add_argument("--temperature", type=float)
    result.add_argument("--mode", choices=[mode.value for mode in OversightMode], required=True)
    result.add_argument("--rounds", type=int, default=100)
    result.add_argument("--seed", type=int, default=0)
    result.add_argument("--response-order", choices=[order.value for order in ResponseOrder], default="paper")
    result.add_argument("--output", required=True)
    result.add_argument("--resume", action="store_true")
    result.add_argument("--paper-main", action="store_true")
    result.add_argument("--early-stop-converged", action="store_true")
    result.add_argument("--round-delay", type=float, default=0.0)
    result.add_argument("--max-attempts", type=int, default=5)
    result.add_argument("--base-retry-delay", type=float, default=2.0)
    return result


def main() -> None:
    asyncio.run(run(parser().parse_args()))


if __name__ == "__main__":
    main()
