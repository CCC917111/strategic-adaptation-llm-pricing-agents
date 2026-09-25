"""Validate and export all five historical stationary runs; no model calls.

Supply the original seed-0, seed-1, and seed-2/3/4 archive directories.
Only numerical outcomes and file hashes are exported, never API receipts.
"""
import argparse
import csv
import hashlib
import json
import math
from pathlib import Path
from statistics import mean, stdev

MODES = ("passive", "revision", "veto")
NASH, MONO = 1.473, 1.802


def write_csv(path, rows):
    with path.open("w", newline="", encoding="utf-8") as handle:
        writer = csv.DictWriter(handle, fieldnames=list(rows[0]))
        writer.writeheader()
        writer.writerows(rows)


def export(roots, output):
    prices, summaries, sources = [], [], []
    series = {}
    transitions = unchanged = small = 0
    for seed in range(5):
        root = roots[seed] if seed < 2 else roots[2] / f"seed{seed}"
        for mode in MODES:
            folder = root / mode
            manifest = json.loads((folder / "manifest.json").read_text())
            path = folder / "rounds.jsonl"
            rows = [json.loads(line) for line in path.read_text().splitlines() if line.strip()]
            assert manifest["status"] == "completed"
            assert [r["round_index"] for r in rows] == list(range(1, len(rows) + 1))
            assert 40 <= len(rows) <= 100
            sources.append({"run": seed, "mode": mode, "rounds": len(rows),
                            "rounds_sha256": hashlib.sha256(path.read_bytes()).hexdigest(),
                            "manifest_sha256": hashlib.sha256((folder / "manifest.json").read_bytes()).hexdigest()})
            flagged = interventions = 0
            for index, row in enumerate(rows):
                t = row["round_index"]
                ps = row["executed_prices"]
                assert math.isclose(row["market_outcome"]["market_size"], 1.0)
                weights = [math.exp((2 - p) / .25) for p in ps]
                for firm, proposal in enumerate(row["proposals"]):
                    price = ps[firm]
                    outcome = row["market_outcome"]["firms"][firm]
                    share = weights[firm] / (1 + sum(weights))
                    assert 1 <= price <= 3
                    assert math.isclose(outcome["quantity"], share, abs_tol=1e-10)
                    assert math.isclose(outcome["profit"], (price - 1) * share, abs_tol=1e-10)
                    flag = row["assessments"][firm]["flagged"]
                    active = flag and not row["assessments"][firm]["warmup"]
                    if mode == "passive" or not active:
                        expected = proposal["price"]
                    elif mode == "revision":
                        expected = max(1, min(row["revisions"][firm]["price"], proposal["price"] - .01))
                    else:
                        expected = max(1, min(proposal["price"], 1.08 * NASH, rows[index - 1]["executed_prices"][firm]))
                    assert math.isclose(price, expected, abs_tol=1e-10)
                    flagged += bool(flag)
                    interventions += bool(active and mode != "passive")
                    prices.append({"seed": seed, "mode": mode, "round": t, "firm_id": firm,
                                   "proposal_price": proposal["price"], "executed_price": price,
                                   "quantity": outcome["quantity"], "profit": outcome["profit"], "flagged": flag})
                    if t >= 11:
                        delta = abs(proposal["price"] - rows[index - 1]["proposals"][firm]["price"])
                        transitions += 1
                        unchanged += delta <= 1e-12
                        small += delta <= .05 + 1e-12
            values = [mean(r["executed_prices"]) for r in rows]
            series[seed, mode] = values
            late = mean(values[-20:])
            summaries.append({"seed": seed, "mode": mode, "rounds": len(rows), "final_window": 20,
                              "late_window_mean_price": late,
                              "supracompetitive_index": (late - NASH) / (MONO - NASH),
                              "flagged_agent_rounds": flagged, "intervention_agent_rounds": interventions})
    common_end = min(len(v) for v in series.values())
    aggregates = []
    for mode in MODES:
        for t in range(5, common_end + 1):
            values = [mean(series[seed, mode][t - 5:t]) for seed in range(5)]
            avg, sd = mean(values), stdev(values)
            aggregates.append({"mode": mode, "round": t, "n_runs": 5,
                               **{f"run{seed}": v for seed, v in enumerate(values)},
                               "mean": avg, "sample_sd": sd,
                               "mean_minus_sd": avg - sd, "mean_plus_sd": avg + sd})
    output.mkdir(parents=True, exist_ok=True)
    write_csv(output / "price-trajectories.csv", prices)
    write_csv(output / "run-summary.csv", summaries)
    write_csv(output / "five-round-aggregate.csv", aggregates)
    provenance = {"experiment": "stationary-market five-run descriptive summary",
                  "run_ids": list(range(5)), "modes": list(MODES),
                  "records": len(prices), "market_rounds": len(prices) // 2,
                  "common_rounds": [1, common_end], "source_files": sources,
                  "aggregation": "Two-firm mean per round, then trailing five-round mean within each run; sample SD (ddof=1) across five runs. No endpoint padding.",
                  "interpretation": "Completed historical runs pooled descriptively across batches; SD is between-run dispersion, not a confidence interval or a treatment-effect estimate.",
                  "proposal_movement_round11_onward": {"transitions": transitions, "unchanged": unchanged, "at_most_0p05": small}}
    (output / "provenance.json").write_text(json.dumps(provenance, indent=2) + "\n")
    print(json.dumps({"records": len(prices), "summaries": summaries, "movement": provenance["proposal_movement_round11_onward"]}, indent=2))


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--seed0-root", type=Path, required=True)
    parser.add_argument("--seed1-root", type=Path, required=True)
    parser.add_argument("--seed234-root", type=Path, required=True)
    parser.add_argument("--output", type=Path, default=Path("results/stationary-five-run"))
    args = parser.parse_args()
    export((args.seed0_root, args.seed1_root, args.seed234_root), args.output)
