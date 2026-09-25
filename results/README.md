# Published experiment data

## Stationary-market baseline data

The complete baseline contains five runs per mode (0–4), fifteen cells, 665 market rounds, and 1,330 firm-round records. The recorded model identifier is `gemini-3.7-flash`, with high thinking. Demand parameters, market size, marginal cost, and the oversight/stopping rules are fixed across the expanded set. See [the protocol and results](../docs/reference-experiment.md).

| File | Contents |
|---|---|
| [Full price trajectories](stationary-five-run/price-trajectories.csv) | All 1,330 firm-round records, including proposed/executed prices, quantities, profits, and flags |
| [Run summaries](stationary-five-run/run-summary.csv) | Fifteen cells: horizon, final-20 price, SI, and flag/intervention counts |
| [Five-round aggregates](stationary-five-run/five-round-aggregate.csv) | Trailing five-round averages per run, then mean and sample SD across five runs |
| [Individual trajectories](stationary-five-run/individual-trajectories.png) | Five rows by three modes, retaining complete 40–55-round horizons |
| [Aggregate figure](stationary-five-run/five-run-aggregate.png) | Three mode panels, mean and mean ± one sample SD on the common interval |
| [Provenance](stationary-five-run/provenance.json) | Original raw-log/manifest hashes, record counts, aggregation rule, and movement counts |

The aggregate uses rounds 1–40 and begins at round 5 so every point has a full trailing window. There is no endpoint padding. The SD uses the five run-level means (`ddof=1`), rather than treating the two interacting firms as independent observations. These historical batches are pooled descriptively; SD is not a confidence interval. Final-window summaries instead retain each run's own final twenty rounds.

To regenerate the figures without API calls:

```bash
python experiments/plot_stationary_results.py --output /tmp/stationary-five-run
```

`experiments/export_stationary_results.py` accepts the three original archive locations through `--seed0-root`, `--seed1-root`, and `--seed234-root`, validates the raw records, and rebuilds the four public numerical/provenance files. Original provider receipts and full agent text are excluded.

## Original two-run archive

The following files cover only runs 0 and 1. Numerical values and model-generated text are retained from the earlier release; API labels use generic interface names. Its twenty text examples are not a five-run text sample.

| File | Contents |
|---|---|
| [gemini37-reference-summary.csv](gemini37-reference-summary.csv) | Six run summaries, including final-20 prices, SI, flag counts, and recorded API transport |
| [gemini37-price-trajectories.csv](gemini37-price-trajectories.csv) | All 520 firm-round price records from the combined report CSV |
| [gemini37-text-examples.csv](gemini37-text-examples.csv) | 12 final-round records and all 8 revision records, including public justification and private notes |
| [Price trajectories](figures/price_trajectories_seed0_seed1.png) | Original six-panel report figure |
| [Supracompetitive indices](figures/supracompetitive_index_seed0_seed1.png) | Original report's final-window SI comparison |
| [data-provenance.json](data-provenance.json) | Source filenames and hashes, selection rule, and validation counts |

## Fields and selection

`seed` and `mode` identify a run. `round` starts at 1; `firm_id` is 0 or 1. `proposal_price` is the first model proposal. `executed_price` is the price used by the market after any oversight. Prices retain the source CSV's precision.

In the text table, `selection_reason` is `terminal` or `revision`. `proposal_*` fields contain the first call's text. `final_*` fields contain the text retained for the next round, after revision when applicable. `used_competitor_info` is the recorded final self-report, not an independently verified measure. `source_csv_record` is the one-based data-record position, excluding the header, in the combined report CSV; it is not a physical line number because CSV fields may contain newlines.

The selection is retrospective: both firms' last records in all six runs plus every record with a revision note. No text was selected by keyword, and the excerpts are not a random or preregistered sample. The selected fields are copied verbatim with no translation or strategy labels. No selection overlap occurs in these data, giving 20 distinct records.

## Scope and provenance

The 520 records represent 260 market rounds across six runs, with 40/40/40 rounds for seed 0 and 40/55/45 for seed 1 (passive/revision/veto). The price table includes every round present in the combined report. Its six final-20 mean prices and SI values reconcile with the published summary.

The original two-run release was built from a report bundle containing the combined text/price CSV, two detailed summary JSON files, and the figures. The expanded five-run release was subsequently checked against the original round logs and completion manifests. Historical API labels describe the recorded interface; they are not an independent verification of the upstream model.

Full prompt/provider traces, credentials, and the remaining 500 text records are excluded from this release. The source hashes allow later comparison with the retained report files; hashes alone do not establish API provenance. `private notes` refers to what the rival and regulator could observe during the simulation, not a claim that these published records are confidential personal data.

## Reproduction

Run `python experiments/plot_reference_results.py --output /tmp/gemini37-figures` from the repository root after installing the `plots` extra. This uses only the published price and summary CSV files and makes no API calls. Original PNGs are retained unchanged; reproduced figure styling may differ.

## Arm2 dynamic-market data

The files in `arm2-cycle/` cover five **passive** runs of the deterministic demand cycle, each lasting 80 rounds. The implementation supports all three oversight modes, but revision/veto result records are not included here. See [the Arm2 setting and source-version notes](../docs/arm2-cycle.md).

| File | Contents |
|---|---|
| [price-trajectories.csv](arm2-cycle/price-trajectories.csv) | All 800 firm-round records, including prices, market size, quantities, profits, and flags |
| [run-summary.csv](arm2-cycle/run-summary.csv) | Five run summaries |
| [five-round-aggregate.csv](arm2-cycle/five-round-aggregate.csv) | Sixteen non-overlapping five-round blocks; across-run mean and sample standard deviation |
| [text-examples.csv](arm2-cycle/text-examples.csv) | Fifty verbatim public justifications and private notes: both firms in every run at rounds 11, 31, 51, 71, and 80 |
| [provenance.json](arm2-cycle/provenance.json) | Historical source and raw-log hashes, requested API settings, and selection/aggregation rules |

Aggregation first averages the two firms within each run and five-round block, then computes the mean and sample SD across the five runs (`ddof=1`). Blocks are rounds 1–5, 6–10, and so on, not a sliding average. The SD describes between-run dispersion; it is not a confidence interval.

Text selection includes every peak, trough, and final-round record under this retrospective rule. Notes are generated experimental records, private to the firm during the simulation. Full API receipts, credentials, and local filesystem paths are excluded. Run labels correspond to requested seed identifiers; they do not establish provider-side reproducibility.

Rebuild the two passive figures without API calls:

```bash
python experiments/plot_cycle_results.py --output /tmp/arm2-figures
```

For holders of the original passive archive, `experiments/export_cycle_results.py --root /path/to/passive-archive --output /tmp/arm2-data` validates the records and rebuilds all five public files. This exporter accepts the original passive-batch layout, not the multi-mode runner's layout.
