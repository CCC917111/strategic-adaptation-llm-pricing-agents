# Experiment Reproducibility Notes

## What is included

The repository contains the sanitized core implementation needed to inspect the market, prompt/state loop, Gemini structured-output call, oversight logic, persistence, and convergence criteria. Secret-bearing `.env` files, key-pool backups, virtual environments, raw provider logs, and large raw trajectories are intentionally excluded.

The compact result table in `results/preliminary-results.csv` was transcribed from 18 completed archived runs. It is provided for review, not as a substitute for publishing the raw trajectories after they have been checked for sensitive metadata.

## Environment variables

Copy `.env.example` to a local `.env` and supply your own key. Never commit `.env`.

```text
GEMINI_API_KEY=your_key_here
GEMINI_MODEL=gemini-3.7-flash
```

The completed exploratory runs used `gemini-3.5-flash-lite`; the intended next run uses `gemini-3.7-flash` with high thinking and no explicit temperature.

## Paper-main profile

```bash
python -m pricing_experiment.run_live \
  --paper-main \
  --provider gemini \
  --model gemini-3.7-flash \
  --thinking-level high \
  --mode passive \
  --rounds 100 \
  --seed 0 \
  --output experiments/results/paper_main_passive_seed0
```

Repeat with `--mode revision` and `--mode veto`. Provider quotas, retry policy, model availability, exact SDK version, timestamps, and the run manifest should be archived with every result.

## Next-method profile

The next experiment will add controlled regime transitions, randomized carry/reset/sanitize memory conditions, and pre-registered exogenous price probes. Those changes are not yet implemented in the uploaded baseline and are deliberately marked TBD rather than silently mixed into the preliminary results.
