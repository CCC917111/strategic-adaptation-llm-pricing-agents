"""Durable experiment records and atomic run manifests."""

import json
import os
from dataclasses import asdict
from datetime import UTC, datetime
from pathlib import Path
from typing import Any

from pricing_agents import PricingDecision
from pricing_market import FirmOutcome, MarketOutcome
from pricing_regulator import FlagReason, RegulatoryAssessment

from .runner import ExperimentRound


SCHEMA_VERSION = 1


def utc_now() -> str:
    return datetime.now(UTC).isoformat()


def round_to_dict(result: ExperimentRound) -> dict[str, Any]:
    return {
        "schema_version": SCHEMA_VERSION,
        "round_index": result.round_index,
        "proposals": [asdict(item) for item in result.proposals],
        "revisions": [
            asdict(item) if item is not None else None for item in result.revisions
        ],
        "assessments": [
            {
                "firm_id": item.firm_id,
                "benchmark_price": item.benchmark_price,
                "reasons": [reason.value for reason in item.reasons],
                "warmup": item.warmup,
                "flagged": item.flagged,
            }
            for item in result.assessments
        ],
        "executed_prices": list(result.executed_prices),
        "market_outcome": {
            "firms": [asdict(item) for item in result.market_outcome.firms],
            "outside_share": result.market_outcome.outside_share,
            "market_size": result.market_outcome.market_size,
        },
    }


def round_from_dict(data: dict[str, Any]) -> ExperimentRound:
    if data.get("schema_version") != SCHEMA_VERSION:
        raise ValueError("Unsupported experiment-round schema version.")
    proposals = tuple(PricingDecision(**item) for item in data["proposals"])
    revisions = tuple(
        PricingDecision(**item) if item is not None else None
        for item in data["revisions"]
    )
    assessments = tuple(
        RegulatoryAssessment(
            firm_id=item["firm_id"],
            benchmark_price=item["benchmark_price"],
            reasons=tuple(FlagReason(reason) for reason in item["reasons"]),
            warmup=item["warmup"],
        )
        for item in data["assessments"]
    )
    market = data["market_outcome"]
    outcome = MarketOutcome(
        firms=tuple(FirmOutcome(**item) for item in market["firms"]),
        outside_share=market["outside_share"],
        market_size=market.get("market_size", 1.0),
    )
    return ExperimentRound(
        round_index=data["round_index"],
        proposals=(proposals[0], proposals[1]),
        revisions=(revisions[0], revisions[1]),
        assessments=(assessments[0], assessments[1]),
        executed_prices=(data["executed_prices"][0], data["executed_prices"][1]),
        market_outcome=outcome,
    )


class ExperimentStore:
    """Append successful rounds and maintain an atomic manifest."""

    def __init__(self, output_directory: str | Path) -> None:
        self.output_directory = Path(output_directory)
        self.rounds_path = self.output_directory / "rounds.jsonl"
        self.manifest_path = self.output_directory / "manifest.json"

    def initialize(
        self, config: dict[str, Any], *, resume: bool
    ) -> list[ExperimentRound]:
        self.output_directory.mkdir(parents=True, exist_ok=True)
        existing = self.load_rounds()
        if existing and not resume:
            raise FileExistsError(
                f"{self.rounds_path} already has {len(existing)} rounds; "
                "use --resume or choose another output directory."
            )
        if self.manifest_path.exists():
            manifest = json.loads(self.manifest_path.read_text())
            if manifest.get("config") != config:
                raise ValueError("Existing manifest configuration differs from this run.")
            manifest.update(
                status="running",
                resumed_at=utc_now(),
                completed_rounds=len(existing),
            )
            self._clear_terminal_fields(manifest)
        else:
            manifest = {
                "schema_version": SCHEMA_VERSION,
                "status": "running",
                "started_at": utc_now(),
                "completed_rounds": len(existing),
                "config": config,
            }
        self._write_manifest(manifest)
        return existing

    def append_round(self, result: ExperimentRound) -> None:
        serialized = json.dumps(
            round_to_dict(result), ensure_ascii=False, separators=(",", ":")
        )
        with self.rounds_path.open("a", encoding="utf-8") as handle:
            handle.write(serialized + "\n")
            handle.flush()
            os.fsync(handle.fileno())
        manifest = json.loads(self.manifest_path.read_text())
        manifest["completed_rounds"] = result.round_index
        manifest["last_checkpoint_at"] = utc_now()
        self._write_manifest(manifest)

    def finish(self, *, stopping: dict[str, Any] | None = None) -> None:
        manifest = json.loads(self.manifest_path.read_text())
        # A resumed run may previously have failed. Completed manifests must not
        # retain that stale failure, which made several archived runs ambiguous.
        for field in ("error", "error_type", "failed_at"):
            manifest.pop(field, None)
        manifest["status"] = "completed"
        manifest["finished_at"] = utc_now()
        if stopping is not None:
            manifest["stopping"] = stopping
        self._write_manifest(manifest)

    def fail(self, exc: Exception) -> None:
        manifest = json.loads(self.manifest_path.read_text())
        manifest.update(
            status="failed",
            failed_at=utc_now(),
            error_type=type(exc).__name__,
            error=str(exc),
        )
        self._write_manifest(manifest)

    def load_rounds(self) -> list[ExperimentRound]:
        if not self.rounds_path.exists():
            return []
        rounds: list[ExperimentRound] = []
        with self.rounds_path.open(encoding="utf-8") as handle:
            for line_number, line in enumerate(handle, start=1):
                if not line.strip():
                    continue
                try:
                    rounds.append(round_from_dict(json.loads(line)))
                except Exception as exc:
                    raise ValueError(
                        f"Invalid checkpoint at line {line_number}."
                    ) from exc
        for expected, item in enumerate(rounds, start=1):
            if item.round_index != expected:
                raise ValueError("Checkpoint rounds are not contiguous.")
        return rounds

    @staticmethod
    def _clear_terminal_fields(manifest: dict[str, Any]) -> None:
        for field in (
            "error",
            "error_type",
            "failed_at",
            "finished_at",
            "stopping",
        ):
            manifest.pop(field, None)

    def _write_manifest(self, manifest: dict[str, Any]) -> None:
        temporary = self.manifest_path.with_suffix(".json.tmp")
        temporary.write_text(
            json.dumps(manifest, indent=2, ensure_ascii=False) + "\n",
            encoding="utf-8",
        )
        os.replace(temporary, self.manifest_path)
