# Reference experiment data

These files describe the completed stationary experiment with the recorded model identifier `gemini-3.7-flash`, requested high thinking, two seeds, and passive/revision/veto oversight. See [the protocol and results](../docs/reference-experiment.md) for the setting and interpretation.

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

The report bundle contains the combined text/price CSV, two detailed summary JSON files, and the figures. Original `rounds.jsonl` and per-call manifests were not part of the bundle used here. API transport is therefore disclosed from the historical documentation, not newly verified from provider receipts. The relay's upstream identity and equivalence to direct Google calls remain unverified. New runs use the official Google API.

Full prompt/provider traces, credentials, and the remaining 500 text records are excluded from this release. The source hashes allow later comparison with the retained report files; hashes alone do not establish API provenance. `private notes` refers to what the rival and regulator could observe during the simulation, not a claim that these published records are confidential personal data.

## Reproduction

Run `python experiments/plot_reference_results.py --output /tmp/gemini37-figures` from the repository root after installing the `plots` extra. This uses only the published price and summary CSV files and makes no API calls. Original PNGs are retained unchanged; reproduced figure styling may differ.
