# Run the Gemini 3.7 Flash reference experiment

The repository exposes one experiment: the stationary two-firm reference protocol in `gemini37-reference-design.json`.

## Install

```bash
python -m venv .venv
source .venv/bin/activate
python -m pip install -e '.[gemini,test]'
```

Never commit an API key or populated `.env` file.

## Official Google transport

```bash
export GEMINI_API_KEY='your-key'
python -m pricing_experiment.run_reference_experiment \
  --transport google \
  --mode passive \
  --seed 0 \
  --output experiments/results/gemini37_passive_seed0
```

The runner pins:

- model `gemini-3.7-flash`;
- thinking level `high`;
- no explicit temperature;
- Google Gen AI `GenerateContent`;
- paper-order structured JSON;
- a fixed regulatory benchmark of 1.473; and
- convergence checks from round 40 through a maximum of 100 rounds.

Repeat the command for `passive`, `revision`, and `veto`, and use independent seeds.

## OpenAI-compatible relay

The recorded runs used a YunZhuHub relay after Google capacity limits. The adapter is provider-neutral and requires an HTTPS base URL:

```bash
export GEMINI_OPENAI_COMPATIBLE_BASE_URL='https://your-relay.example/v1'
export GEMINI_OPENAI_COMPATIBLE_API_KEY='your-key'
python -m pricing_experiment.run_reference_experiment \
  --transport openai-compatible \
  --mode passive \
  --seed 0 \
  --output experiments/results/gemini37_passive_seed0_relay
```

Do not combine transports within a new run. The completed seed 0 passive cell did switch transport at round 13, so it is retained as descriptive validation rather than a clean replication cell.

## Outputs

Each run directory contains:

- `manifest.json`: fixed configuration, progress, and stopping reason;
- `rounds.jsonl`: proposals, text fields, flags, executed prices, market outcomes, and call metadata.

The repository includes only the sanitized six-cell summary at `results/gemini37-reference-summary.csv`. Raw provider traces and credentials are excluded.

## Offline verification

```bash
python -m pytest -q
```
