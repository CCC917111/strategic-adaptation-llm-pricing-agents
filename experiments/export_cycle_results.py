"""Validate a completed Arm2 suite and export a compact public dataset.

Does not export request headers, credentials, provider receipts, or local paths.
Text examples use all firms and runs at peaks, troughs, and the final round.
"""

from __future__ import annotations

import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
from statistics import mean, stdev


def write_csv(path, rows):
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def export(root: Path, output: Path):
    suite = json.loads((root / "suite.json").read_text())
    if suite["status"] != "completed" or sorted(suite["seeds"]) != list(range(5)):
        raise ValueError("Expected the completed five-run Arm2 suite.")
    prices, texts, summaries, hashes = [], [], [], {}
    for seed in range(5):
        path = root / f"seed{seed}" / "rounds.jsonl"
        manifest = json.loads((path.parent / "manifest.json").read_text())
        rows = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
        if manifest["status"] != "completed" or len(rows) != 80:
            raise ValueError(f"Incomplete seed {seed}")
        if manifest["stopping"]["reason"] != "fixed_horizon":
            raise ValueError("Unexpected stopping reason.")
        config = manifest["config"]
        assert config["temperature_requested"] == 1.2
        assert config["seed_requested"] == seed
        assert config["mode"] == "passive"
        hashes[f"seed{seed}/rounds.jsonl"] = hashlib.sha256(path.read_bytes()).hexdigest()
        means = []
        unchanged = 0
        small = 0
        for index, row in enumerate(rows, 1):
            assert row["round_index"] == index
            t = index - 1
            angle = 2 * math.pi * (t % 40) / 40
            size = 100 * (1 + .5 * math.sin(angle))
            assert math.isclose(size, row["market_outcome"]["market_size"], abs_tol=1e-9)
            assert row["revisions"] == [None, None]
            phase = "turning" if abs(math.cos(angle)) < 1e-12 else ("expansion" if math.cos(angle) > 0 else "contraction")
            p = row["executed_prices"]
            means.append(mean(p))
            weights = [math.exp((2 - value) / .25) for value in p]
            for firm, decision in enumerate(row["proposals"]):
                assert 1 <= p[firm] <= 3 and decision["price"] == p[firm]
                assert len(decision["notes"]) <= 2000
                outcome = row["market_outcome"]["firms"][firm]
                share = weights[firm] / (1 + sum(weights))
                assert math.isclose(outcome["share"], share, abs_tol=1e-10)
                assert math.isclose(outcome["quantity"], size * share, abs_tol=1e-9)
                assert math.isclose(outcome["profit"], (p[firm] - 1) * size * share, abs_tol=1e-9)
                metadata = decision["api_metadata"]
                assert metadata["temperature_requested"] == 1.2
                assert metadata["seed_requested"] == seed
                assert metadata["model_requested"] == "gemini-3.7-flash"
                prices.append({
                    "seed": seed, "round": index, "t": t, "cycle": t // 40 + 1,
                    "phase": phase, "market_size": size, "firm": firm,
                    "proposed_price": decision["price"], "executed_price": p[firm],
                    "share": share, "quantity": outcome["quantity"], "profit": outcome["profit"],
                    "flagged": row["assessments"][firm]["flagged"],
                })
                if index in (11, 31, 51, 71, 80):
                    texts.append({
                        "seed": seed, "round": index, "firm": firm,
                        "event": "final" if index == 80 else ("peak" if index in (11, 51) else "trough"),
                        "price": p[firm], "public_justification": decision["justification"],
                        "used_competitor_info": decision["used_competitor_info"],
                        "private_notes": decision["notes"],
                    })
                if index > 1:
                    delta = abs(p[firm] - rows[index-2]["executed_prices"][firm])
                    unchanged += delta <= 1e-12
                    small += delta <= .05 + 1e-12
        summaries.append({
            "seed": seed, "rounds": 80, "mean_price_rounds_1_40": mean(means[:40]),
            "mean_price_rounds_41_80": mean(means[40:]), "final_mean_price": means[-1],
            "final_firm0_price": rows[-1]["executed_prices"][0],
            "final_firm1_price": rows[-1]["executed_prices"][1],
            "unchanged_price_transitions": unchanged, "transitions_at_most_0p05": small,
            "total_within_firm_transitions": 158,
        })
    # First average the two firms, then use non-overlapping five-round blocks.
    # The dispersion unit is the run (n=5), never the ten correlated firms.
    blocks = []
    for start in range(1, 81, 5):
        run_values = [mean(row["executed_price"] for row in prices
                           if row["seed"] == seed and start <= row["round"] < start + 5)
                      for seed in range(5)]
        avg, sd = mean(run_values), stdev(run_values)
        blocks.append({"round_start": start, "round_end": start + 4,
                       "round_midpoint": start + 2, "n_runs": 5,
                       **{f"seed{seed}_mean": value for seed, value in enumerate(run_values)},
                       "mean": avg, "sample_sd": sd, "mean_minus_sd": avg - sd,
                       "mean_plus_sd": avg + sd})
    output.mkdir(parents=True, exist_ok=True)
    write_csv(output / "price-trajectories.csv", prices)
    write_csv(output / "run-summary.csv", summaries)
    write_csv(output / "five-round-aggregate.csv", blocks)
    write_csv(output / "text-examples.csv", texts)
    provenance = {"experiment": suite["experiment"], "started_at": suite["started_at"],
                  "finished_at": suite["finished_at"], "records": len(prices),
                  "transport": "YunZhuHub OpenAI-compatible chat completions",
                  "model_requested": "gemini-3.7-flash", "temperature_requested": 1.2,
                  "thinking_requested": "high", "seed_identifiers_requested": list(range(5)),
                  "source_sha256": suite["config_example"]["source_sha256"],
                  "raw_rounds_sha256": hashes,
                  "text_selection": "All firms and runs at rounds 11,31,51,71,80; retrospective, exhaustive for these events.",
                  "aggregation": "Two-firm mean, then non-overlapping five-round mean within each run; mean and sample SD (ddof=1) across five runs."}
    (output / "provenance.json").write_text(json.dumps(provenance, indent=2) + "\n")
    print(json.dumps({"summaries": summaries, "aggregate_final_block": blocks[-1],
                      "numeric_rows": len(prices), "text_rows": len(texts)}, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--root", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path("results/arm2-cycle"))
    args = parser.parse_args()
    export(args.root, args.output)
