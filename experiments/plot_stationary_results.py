"""Rebuild full five-run stationary figures from public CSVs, without API calls."""
import argparse
import csv
import math
from pathlib import Path
from statistics import mean, stdev

import matplotlib
matplotlib.use("Agg")
import matplotlib.pyplot as plt

MODES = ("passive", "revision", "veto")
TITLES = ("Passive", "Revision", "Veto / replacement")
COLORS = ("#287ab3", "#ff7f0e", "#2ba33a")
ROOT = Path(__file__).resolve().parents[1]


def read(path):
    with path.open(newline="", encoding="utf-8") as handle:
        return list(csv.DictReader(handle))


def plot(data, output):
    rows = read(data / "price-trajectories.csv")
    summaries = read(data / "run-summary.csv")
    aggregates = read(data / "five-round-aggregate.csv")
    output.mkdir(parents=True, exist_ok=True)
    plt.rcParams.update({"axes.spines.top": False, "axes.spines.right": False})
    fig, axes = plt.subplots(5, 3, figsize=(15, 16), sharey=True, layout="constrained")
    series = {}
    for seed in range(5):
        for col, (mode, title, color) in enumerate(zip(MODES, TITLES, COLORS)):
            summary = next(r for r in summaries if int(r["seed"]) == seed and r["mode"] == mode)
            n = int(summary["rounds"])
            cell = [r for r in rows if int(r["seed"]) == seed and r["mode"] == mode]
            values = {(int(r["round"]), int(r["firm_id"])): float(r["executed_price"]) for r in cell}
            assert len(cell) == 2 * n and set(values) == {(t, f) for t in range(1, n + 1) for f in (0, 1)}
            ts = list(range(1, n + 1))
            firms = [[values[t, f] for t in ts] for f in (0, 1)]
            means = [mean(pair) for pair in zip(*firms)]
            series[seed, mode] = means
            late = mean(means[-20:])
            assert math.isclose(late, float(summary["late_window_mean_price"]), abs_tol=1e-10)
            assert math.isclose((late-1.473)/.329, float(summary["supracompetitive_index"]), abs_tol=1e-10)
            ax = axes[seed, col]
            for f, style in enumerate(("--", ":")):
                ax.plot(ts, firms[f], style, color=color, alpha=.4, label=f"Firm {f}")
            ax.plot(ts, means, color=color, lw=2, label="Two-firm mean")
            decorate(ax)
            ax.set_xlim(1, n)
            if seed == 0: ax.set_title(title, fontweight="bold")
            if col == 0: ax.set_ylabel(f"Run {seed}\nExecuted price")
            if seed == 4: ax.set_xlabel("Round")
    axes[0, 2].legend(frameon=False, fontsize=8)
    fig.suptitle("Stationary market: five runs under three oversight modes", fontweight="bold")
    fig.savefig(output / "individual-trajectories.png", dpi=180)
    plt.close(fig)
    fig, axes = plt.subplots(1, 3, figsize=(15, 5), sharey=True, layout="constrained")
    for ax, mode, title, color in zip(axes, MODES, TITLES, COLORS):
        records = [r for r in aggregates if r["mode"] == mode]
        for r in records:
            t = int(r["round"])
            vals = [mean(series[s, mode][t-5:t]) for s in range(5)]
            assert all(math.isclose(vals[s], float(r[f"run{s}"]), abs_tol=1e-10) for s in range(5))
            assert math.isclose(mean(vals), float(r["mean"]), abs_tol=1e-10)
            assert math.isclose(stdev(vals), float(r["sample_sd"]), abs_tol=1e-10)
        ts = [int(r["round"]) for r in records]
        for field, style, label in (("mean", "-", "Mean"), ("mean_minus_sd", "--", "Mean - 1 SD"), ("mean_plus_sd", ":", "Mean + 1 SD")):
            ax.plot(ts, [float(r[field]) for r in records], style, color=color, lw=2.5 if field == "mean" else 1.4, label=label)
        decorate(ax)
        ax.set(title=title, xlabel="Round (trailing 5-round average)", xlim=(5, max(ts)))
    axes[0].set_ylabel("Executed price")
    axes[2].legend(frameon=False)
    fig.suptitle("Stationary market: five-run mean and sample standard deviation", fontweight="bold")
    fig.savefig(output / "five-run-aggregate.png", dpi=180)
    plt.close(fig)
    print("Validated all 15 trajectories, final-window metrics, and five-run aggregates.")


def decorate(ax):
    ax.axvline(10, color="#96a0aa", ls=":", lw=1)
    ax.axhline(1.473, color="#555", ls="--", lw=1)
    ax.axhline(1.802, color="#888", ls="-.", lw=1)
    ax.grid(axis="y", alpha=.2)


if __name__ == "__main__":
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument("--data", type=Path, default=ROOT / "results/stationary-five-run")
    parser.add_argument("--output", type=Path, default=ROOT / "results/stationary-five-run")
    args = parser.parse_args()
    plot(args.data, args.output)
