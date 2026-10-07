# Transaction Reporting Automation

A Python script that turns raw quarterly transaction data into a submission-ready CSV, replacing a manual process that took about 3 hours with one that runs end to end in roughly 15 minutes (the script itself runs in about 30 seconds).

## What it does

1. **Ingests** a raw transaction Excel file (300K+ rows)
2. **Filters** to a target year and quarter
3. **Filters** to a configurable list of states
4. **Maps** program administrators to broker details
5. **Builds** a formatted output dataset
6. **Validates** row counts and premium totals, including a state-by-state summary to reconcile against the source pull
7. **Exports** the final CSV

## Requirements

- Python 3.9+
- pandas
- openpyxl

```bash
pip install pandas openpyxl
```

## Configuration

Edit the settings at the top of `transaction_automation.py`:

| Setting | Description |
|---|---|
| `TRANSACTION_FILE` | Path to the source Excel file |
| `STATES` | List of state codes to include |
| `YEAR` / `QUARTER` | Reporting period to filter on |
| `BROKER_MAP` | Lookup of administrator name to broker number and name |

## Usage

```bash
python transaction_automation.py
```

The script prints row counts after each filter, the date range of the filtered data, and a premium summary by state. It then writes the output CSV to the working directory.

## Validation

Before submitting, compare the state-by-state premium totals and the overall total printed at the end of the run against the source validation pull. They should match.

## Notes

- Source data and output files are not included in this repo (see `.gitignore`). Broker details in the script are placeholders.
- Built with Python, pandas, and Jupyter.
