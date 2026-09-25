"""Run the basic Arm2 condition: five repeats, INFER, passive, fixed 80 rounds.

No ablation or intervention is launched by this command. API receipts and raw
notes are local artifacts and must be reviewed before any public release.
"""

from __future__ import annotations

import argparse
import asyncio
import csv
import hashlib
import json
import os
import shutil
from dataclasses import asdict
from pathlib import Path

from pricing_agents import RetryingModelClient, create_agent_pair
from pricing_agents.cycle_prompts import CyclePromptFactory
from pricing_market.cycle import CycleConfig, CyclicLogitMarket
from pricing_regulator import OversightMode, Regulator

from .persistence import ExperimentStore, utc_now
from .runner import GameRunner


def write_json(path: Path, value: dict) -> None:
    temporary = path.with_suffix(path.suffix + ".tmp")
    temporary.write_text(json.dumps(value, indent=2, ensure_ascii=False) + "\n")
    os.replace(temporary, path)


def cell_config(args: argparse.Namespace, seed: int) -> dict:
    return {
        "experiment": "arm2-deterministic-cycle-v1",
        "model_requested": args.model,
        "reasoning_effort_requested": args.thinking_level,
        "temperature_requested": args.temperature,
        "seed_requested": seed,
        "transport": "openai_chat_completions",
        "endpoint_host": args.endpoint_host,
        "mode": "passive",
        "prompt": "unchanged-historical-local-paper-prompt",
        "information": "INFER: past prices and own outcomes; no market index or phase",
        "cycle": asdict(CycleConfig()),
        "indexing": "round r uses t=r-1; first market size is 100",
        "rounds": 80,
        "early_stopping": False,
        "round_delay_seconds": args.round_delay,
        "source_sha256": args.source_sha256,
    }


def make_runner(client, seed: int) -> GameRunner:
    return GameRunner(
        agents=create_agent_pair(
            lambda firm: RetryingModelClient(
                client, max_attempts=5, base_delay_seconds=2,
                attempt_timeout_seconds=None, jitter_seed=seed + firm,
            ),
            prompts=CyclePromptFactory(),
        ),
        market=CyclicLogitMarket(),
        regulator=Regulator(OversightMode.PASSIVE),
    )


def validate_path(rows, *, completed: bool = False) -> None:
    if len(rows) > 80 or (completed and len(rows) != 80):
        raise ValueError("Checkpoint length does not match the fixed horizon.")
    cycle = CycleConfig()
    for row in rows:
        expected = float(cycle.state(row.round_index)["market_size"])
        if abs(row.market_outcome.market_size - expected) > 1e-9:
            raise ValueError("Checkpoint does not match the Arm2 demand path.")


async def run_cell(args: argparse.Namespace, seed: int, limiter: asyncio.Semaphore) -> dict:
    from pricing_agents.openai_compatible_client import OpenAICompatibleModelClient

    directory = args.output / f"seed{seed}"
    store = ExperimentStore(directory)
    config = cell_config(args, seed)
    # Enforce configuration identity even on a completed resume.
    if store.manifest_path.exists():
        previous = json.loads(store.manifest_path.read_text())
        if previous["config"] != config:
            raise ValueError(f"seed{seed}: configuration differs from saved run.")
        if previous["status"] == "completed":
            validate_path(store.load_rounds(), completed=True)
            if not args.resume:
                raise FileExistsError("Completed cell exists; use --resume or a new directory.")
            return {"seed": seed, "status": "completed", "rounds": 80}
    restored = store.initialize(config, resume=args.resume)
    validate_path(restored)

    class LimitedClient(OpenAICompatibleModelClient):
        async def generate(self, **kwargs):
            async with limiter:
                return await super().generate(**kwargs)

    client = LimitedClient(
        model=args.model, seed=seed, temperature=args.temperature,
        reasoning_effort=args.thinking_level,
        receipt_path=directory / "api-receipts.jsonl",
    )
    runner = make_runner(client, seed)
    runner.restore(restored)
    try:
        while len(runner.rounds) < 80:
            row = await runner.run_round()
            store.append_round(row)
            print(json.dumps({
                "seed": seed, "round": row.round_index,
                "market_size": row.market_outcome.market_size,
                "prices": row.executed_prices, "at": utc_now(),
            }), flush=True)
            if args.round_delay and len(runner.rounds) < 80:
                await asyncio.sleep(args.round_delay)
        store.finish(stopping={"reason": "fixed_horizon", "round": 80})
        return {"seed": seed, "status": "completed", "rounds": 80}
    except Exception as exc:
        # Provider errors may contain URLs or response text; keep only their type.
        store.fail(RuntimeError(type(exc).__name__))
        return {"seed": seed, "status": "failed", "rounds": len(runner.rounds),
                "error_type": type(exc).__name__}
    finally:
        await client.close()


async def run_suite(args: argparse.Namespace) -> None:
    from urllib.parse import urlsplit
    import httpx

    if args.round_delay < 0 or not 0 <= args.temperature <= 2:
        raise ValueError("Invalid delay or temperature.")
    if len(args.seeds) != 5 or len(set(args.seeds)) != 5 or min(args.seeds) < 0:
        raise ValueError("Provide five distinct nonnegative seed identifiers.")
    endpoint = os.environ.get("GEMINI_OPENAI_COMPATIBLE_BASE_URL", "").rstrip("/")
    parsed = urlsplit(endpoint)
    if parsed.scheme != "https" or not parsed.hostname or parsed.username or parsed.password or parsed.query or parsed.fragment:
        raise ValueError("Configure a plain HTTPS API base URL without credentials or query.")
    key = os.environ.get("GEMINI_OPENAI_COMPATIBLE_API_KEY", "")
    if not key:
        raise RuntimeError("GEMINI_OPENAI_COMPATIBLE_API_KEY is not set.")
    args.endpoint_host = parsed.hostname
    source = Path(__file__).resolve().parents[1]
    args.source_sha256 = {
        str(p.relative_to(source)): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sorted(source.rglob("*.py"))
    }
    args.output.mkdir(parents=True, exist_ok=True)
    suite_path = args.output / "suite.json"
    # Validate all saved configs before making a network call or overwriting status.
    for seed in args.seeds:
        manifest = args.output / f"seed{seed}" / "manifest.json"
        if manifest.exists():
            if not args.resume:
                raise FileExistsError("Existing suite; use --resume or a new output directory.")
            if json.loads(manifest.read_text())["config"] != cell_config(args, seed):
                raise ValueError("Existing cell configuration differs from this run.")
    if suite_path.exists():
        previous = json.loads(suite_path.read_text())
        if previous.get("seeds") != args.seeds:
            raise ValueError("Existing suite has different seed identifiers.")
        if previous.get("status") == "completed":
            for seed in args.seeds:
                directory = args.output / f"seed{seed}"
                manifest = json.loads((directory / "manifest.json").read_text())
                if manifest["status"] != "completed":
                    raise ValueError("Inconsistent completed suite.")
                validate_path(ExperimentStore(directory).load_rounds(), completed=True)
            print("All five runs completed; no API calls.", flush=True)
            return

    snapshot = args.output / "code" / "src"
    if not snapshot.exists():
        shutil.copytree(source, snapshot, ignore=shutil.ignore_patterns("__pycache__"))
    snapshot_hashes = {
        str(p.relative_to(snapshot)): hashlib.sha256(p.read_bytes()).hexdigest()
        for p in sorted(snapshot.rglob("*.py"))
    }
    if snapshot_hashes != args.source_sha256:
        raise ValueError("Source differs from the archived code snapshot.")
    with (args.output / "market-path.csv").open("w", newline="") as handle:
        path = [CycleConfig().state(r) for r in range(1, 81)]
        writer = csv.DictWriter(handle, fieldnames=list(path[0]))
        writer.writeheader()
        writer.writerows(path)
    state = {"experiment": "arm2-deterministic-cycle-v1", "status": "starting",
             "started_at": utc_now(), "seeds": args.seeds,
             "config_example": cell_config(args, args.seeds[0]),
             "api_concurrency_limit": 6, "cells": []}
    write_json(suite_path, state)
    try:
        async with httpx.AsyncClient(timeout=30, follow_redirects=False) as client:
            response = await client.get(endpoint + "/models", headers={"Authorization": "Bearer " + key})
            response.raise_for_status()
            if args.model not in {row["id"] for row in response.json().get("data", [])}:
                raise ValueError("Requested model is missing from provider catalog.")
        state.update(status="running", catalog_verified_at=utc_now())
        write_json(suite_path, state)
        limiter = asyncio.Semaphore(6)

        async def tracked(seed):
            try:
                result = await run_cell(args, seed, limiter)
            except Exception as exc:
                result = {"seed": seed, "status": "failed", "error_type": type(exc).__name__}
            state["cells"].append(result)
            write_json(suite_path, state)
            return result

        cells = await asyncio.gather(*(tracked(seed) for seed in args.seeds))
        state.update(status="completed" if all(c["status"] == "completed" for c in cells) else "incomplete",
                     finished_at=utc_now())
    except Exception as exc:
        state.update(status="failed", error_type=type(exc).__name__, finished_at=utc_now())
    write_json(suite_path, state)
    print(json.dumps({"suite_status": state["status"]}), flush=True)
    if state["status"] != "completed":
        raise SystemExit(1)


def main() -> None:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--model", default="gemini-3.7-flash")
    parser.add_argument("--temperature", type=float, default=1.2)
    parser.add_argument("--thinking-level", default="high", choices=("low", "medium", "high"))
    parser.add_argument("--seeds", type=int, nargs=5, default=[0, 1, 2, 3, 4])
    parser.add_argument("--round-delay", type=float, default=15.0)
    parser.add_argument("--resume", action="store_true")
    asyncio.run(run_suite(parser.parse_args()))


if __name__ == "__main__":
    main()
