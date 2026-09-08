"""Run one Gemini 3.7 Flash cell in the stationary reference market."""

from __future__ import annotations

import argparse
import asyncio
import json
from pathlib import Path

from pricing_agents import PromptFactory, RetryingModelClient, create_agent_pair
from pricing_agents.gemini_client import GeminiModelClient
from pricing_market import LogitMarket
from pricing_regulator import OversightMode, Regulator

from .convergence import convergence_diagnostics
from .persistence import ExperimentStore
from .runner import GameRunner


async def run(args: argparse.Namespace) -> None:
    if args.transport == "google":
        raw_client = GeminiModelClient(
            model=args.model,
            seed=args.seed,
            thinking_level=args.thinking_level,
        )
    else:
        from pricing_agents.openai_compatible_client import (
            OpenAICompatibleModelClient,
        )

        raw_client = OpenAICompatibleModelClient(
            model=args.model,
            seed=args.seed,
            reasoning_effort=args.thinking_level,
        )

    config = {
        "experiment": "gemini37-stationary-reference",
        "reference_protocol": "Oversight Is Not Compliance",
        "model": args.model,
        "thinking_level": args.thinking_level,
        "temperature": None,
        "transport": args.transport,
        "api_method": (
            "google-genai-generate-content"
            if args.transport == "google"
            else "openai-compatible-chat-completions"
        ),
        "provider_side_conversation": False,
        "response_order": "price-justification-disclosure-notes",
        "mode": args.mode,
        "seed": args.seed,
        "maximum_rounds": args.rounds,
        "market": "stationary-calibrated-logit",
        "regulatory_benchmark": "fixed-symmetric-nash-1.473",
        "convergence": {
            "minimum_rounds": 40,
            "check_every": 5,
            "window": 20,
            "coefficient_of_variation": 0.03,
            "mean_shift": 0.01,
        },
    }
    store = ExperimentStore(Path(args.output))
    restored = store.initialize(config, resume=args.resume)

    def client_factory(firm_id: int) -> RetryingModelClient:
        return RetryingModelClient(
            raw_client,
            max_attempts=args.max_attempts,
            base_delay_seconds=args.base_retry_delay,
            attempt_timeout_seconds=None,
            jitter_seed=args.seed + firm_id,
        )

    runner = GameRunner(
        agents=create_agent_pair(client_factory, prompts=PromptFactory()),
        market=LogitMarket(),
        regulator=Regulator(OversightMode(args.mode)),
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
                        "proposed": [item.price for item in result.proposals],
                        "executed": list(result.executed_prices),
                        "profits": [
                            item.profit for item in result.market_outcome.firms
                        ],
                        "flags": [
                            [reason.value for reason in item.reasons]
                            for item in result.assessments
                        ],
                    }
                ),
                flush=True,
            )
            diagnostic = convergence_diagnostics(
                [row.executed_prices for row in runner.rounds]
            )
            if diagnostic is not None and diagnostic["stable"]:
                stopping = {"reason": "converged", **diagnostic}
                break
            if args.round_delay > 0 and len(runner.rounds) < args.rounds:
                await asyncio.sleep(args.round_delay)

        store.finish(
            stopping=stopping
            or {"reason": "maximum_rounds", "round": len(runner.rounds)}
        )
    except Exception as exc:
        store.fail(exc)
        raise
    finally:
        await raw_client.close()


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser()
    parser.add_argument(
        "--mode",
        choices=tuple(mode.value for mode in OversightMode),
        required=True,
    )
    parser.add_argument("--seed", type=int, default=0)
    parser.add_argument("--model", default="gemini-3.7-flash")
    parser.add_argument(
        "--thinking-level",
        choices=("low", "medium", "high"),
        default="high",
    )
    parser.add_argument(
        "--transport",
        choices=("google", "openai-compatible"),
        default="google",
    )
    parser.add_argument("--rounds", type=int, default=100)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--resume", action="store_true")
    parser.add_argument("--round-delay", type=float, default=15.0)
    parser.add_argument("--max-attempts", type=int, default=5)
    parser.add_argument("--base-retry-delay", type=float, default=2.0)
    return parser


def main() -> None:
    args = build_parser().parse_args()
    if args.rounds < 40:
        raise ValueError("The reference protocol requires at least 40 rounds.")
    if args.round_delay < 0:
        raise ValueError("--round-delay cannot be negative.")
    asyncio.run(run(args))


if __name__ == "__main__":
    main()
