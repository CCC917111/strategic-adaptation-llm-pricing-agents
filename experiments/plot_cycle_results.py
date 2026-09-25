"""Rebuild Arm2 figures from the public CSV, without a model/API call."""

from __future__ import annotations

import argparse
import csv
from collections import defaultdict
from pathlib import Path
from statistics import mean, stdev

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt


def plot(data: Path, output: Path):
    records = list(csv.DictReader((data / "price-trajectories.csv").open()))
    series = defaultdict(dict)
    demand = {}
    for row in records:
        seed, firm, rnd = int(row["seed"]), int(row["firm"]), int(row["round"])
        series[seed, firm][rnd] = float(row["executed_price"])
        demand[rnd] = float(row["market_size"])
    if set(series) != {(s, f) for s in range(5) for f in (0, 1)}:
        raise ValueError("Expected five runs and two firms per run.")
    if any(set(values) != set(range(1, 81)) for values in series.values()):
        raise ValueError("Every firm needs 80 contiguous rounds.")
    rounds = list(range(1, 81))
    means = {s: [mean((series[s, 0][r], series[s, 1][r])) for r in rounds] for s in range(5)}
    plt.rcParams.update({"font.family": "DejaVu Sans", "font.size": 10,
                         "axes.spines.top": False, "axes.spines.right": False})
    output.mkdir(parents=True, exist_ok=True)
    colors = ["#2B6CB0", "#B45309", "#15803D", "#7C3AED", "#BE185D"]

    def benchmarks(ax):
        ax.axhline(1.47292666, color="#475569", ls="--", lw=1, label="Nash 1.473")
        ax.axhline(1.92498092, color="#64748B", ls="-.", lw=1, label="Joint-profit 1.925")
        ax.axvline(40.5, color="#94A3B8", ls=":", lw=1)
        ax.grid(axis="y", color="#E2E8F0", lw=.7)
        ax.set_xlim(1, 80)
        ax.set_xlabel("Round")

    fig, axes = plt.subplots(2, 3, figsize=(14, 7.6), constrained_layout=True)
    low = min(float(r["executed_price"]) for r in records)
    high = max(float(r["executed_price"]) for r in records)
    for seed, ax in enumerate(axes.flat[:5]):
        color = colors[seed]
        ax.plot(rounds, list(series[seed, 0].values()), color=color, alpha=.45, ls="--", lw=1.2, label="Firm 0")
        ax.plot(rounds, list(series[seed, 1].values()), color=color, alpha=.55, ls=":", lw=1.4, label="Firm 1")
        ax.plot(rounds, means[seed], color=color, lw=2, label="Two-firm mean")
        benchmarks(ax)
        ax.set_ylim(min(1.43, low - .03), high + .05)
        ax.set_title(f"Run {seed}", loc="left", fontweight="bold")
        ax.set_ylabel("Executed price")
        if seed == 0:
            ax.legend(fontsize=8, ncol=2, loc="upper right")
    ax = axes.flat[5]
    ax.plot(rounds, [demand[r] for r in rounds], color="#334155", lw=2)
    ax.axvline(40.5, color="#94A3B8", ls=":", lw=1)
    ax.set(title="Shared market-size cycle", xlabel="Round", ylabel="Market size")
    ax.set_xlim(1, 80)
    ax.set_ylim(40, 160)
    ax.grid(axis="y", color="#E2E8F0", lw=.7)
    fig.suptitle("Arm2: deterministic demand cycle · five runs · passive execution", fontsize=16, fontweight="bold")
    fig.savefig(output / "arm2-run-trajectories.png", dpi=180)
    plt.close(fig)

    fig, (ax, demand_ax) = plt.subplots(2, 1, figsize=(11, 7), sharex=True,
                                      gridspec_kw={"height_ratios": [3, 1]}, constrained_layout=True)
    xs = list(range(3, 81, 5))
    blocked = {s: [mean(means[s][i:i+5]) for i in range(0, 80, 5)] for s in range(5)}
    avg = [mean(blocked[s][i] for s in range(5)) for i in range(16)]
    sd = [stdev(blocked[s][i] for s in range(5)) for i in range(16)]
    for seed in range(5):
        ax.plot(xs, blocked[seed], color=colors[seed], lw=1, alpha=.5, label=f"Run {seed}")
    ax.fill_between(xs, [m-s for m,s in zip(avg,sd)], [m+s for m,s in zip(avg,sd)],
                    color="#334155", alpha=.13, label="Mean ± 1 sample SD (5 runs)")
    ax.plot(xs, avg, color="#0F172A", lw=2.8, marker="o", markersize=3, label="Across-run mean")
    benchmarks(ax)
    ax.set_xlabel("")
    ax.set_ylabel("Executed price · five-round mean")
    ax.legend(ncol=3, fontsize=8.5, loc="upper right")
    ax.set_ylim(min(1.43, min(m-s for m,s in zip(avg,sd))-.02), max(m+s for m,s in zip(avg,sd))+.08)
    demand_ax.plot(rounds, [demand[r] for r in rounds], color="#475569", lw=1.8)
    demand_ax.axvline(40.5, color="#94A3B8", ls=":", lw=1)
    demand_ax.set_ylabel("Market size")
    demand_ax.set_xlabel("Round · price points represent blocks 1–5, 6–10, …, 76–80")
    demand_ax.set_yticks([50, 100, 150])
    demand_ax.set_ylim(40, 160)
    demand_ax.grid(axis="y", color="#E2E8F0", lw=.7)
    fig.suptitle("Arm2: average pricing across five independent runs", fontsize=16, fontweight="bold")
    fig.savefig(output / "arm2-five-run-aggregate.png", dpi=180)
    plt.close(fig)
    print("Saved the two Arm2 figures.")


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=Path("results/arm2-cycle"))
    parser.add_argument("--output", type=Path, default=Path("results/figures"))
    args = parser.parse_args()
    plot(args.data, args.output)
