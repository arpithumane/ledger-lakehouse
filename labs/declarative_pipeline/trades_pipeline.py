# Declarative Pipeline lab: bronze and Silver trades, with expectations.
#
# Ab Initio mapping: instead of drawing each step and wiring the order, you declare each table
# and what it reads from. The pipeline works out the order, the incremental loading and the retries.
#
# This file is a pipeline source file, not a notebook, so don't run it cell by cell.
# Attach it to a pipeline: target catalog `workspace`, target schema `pipeline_lab`.

import dlt
from pyspark.sql import functions as F

LANDING = "/Volumes/workspace/bronze/landing/trades/"


# Bronze: a streaming table, loaded with Auto Loader.
# Auto Loader remembers which files it has already read, so each run picks up only new files.
@dlt.table(comment="Raw trades from the landing volume, all strings, with audit columns.")
def trades_bronze():
    return (
        spark.readStream.format("cloudFiles")
        .option("cloudFiles.format", "csv")
        .option("header", "true")
        .load(LANDING)
        .withColumn("_source_file", F.col("_metadata.file_path"))
        .withColumn("_ingest_ts", F.current_timestamp())
    )


# Silver: typed and deduped, with expectations (data quality rules declared on the table).
#   expect          -> keep the failing row, but count it in the pipeline's metrics
#   expect_or_drop  -> remove the failing row, and count it
#   expect_or_fail  -> stop the whole update
@dlt.table(comment="Typed trade events with true duplicates removed.")
@dlt.expect("valid_counterparty", "counterparty_id IS NOT NULL")
@dlt.expect_or_drop("positive_quantity", "quantity > 0")
# YOUR TURN: add an expectation that drops rows whose currency isn't USD, EUR, GBP or JPY.
@dlt.expect_or_drop("valid_currency", "currency IS NOT NULL and currency IN ('USD', 'EUR', 'GBP', 'JPY')")
# Remember what you learned about NULLs in your own rules.
def trades_silver():
    return (
        dlt.read("trades_bronze")
        .select(
            "trade_id",
            F.expr("try_cast(trade_ts AS timestamp)").alias("trade_ts"),
            "desk",
            "instrument_id",
            "counterparty_id",
            "side",
            F.expr("try_cast(quantity AS int)").alias("quantity"),
            F.expr("try_cast(price AS decimal(18,4))").alias("price"),
            "currency",
            "status",
            "_source_file",
            "_ingest_ts",
        )
        .dropDuplicates(["trade_id", "trade_ts", "status"])
    )
