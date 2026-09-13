# Run the Gemini 3.7 Flash reference experiment

The repository exposes one experiment: the stationary two-firm reference protocol in `gemini37-reference-design.json`.

## Install

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[gemini,test]'
```

Never commit an API key or populated `.env` file.

## Run through the official Google API

Obtain your own key through [Google AI Studio](https://aistudio.google.com/apikey) and use the API within Google's [available regions](https://ai.google.dev/gemini-api/docs/available-regions) and [terms](https://ai.google.dev/gemini-api/terms). Live runs consume your API quota and may incur charges. Set the key in your shell; the runner does not automatically load `.env` files.

```bash
export GEMINI_API_KEY='your-key'
python -m pricing_experiment.run_reference_experiment \
  --mode passive \
  --seed 0 \
  --output experiments/results/gemini37_passive_seed0
```

The reference defaults are:

- model `gemini-3.7-flash`;
- thinking level `high`;
- no explicit temperature;
- Google Gen AI `GenerateContent`;
- paper-order structured JSON;
- a fixed regulatory benchmark of 1.473; and
- convergence checks from round 40 through a maximum of 100 rounds.

Repeat the command for `passive`, `revision`, and `veto`, and use independent seeds. `--model` and `--thinking-level` allow an explicit model selection. Verify that the requested model and thinking level are supported by your Google account. A different model is a new experiment, not an exact reproduction of the recorded cells.

The public runner supports only the official Google API. The historical data include a third-party route, recorded in [the provenance table](../docs/reference-experiment.md#7-model-and-api-provenance). Those historical records are retained with their original provenance.

`clients.py` defines the common interface and an offline scripted test client. `gemini_client.py` implements the actual Google call. The experiment runner builds the agents, carries their history and notes forward, and saves each completed round.

## Outputs

Each run directory contains:

- `manifest.json`: fixed configuration, progress, and stopping reason;
- `rounds.jsonl`: proposals, text fields, flags, executed prices, market outcomes, and call metadata.

The published [result files](../results/README.md) contain 520 price records, six cell summaries, two figures, and 20 text examples. Full provider traces and the remaining text records are not included.

## Recreate the figures without API calls

From the repository root:

```bash
python -m pip install -e '.[plots]'
python experiments/plot_reference_results.py --output /tmp/gemini37-figures
```

This reads the published CSV files and checks that their final-window means agree. It writes a six-panel price trajectory plot and an SI comparison. The checked-in PNGs are the original report figures, so the regenerated styling may differ.

## Offline verification

```bash
python -m pytest -q
```
