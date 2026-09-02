# Reproducing the Completed Experiments

The commands are grouped by the comparison they reproduce.

## Installation

```bash
python -m pip install -e '.[gemini]'
export GEMINI_API_KEY='your-key'
```

Never commit an `.env` file or API key.

## Static-market benchmark

The baseline design is in `paper-baseline-design.json`. One paper-order passive cell can be run with:

```bash
python -m pricing_experiment.run_paper_baseline \
  --mode passive \
  --response-order paper \
  --seed 0 \
  --output experiments/results/paper_baseline_passive_seed0
```

Repeat for `passive`, `revision`, and `veto`, and for seeds 0–2.

The defaults reproduce the completed archived implementation:

- `gemini-3.5-flash-lite`;
- Gemini Interactions API path;
- paper response order;
- static calibrated market;
- fixed regulatory benchmark `1.473`;
- 100 rounds; and
- no online early stopping.

This is intentionally labelled paper-based rather than exact. To use the later alignment corrections, add `--round-best-response --early-stop`; results from that corrected profile are not included as completed results in this repository.

## Response-schema diagnostic

Use the same runner and change only:

```bash
--response-order price-last
```

For example:

```bash
python -m pricing_experiment.run_paper_baseline \
  --mode passive \
  --response-order price-last \
  --seed 0 \
  --output experiments/results/response_order_passive_seed0_price_last
```

The combined 18-cell result table is `results/preliminary-results.csv`.

## Mature and expanding demand

The dynamic design is in `hidden-demand-design.json`. One expanding retail cell can be run with:

```bash
python -m pricing_experiment.run_live \
  --market expanding \
  --industry retail \
  --seed 0 \
  --output experiments/results/hidden_demand_retail_expanding_seed0
```

Repeat for both markets, both industry descriptions, and seeds 0–2.

These defaults match the completed dynamic experiment:

- `gemini-3.5-flash-lite`;
- Gemini `GenerateContent`;
- passive oversight;
- paper response order;
- maximum 100 rounds and minimum 60 rounds; and
- convergence checks every 5 rounds with a 20-round window.

## Included summaries

- `results/paper-baseline-summary.csv`: 9 paper-order baseline cells.
- `results/preliminary-results.csv`: the baseline plus 9 price-last extension cells.
- `results/hidden-demand-summary.csv`: 12 mature/expanding cells.

## Data-handling limit

The repository includes sanitized code, fixed design files, and compact summaries. Raw provider logs and text trajectories are not included until their metadata has been checked. The hidden-demand implementation has passed calibration and offline integration checks, but a fresh end-to-end API rerun has not yet been completed from this public package.
