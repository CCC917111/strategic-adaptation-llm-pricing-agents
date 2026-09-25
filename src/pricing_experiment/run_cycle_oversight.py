"""Fixed-horizon Arm2 cycles under the three unchanged oversight modes.

Each requested mode runs five replicates. Use --modes passive for a passive-only
suite. This entry point writes each cell to seedN/MODE and never imports or
overwrites historical passive-only records.
"""

from __future__ import annotations

import argparse
import asyncio
import csv
import hashlib
import json
import math
import os
import shutil
from contextlib import contextmanager
from dataclasses import asdict
from pathlib import Path
from urllib.parse import urlsplit

from pricing_agents import RetryingModelClient, create_agent_pair
from pricing_agents.cycle_prompts import CyclePromptFactory
from pricing_market.cycle import CycleConfig, CyclicLogitMarket
from pricing_regulator import OversightMode, Regulator

from .persistence import ExperimentStore, utc_now, write_json
from .runner import GameRunner


HORIZON = 80


@contextmanager
def suite_lock(output: Path):
    """Fail before any API call if another process owns this output directory."""
    try:
        import fcntl
    except ImportError as exc:
        raise RuntimeError("This runner requires POSIX file locking (macOS or Linux).") from exc
    output.mkdir(parents=True, exist_ok=True)
    # Do not remove the inode: a second process may already have opened it.
    with (output / ".suite.lock").open("a+", encoding="utf-8") as handle:
        try:
            fcntl.flock(handle.fileno(), fcntl.LOCK_EX | fcntl.LOCK_NB)
        except BlockingIOError:
            raise RuntimeError("Another process is using this output directory.") from None
        try:
            handle.seek(0)
            handle.truncate()
            handle.write(json.dumps({"pid": os.getpid(), "acquired_at": utc_now()}))
            handle.flush()
            yield
        finally:
            fcntl.flock(handle.fileno(), fcntl.LOCK_UN)


def validated_endpoint() -> str:
    endpoint = os.environ.get("GEMINI_OPENAI_COMPATIBLE_BASE_URL", "").strip().rstrip("/")
    try:
        parsed = urlsplit(endpoint)
        safe = (parsed.scheme == "https" and bool(parsed.hostname)
                and parsed.username is None and parsed.password is None
                and "?" not in endpoint and "#" not in endpoint
                and not any(character.isspace() for character in endpoint))
        parsed.port
    except ValueError:
        safe = False
    if not safe:
        raise ValueError("Configure an HTTPS API base URL without credentials, query, or fragment.")
    return endpoint


def cell_config(args: argparse.Namespace, seed: int, mode: str) -> dict:
    return {
        "experiment": "arm2-deterministic-cycle-oversight-v1",
        "model_requested": args.model,
        "reasoning_effort_requested": args.thinking_level,
        "temperature_requested": args.temperature,
        "seed_requested": seed,
        "transport": "openai_chat_completions",
        "endpoint": args.endpoint,
        "mode": OversightMode(mode).value,
        "regulator": asdict(Regulator(mode).config),
        "prompt": "unchanged-historical-local-paper-prompt",
        "information": "INFER: past prices and own outcomes; no market index or phase",
        "cycle": asdict(CycleConfig()),
        "indexing": "round r uses t=r-1; first market size is 100",
        "rounds": HORIZON,
        "early_stopping": False,
        "round_delay_seconds": args.round_delay,
        "save_api_receipts": not args.no_receipts,
        "source_sha256": args.source_sha256,
    }


def make_runner(client, seed: int, mode: str) -> GameRunner:
    return GameRunner(
        agents=create_agent_pair(
            lambda firm: RetryingModelClient(
                client, max_attempts=5, base_delay_seconds=2,
                attempt_timeout_seconds=None, jitter_seed=seed + firm,
            ),
            prompts=CyclePromptFactory(),
        ),
        market=CyclicLogitMarket(),
        regulator=Regulator(mode),
    )


def validate_checkpoint(rows, mode: str, *, completed: bool = False) -> None:
    """Validate horizon, demand path, flags, and mode-specific executed prices."""
    if len(rows) > HORIZON or (completed and len(rows) != HORIZON):
        raise ValueError("Checkpoint length does not match the fixed horizon.")
    regulator = Regulator(mode)
    market = CyclicLogitMarket()
    history = []
    for expected_round, row in enumerate(rows, start=1):
        if row.round_index != expected_round:
            raise ValueError("Checkpoint rounds are not contiguous.")
        expected_size = market.market_size_at(row.round_index)
        if not math.isfinite(row.market_outcome.market_size) or abs(
            row.market_outcome.market_size - expected_size
        ) > 1e-9:
            raise ValueError("Checkpoint does not match the Arm2 demand path.")
        assessments = regulator.assess_round(
            round_index=row.round_index,
            proposed_prices=tuple(p.price for p in row.proposals),
            price_history=history,
        )
        if row.assessments != assessments:
            raise ValueError("Checkpoint flags differ from the oversight protocol.")
        for firm, assessment in enumerate(assessments):
            needs_revision = (regulator.mode is OversightMode.REVISION
                              and assessment.flagged and not assessment.warmup)
            revision = row.revisions[firm]
            if (revision is not None) != needs_revision:
                raise ValueError("Checkpoint revision records do not match the mode.")
            expected_price = regulator.execute_price(
                proposed_price=row.proposals[firm].price,
                assessment=assessment,
                previous_executed_price=history[-1][firm] if history else None,
                revised_price=revision.price if revision else None,
            )
            if not math.isfinite(row.executed_prices[firm]) or abs(
                row.executed_prices[firm] - expected_price
            ) > 1e-12:
                raise ValueError("Checkpoint executed price differs from the oversight rule.")
        if market.evaluate(row.executed_prices, round_index=row.round_index) != row.market_outcome:
            raise ValueError("Checkpoint outcomes differ from the market calculation.")
        history.append(row.executed_prices)


def checked_existing_cell(args, seed: int, mode: str):
    store = ExperimentStore(args.output / f"seed{seed}" / mode)
    if not store.manifest_path.exists():
        if store.rounds_path.exists():
            raise ValueError("Checkpoint data exists without its configuration manifest.")
        return store, None, []
    if not args.resume:
        raise FileExistsError("Existing cell; use --resume or a new output directory.")
    manifest = json.loads(store.manifest_path.read_text())
    if manifest["config"] != cell_config(args, seed, mode):
        raise ValueError("Existing cell configuration differs from this run.")
    rows = store.load_rounds()
    validate_checkpoint(rows, mode, completed=manifest["status"] == "completed")
    return store, manifest, rows


async def run_cell(args: argparse.Namespace, seed: int, mode: str,
                   limiter: asyncio.Semaphore) -> dict:
    from pricing_agents.openai_compatible_client import OpenAICompatibleModelClient

    store, previous, _ = checked_existing_cell(args, seed, mode)
    if previous is not None and previous["status"] == "completed":
        return {"seed": seed, "mode": mode, "status": "completed", "rounds": HORIZON}
    restored = store.initialize(cell_config(args, seed, mode), resume=args.resume)
    validate_checkpoint(restored, mode)

    class LimitedClient(OpenAICompatibleModelClient):
        async def generate(self, **kwargs):
            async with limiter:
                return await super().generate(**kwargs)

    client = None
    runner = None
    try:
        client = LimitedClient(
            model=args.model, seed=seed, temperature=args.temperature,
            reasoning_effort=args.thinking_level, base_url=args.endpoint,
            receipt_path=(None if args.no_receipts else
                          store.output_directory / "api-receipts.jsonl"),
        )
        runner = make_runner(client, seed, mode)
        runner.restore(restored)
        while len(runner.rounds) < HORIZON:
            row = await runner.run_round()
            store.append_round(row)
            print(json.dumps({"seed": seed, "mode": mode, "round": row.round_index,
                              "market_size": row.market_outcome.market_size,
                              "prices": row.executed_prices, "at": utc_now()}), flush=True)
            if args.round_delay and len(runner.rounds) < HORIZON:
                await asyncio.sleep(args.round_delay)
        store.finish(stopping={"reason": "fixed_horizon", "round": HORIZON})
        return {"seed": seed, "mode": mode, "status": "completed", "rounds": HORIZON}
    except Exception as exc:
        store.fail(RuntimeError(type(exc).__name__))
        return {"seed": seed, "mode": mode, "status": "failed",
                "rounds": len(runner.rounds) if runner is not None else len(restored),
                "error_type": type(exc).__name__}
    finally:
        if client is not None:
            await client.close()


async def _run_locked_suite(args: argparse.Namespace) -> None:
    import httpx

    args.endpoint = validated_endpoint()
    source = Path(__file__).resolve().parents[1]
    args.source_sha256 = {
        str(path.relative_to(source)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(source.rglob("*.py"))
    }
    cells = [(seed, mode) for seed in args.seeds for mode in args.modes]
    # Check every existing cell, including its executed prices, before any call.
    existing = [checked_existing_cell(args, seed, mode) for seed, mode in cells]
    suite_path = args.output / "suite.json"
    if suite_path.exists():
        previous = json.loads(suite_path.read_text())
        if previous.get("seeds") != args.seeds or previous.get("modes") != args.modes:
            raise ValueError("Existing suite has different seed identifiers or modes.")
    if all(manifest is not None and manifest["status"] == "completed"
           for _, manifest, _ in existing):
        print("All requested runs completed; no API calls.", flush=True)
        return
    snapshot = args.output / "code" / "src"
    if not snapshot.exists():
        shutil.copytree(source, snapshot, ignore=shutil.ignore_patterns("__pycache__"))
    snapshot_hashes = {
        str(path.relative_to(snapshot)): hashlib.sha256(path.read_bytes()).hexdigest()
        for path in sorted(snapshot.rglob("*.py"))
    }
    if snapshot_hashes != args.source_sha256:
        raise ValueError("Source differs from the archived code snapshot.")
    key = os.environ.get("GEMINI_OPENAI_COMPATIBLE_API_KEY", "").strip()
    if not key:
        raise RuntimeError("GEMINI_OPENAI_COMPATIBLE_API_KEY is not set.")
    with (args.output / "market-path.csv").open("w", newline="", encoding="utf-8") as handle:
        path = [CycleConfig().state(r) for r in range(1, HORIZON + 1)]
        writer = csv.DictWriter(handle, fieldnames=list(path[0]))
        writer.writeheader()
        writer.writerows(path)
    state = {"experiment": "arm2-deterministic-cycle-oversight-v1", "status": "starting",
             "started_at": utc_now(), "seeds": args.seeds, "modes": args.modes,
             "config_example": cell_config(args, *cells[0]),
             "api_concurrency_limit": 6, "cells": []}
    write_json(suite_path, state)
    try:
        async with httpx.AsyncClient(timeout=30, follow_redirects=False) as client:
            response = await client.get(args.endpoint + "/models",
                                        headers={"Authorization": "Bearer " + key})
            response.raise_for_status()
            if args.model not in {row["id"] for row in response.json().get("data", [])}:
                raise ValueError("Requested model is missing from provider catalog.")
        state.update(status="running", catalog_verified_at=utc_now())
        write_json(suite_path, state)
        limiter = asyncio.Semaphore(6)

        async def tracked(seed, mode):
            try:
                result = await run_cell(args, seed, mode, limiter)
            except Exception as exc:
                result = {"seed": seed, "mode": mode, "status": "failed",
                          "error_type": type(exc).__name__}
            state["cells"].append(result)
            write_json(suite_path, state)
            return result

        results = await asyncio.gather(*(tracked(seed, mode) for seed, mode in cells))
        state.update(status="completed" if all(r["status"] == "completed" for r in results)
                     else "incomplete", finished_at=utc_now())
    except Exception as exc:
        state.update(status="failed", error_type=type(exc).__name__, finished_at=utc_now())
    write_json(suite_path, state)
    print(json.dumps({"suite_status": state["status"]}), flush=True)
    if state["status"] != "completed":
        raise SystemExit(1)


async def run_suite(args: argparse.Namespace) -> None:
    if not math.isfinite(args.round_delay) or args.round_delay < 0:
        raise ValueError("round_delay must be finite and nonnegative.")
    if not math.isfinite(args.temperature) or not 0 <= args.temperature <= 2:
        raise ValueError("temperature must lie in [0, 2].")
    if len(args.seeds) != 5 or len(set(args.seeds)) != 5 or min(args.seeds) < 0:
        raise ValueError("Provide five distinct nonnegative seed identifiers.")
    if not args.modes or len(set(args.modes)) != len(args.modes):
        raise ValueError("Provide distinct oversight modes.")
    args.modes = [OversightMode(mode).value for mode in args.modes]
    with suite_lock(args.output):
        await _run_locked_suite(args)


def build_parser() -> argparse.ArgumentParser:
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--output", type=Path, required=True)
    parser.add_argument("--model", default="gemini-3.7-flash")
    parser.add_argument("--temperature", type=float, default=1.2)
    parser.add_argument("--thinking-level", default="high", choices=("low", "medium", "high"))
    parser.add_argument("--seeds", type=int, nargs=5, default=[0, 1, 2, 3, 4])
    parser.add_argument("--modes", nargs="+", choices=[mode.value for mode in OversightMode],
                        default=[mode.value for mode in OversightMode])
    parser.add_argument("--round-delay", type=float, default=15.0)
    parser.add_argument("--no-receipts", action="store_true")
    parser.add_argument("--resume", action="store_true")
    return parser


def main() -> None:
    asyncio.run(run_suite(build_parser().parse_args()))


if __name__ == "__main__":
    main()
