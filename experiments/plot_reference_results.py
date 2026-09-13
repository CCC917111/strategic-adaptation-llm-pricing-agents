"""Replot published reference prices and SI without model calls."""

import argparse
import csv
import math
from pathlib import Path

import matplotlib

matplotlib.use('Agg')
import matplotlib.pyplot as plt


ROOT = Path(__file__).resolve().parents[1]
MODES = ('passive', 'revision', 'veto')
TITLES = ('Passive', 'Revision', 'Veto / replacement')
COLORS = ('#1f77b4', '#ff7f0e', '#2ca02c')
NASH = 1.473
MONOPOLY_REFERENCE = 1.802


def read_csv(path):
    with path.open(newline='', encoding='utf-8') as handle:
        return list(csv.DictReader(handle))


def main():
    parser = argparse.ArgumentParser(description=__doc__)
    parser.add_argument('--output', type=Path, required=True)
    args = parser.parse_args()
    records = read_csv(ROOT / 'results/gemini37-price-trajectories.csv')
    summaries = read_csv(ROOT / 'results/gemini37-reference-summary.csv')
    args.output.mkdir(parents=True, exist_ok=True)
    fig, axes = plt.subplots(2, 3, figsize=(15, 8), sharey=True, layout='constrained')
    si_fig, si_axes = plt.subplots(1, 2, figsize=(9, 4), sharey=True, layout='constrained')
    for seed in (0, 1):
        indices = []
        for column, (mode, title, color) in enumerate(zip(MODES, TITLES, COLORS)):
            summary = next(r for r in summaries if int(r['seed']) == seed and r['mode'] == mode)
            n = int(summary['rounds'])
            cell = [r for r in records if int(r['seed']) == seed and r['mode'] == mode]
            values = {(int(r['round']), int(r['firm_id'])): float(r['executed_price']) for r in cell}
            expected = {(t, i) for t in range(1, n + 1) for i in (0, 1)}
            if len(cell) != 2 * n or set(values) != expected:
                raise ValueError(f'Incomplete or duplicate price records: {seed}, {mode}')
            t = list(range(1, n + 1))
            firm_prices = [[values[(r, i)] for r in t] for i in (0, 1)]
            means = [(a + b) / 2 for a, b in zip(*firm_prices)]
            late = math.fsum(means[-20:]) / 20
            si = (late - NASH) / (MONOPOLY_REFERENCE - NASH)
            if not math.isclose(late, float(summary['late_window_mean_price']), abs_tol=1e-10):
                raise ValueError(f'Final-window mean differs: {seed}, {mode}')
            if not math.isclose(si, float(summary['supracompetitive_index']), abs_tol=1e-9):
                raise ValueError(f'SI differs: {seed}, {mode}')
            indices.append(si)
            ax = axes[seed, column]
            for i, style in enumerate(('--', ':')):
                ax.plot(t, firm_prices[i], style, color=color, alpha=.4, label=f'Firm {i}')
            ax.plot(t, means, color=color, linewidth=2.4, label='Two-firm mean')
            ax.axvline(10, color='gray', linestyle=':', linewidth=1)
            ax.axhline(NASH, color='dimgray', linestyle='--', linewidth=1)
            ax.axhline(MONOPOLY_REFERENCE, color='gray', linestyle='-.', linewidth=1)
            ax.set(title=f'Seed {seed}: {title}', xlabel='Round', xlim=(1, n))
            ax.grid(axis='y', alpha=.2)
            if column == 0:
                ax.set_ylabel('Executed price')
            if (seed, column) == (0, 2):
                ax.legend(frameon=False)
        bars = si_axes[seed].bar(TITLES, indices, color=COLORS)
        si_axes[seed].bar_label(bars, fmt='%.3f', padding=4)
        si_axes[seed].set(title=f'Seed {seed}', ylim=(0, 1.08))
        si_axes[seed].axhline(1, color='gray', linestyle='--', linewidth=1)
    si_axes[0].set_ylabel('Final-20 supracompetitive index')
    fig.suptitle('Gemini 3.7 Flash high: recorded executed-price trajectories')
    si_fig.suptitle('SI = (final-20 mean price − 1.473) / (1.802 − 1.473)')
    for chart, name in ((fig, 'price_trajectories_seed0_seed1.png'),
                        (si_fig, 'supracompetitive_index_seed0_seed1.png')):
        target = args.output / name
        if target.resolve() == (ROOT / 'results/figures' / name).resolve():
            raise ValueError('Choose a separate output directory to preserve the original report figures.')
        chart.savefig(target, dpi=180)
        plt.close(chart)
        print(target)


if __name__ == '__main__':
    main()
