# Run the pricing experiments

The repository runs the stationary-market baseline specified in `gemini37-reference-design.json`: two sellers interact repeatedly while demand parameters, market size, and marginal cost remain fixed. This establishes their pricing behavior before demand expansion or contraction is introduced.

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
- Google Gen AI `GenerateContent`;
- paper-order structured JSON;
- a fixed regulatory benchmark of 1.473; and
- convergence checks from round 40 through a maximum of 100 rounds.

Repeat the command for `passive`, `revision`, and `veto`, and use independent seeds. `--model` and `--thinking-level` allow an explicit model selection. Verify that the requested model and thinking level are supported by your Google account. A different model is a new experiment, not an exact reproduction of the recorded cells.

The stationary reference runner uses the official Google API. The historical data include a third-party route, recorded in [the provenance table](../docs/reference-experiment.md#7-model-and-api-provenance). Those historical records are retained with their original provenance.

`clients.py` defines the common interface and an offline scripted test client. `gemini_client.py` implements the actual Google call. The experiment runner builds the agents, carries their history and notes forward, and saves each completed round.

## Stationary outputs

Each run directory contains:

- `manifest.json`: fixed configuration, progress, and stopping reason;
- `rounds.jsonl`: proposals, text fields, flags, executed prices, market outcomes, and call metadata.

The published [result files](../results/README.md) contain 520 price records, six cell summaries, two figures, and 20 text examples. Full provider traces and the remaining text records are not included.

## Arm2: deterministic demand cycles

The [dynamic-market design](../docs/arm2-cycle.md) keeps the same three oversight modes and changes market size along a deterministic 40-round sine cycle. Each of five runs per mode lasts exactly 80 rounds. The parameters are also recorded in [arm2-cycle-design.json](arm2-cycle-design.json).

The Arm2 runner uses a configurable OpenAI-compatible chat-completions endpoint. It has no built-in provider address or credential. Set an endpoint and key for a service you are authorized to use; requests can incur charges. The requested model identifier must be available through that service.

```bash
python -m pip install -e '.[compatible,test]'
export GEMINI_OPENAI_COMPATIBLE_BASE_URL='https://your-provider.example/v1'
export GEMINI_OPENAI_COMPATIBLE_API_KEY='your-key'
python -m pricing_experiment.run_cycle_oversight \
  --output experiments/results/arm2_cycle \
  --modes passive revision veto \
  --seeds 0 1 2 3 4 \
  --model gemini-3.7-flash \
  --temperature 1.2 \
  --thinking-level high
```

This launches 15 independent markets, with at most six simultaneous model requests. Each market progresses sequentially through its rounds; the two firms make initial proposals concurrently from the same completed history. Revision calls occur only when the original regulator requires them. The default delay between rounds is 15 seconds. No convergence-based early stopping is used.

Use a new output directory for a new experiment. To resume an interrupted suite, repeat the same command with `--resume`. Completed cells are skipped; saved settings and source hashes must match. To run only missing oversight modes in a separate directory, select `--modes revision veto`. The older `run_cycle_experiment` entry point is retained for the initial passive batch; the multi-mode runner is the entry point for the complete design.

The directory contains `suite.json`, `market-path.csv`, a source snapshot under `code/src`, and a subdirectory for every `seedN/mode`. Each cell saves its configuration and progress in `manifest.json`, complete market rounds in `rounds.jsonl`, and request/response evidence in `api-receipts.jsonl`. API keys and authorization headers are excluded. These raw logs include full experimental prompts and generated text and should be reviewed before public release.

`cycle.py` defines the demand path. `cycle_prompts.py` preserves the historical experiment's prompt wording and revision request. `openai_compatible_client.py` handles the configured API route, while `run_cycle_oversight.py` handles parallel execution, recovery, and recording. The stationary runner and its existing result files are unchanged.

## Recreate the figures without API calls

From the repository root:

```bash
python -m pip install -e '.[plots]'
python experiments/plot_reference_results.py --output /tmp/gemini37-figures
```

This reads the published CSV files and checks that their final-window means agree. It writes a six-panel price trajectory plot and an SI comparison. The checked-in PNGs are the original report figures, so the regenerated styling may differ.

For the published Arm2 passive data, run:

```bash
python experiments/plot_cycle_results.py --output /tmp/arm2-figures
```

This produces the five individual trajectories and a five-run aggregate using non-overlapping five-round blocks. See [the data guide](../results/README.md#arm2-dynamic-market-data) for the release scope, text selection, and sample-SD definition.

## Offline verification

```bash
python -m pytest -q
```
