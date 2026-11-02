# Project 07 — Serverless Data Lake and Analytics Pipeline

**Architecture:** Data engineering / analytics  
**Goal:** Ingest retail transactions, curate them into analytics-ready Parquet datasets, query with Athena, and visualize KPIs in QuickSight.

## Target architecture

~~~mermaid
flowchart LR
    Source[Retail events] --> FH[Kinesis Data Firehose]
    FH --> Raw[S3 raw zone]
    Raw --> Crawler[Glue crawler]
    Crawler --> Catalog[Glue Data Catalog]
    Raw --> ETL[Glue ETL job]
    Catalog --> ETL
    ETL --> Curated[S3 curated Parquet]
    Curated --> Agg[S3 aggregated zone]
    Catalog --> Athena[Athena]
    Athena --> QS[QuickSight dashboard]
    LF[Lake Formation] -. access control .-> Catalog
    LF -. access control .-> Curated
    EB[EventBridge Scheduler] --> ETL
~~~

## Phase 1 — Data contract and zones

1. Define a retail event schema: order ID, event time, store ID, product ID, quantity, price, and status.
2. Generate synthetic data only; do not use customer data.
3. Create separate S3 prefixes or buckets for raw, curated, and aggregated data.
4. Define partition strategy, such as year/month/day, based on query patterns.
5. Enable encryption, Block Public Access, lifecycle rules, and retention.
6. Define data-quality checks: required columns, valid timestamps, positive quantities, and accepted status values.

## Phase 2 — Firehose ingestion

1. Create a delivery stream with an S3 destination.
2. Configure buffering, compression, error output prefix, and logging.
3. Send synthetic retail JSON events using a producer script.
4. Verify raw objects arrive in the expected prefix.
5. Test malformed records and confirm they reach the error path.
6. Keep raw data immutable; add inline transformation only when needed.

## Phase 3 — Glue Catalog

1. Create a Glue database.
2. Create a crawler with least-privilege S3 and Glue permissions.
3. Run the crawler against the raw prefix.
4. Review inferred schema and partition/table settings.
5. Query a small sample from Athena.
6. Keep crawler permissions limited to the relevant data lake paths.

## Phase 4 — Glue ETL

1. Create a Glue ETL job using a supported Spark runtime.
2. Read source JSON using the Data Catalog or an explicit schema.
3. Validate and normalize data types.
4. Remove or quarantine invalid rows.
5. Convert curated output to Parquet with compression.
6. Write partitioned output to the curated zone.
7. Add data-quality summary and job metrics.
8. Make reruns safe and prevent silent duplicate records.

## Phase 5 — Athena

1. Create an Athena workgroup with enforced query result location and encryption.
2. Set a data-scan limit for the lab.
3. Query only required columns and filter on partitions.
4. Compare scanned bytes for partitioned and unpartitioned queries.
5. Create views or aggregated tables for common KPIs.
6. Keep query results in a separate controlled S3 prefix.

## Phase 6 — Lake Formation and KMS

1. Register relevant S3 locations with Lake Formation using the documented role model.
2. Configure database/table permissions for analyst and administrator roles.
3. Apply column-level or row-level filters to a sample dataset.
4. Use KMS keys according to the required encryption boundary.
5. Test that an analyst can query permitted fields but cannot read restricted data.
6. Document IAM, S3 bucket policy, Glue Catalog permission, and Lake Formation grant interactions.

## Phase 7 — Schedule and visualize

1. Create EventBridge Scheduler schedule for the ETL job or orchestration workflow.
2. Use a dedicated role that can start only the intended job.
3. Connect QuickSight to Athena using approved data access configuration.
4. Build dashboard with revenue, order count, average order value, and daily trend.
5. Configure SPICE refresh and row-level security only when needed.
6. Validate that viewers see only authorized data.

## Validation checklist

- Firehose delivers raw records to S3.
- Glue crawler discovers expected schema.
- ETL converts JSON to partitioned Parquet.
- Invalid records are identified and quarantined.
- Athena partition filters reduce bytes scanned.
- Lake Formation denies unauthorized access.
- EventBridge starts scheduled jobs.
- QuickSight visualizes expected KPIs with correct access scope.

## Cost and cleanup

Firehose ingestion, Glue runtime, Athena scanned bytes, S3 storage/requests, and QuickSight users/SPICE can incur charges. Use small synthetic datasets and short ETL runs. Delete schedules, QuickSight assets/data sources, Glue jobs/crawlers/catalog objects, Firehose stream, and S3 objects/buckets after validation.

## Definition of done

The pipeline is repeatable from raw ingestion to dashboard, uses Parquet and partitions effectively, enforces data governance, and records data-quality and cost measurements.
