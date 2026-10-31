# Automated Data Reconciliation Pipeline

## Purpose
Compare source and target order datasets by row count, business key (`order_id`), aggregate amount, and field values. Produce a JSON run report and separate CSV outputs for matches, field mismatches, missing/extra keys, and rejected records.

## Architecture
`CSV source + CSV target -> ingestion/schema validation -> record validation -> normalization/deduplication -> business-key and field reconciliation -> JSON/CSV reports + run log`

## Requirements
- Python 3.10+
- pandas
- pytest

## Windows setup (PowerShell)
```powershell
py -3.11 -m venv .venv
.\.venv\Scripts\Activate.ps1
python -m pip install --upgrade pip
pip install -r requirements.txt
python run.py
```
If PowerShell blocks activation, run `Set-ExecutionPolicy -Scope Process -ExecutionPolicy Bypass`, then activate again.

## Run
1. Keep `data/source.csv` and `data/target.csv` in place.
2. Run `python run.py`.
3. Review files in `output/`.
4. Run tests: `pytest -q`.
5. Generate a larger source file: `python generate_data.py --rows 100000 --output data/source.csv --seed 42`. Create a corresponding target file by copying and deliberately changing selected rows to test reconciliation.

## Data dictionary
| Column | Type | Rule |
|---|---|---|
| order_id | integer | Required, unique business key within each dataset |
| customer_id | integer | Required, positive reference identifier |
| product_name | string | Required, trimmed |
| quantity | integer | Required, greater than zero |
| amount | decimal | Required, non-negative |
| order_date | ISO date | Required, YYYY-MM-DD |

Grain: one row per order. `order_id` is the stable business key. The sample treats `customer_id` as a positive reference identifier; a full implementation should validate it against a customer master table.

## Output files
- `reconciliation_report.json`: run status, counts, aggregates, timing, input file names, run ID.
- `matched_records.csv`: exact field matches by order ID.
- `mismatched_records.csv`: common keys with one or more differing fields.
- `missing_in_target.csv`: valid source keys absent from target.
- `extra_in_target.csv`: valid target keys absent from source.
- `rejected_records.csv`: invalid records and duplicate business keys.
- `run_logs/<run_id>.log`: operational log.

## Rules and assumptions
- Source and target must have the same six-column schema. Unexpected or missing columns fail fast.
- Required values cannot be null/blank; IDs and quantity must be integers; amount cannot be negative; quantity must be positive; date must be a valid ISO date.
- Duplicate keys are quarantined after the first occurrence. The first row is retained deterministically based on input order.
- Amount comparison is exact after conversion to two decimal places. For currencies requiring tolerance, add a configured decimal tolerance.
- Late/out-of-order events are retained; this batch comparison does not impose event-time windows.
- This starter uses CSV files and local outputs; it does not connect to production databases or APIs.

## Idempotency, retries, and backfills
The pipeline does not append to a target table. It rewrites deterministic output filenames for each execution, so rerunning the same inputs does not create duplicate output records. Supply a fixed `run_id` when calling `run_pipeline` to overwrite that run's artifacts. On failure, inspect the JSON report and run log, correct the input/configuration, then rerun. For a backfill, place the historical source/target extracts in separate paths and call `run_pipeline` with those paths and a distinct run ID.

## Performance
The generator supports 100,000+ rows. The reconciliation uses hash sets for key membership and a single pass over shared keys; memory usage is proportional to input size. A next optimization for larger-than-memory data is to stage both datasets in a database and perform indexed joins/aggregations in SQL, or compare sorted chunks.

## Tests
Tests cover happy path, empty files, missing required values, negative amounts, duplicate keys, field mismatch, missing/extra keys, and rerun behavior. Run `pytest -q`.

## Design trade-offs / limitations
This is a deliberately small vertical slice. It uses pandas for clarity and fast local development, not distributed processing. The reference-key rule checks positive customer IDs but does not verify existence in a customer dimension. The pipeline reports aggregate differences alongside record-level differences; it does not attempt to auto-correct source or target data. Unexpected schema changes fail the run instead of silently adapting.
