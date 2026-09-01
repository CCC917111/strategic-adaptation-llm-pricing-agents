# Reproducing the Current Experiment

## Included experiment

The current main experiment is the 12-cell hidden-demand comparison:

```text
2 markets (mature, expanding)
× 2 industry descriptions (retail, software)
× 3 seeds (0, 1, 2)
```

Every completed cell used `gemini-3.5-flash-lite`, passive oversight, paper response order, and the Gemini `GenerateContent` method. The fixed design values are in `hidden-demand-design.json`.

## Environment

Install the project and Gemini dependency, then set your own key in the process environment. Never commit an `.env` file.

```bash
python -m pip install -e '.[gemini]'
export GEMINI_API_KEY='your-key'
```

## Example run

```bash
python -m pricing_experiment.run_live \
  --market expanding \
  --industry retail \
  --seed 0 \
  --output experiments/results/hidden_demand_retail_expanding_seed0
```

Repeat for both markets, both industries, and seeds 0–2. The defaults match the completed experiment: maximum 100 rounds, minimum 60 rounds, convergence checks every 5 rounds with a 20-round window, and a 2-second delay between rounds.

The saved manifest records the requested model, API method, market treatment, scenario text, convergence configuration, and retry settings. API keys are never recorded.

## Data included here

- `results/hidden-demand-summary.csv`: the 12 cell-level summaries used in the README.
- `results/preliminary-results.csv`: an older response-order and oversight pilot, retained as a legacy record.

Raw provider logs and text trajectories are not included yet. They require a separate metadata and privacy check before publication.

## Known reproducibility limit

The completed trajectories were created before this public package contained the hidden-demand market implementation. The implementation has now been added and its calibration is tested, but a fresh end-to-end API rerun has not yet been completed with the public package. The current work is therefore a code-and-result audit, not a claim of independent reproduction.
