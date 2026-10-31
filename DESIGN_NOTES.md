# Design and trade-off note

- **Business key:** `order_id` defines one order row. It is checked for duplicates before reconciliation.
- **Grain:** one record per order. Amount is a row-level order total; aggregate is the sum of valid unique-order amounts.
- **Reject strategy:** invalid rows and duplicate-key rows are written to a quarantine CSV with source dataset and reason.
- **Determinism:** normalization trims product names, parses ISO dates, and rounds amounts to two decimals. Duplicate resolution retains the first input row.
- **Idempotency:** output artifacts are replaced, not appended. Reusing a run ID replaces the same run's artifacts.
- **Recovery:** failed runs emit a failure report and log; retry after correcting the issue. Backfills use distinct input paths and run IDs.
- **Trade-off:** pandas is simple and appropriate for a 0–3 year portfolio project and 100k-scale local demo. For multi-million or streaming workloads, use database staging, partitioning, and incremental reconciliation.
