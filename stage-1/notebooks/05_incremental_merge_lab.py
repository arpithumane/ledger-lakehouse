# Databricks notebook source
# /// script
# [tool.databricks.environment]
# environment_version = "6"
# ///
# MAGIC %md
# MAGIC # 05 - Incremental load with MERGE (lab)
# MAGIC **Ab Initio mapping:** Join the new batch to the target on the key, then send matched records
# MAGIC to an update flow and unmatched records to an insert flow. `MERGE` does all of that in one atomic statement.
# MAGIC
# MAGIC This lab replays your 3 daily files as 3 separate batches into its own table,
# MAGIC `silver.trades_incremental`. It does not touch `silver.trades`.

# COMMAND ----------

from pyspark.sql import functions as F

CATALOG = "workspace"
BRONZE = f"{CATALOG}.bronze"
SILVER = f"{CATALOG}.silver"
TARGET = f"{SILVER}.trades_incremental"

EVENT_KEY = ["trade_id", "trade_ts", "status"]

# Start the lab from an empty table. This drops only the lab table.
spark.sql(f"DROP TABLE IF EXISTS {TARGET}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 1 - Prepare one day's batch
# MAGIC Dedupe the batch first. A true duplicate inside one batch would otherwise be inserted twice,
# MAGIC because neither copy exists in the target yet.

# COMMAND ----------

def prepare_batch(day: str):
    return (
        spark.table(f"{BRONZE}.trades_raw")
        .filter(F.col("_source_file").contains(f"trades_{day}"))
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
            "source_system",
            "_source_file",
            "_ingest_ts",
        )
        .dropDuplicates(EVENT_KEY)
    )

# Create the empty target with the same columns as a batch.
prepare_batch("20261102").limit(0).write.format("delta").saveAsTable(TARGET)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 2 - The MERGE
# MAGIC - **Key (`ON`):** one event, the same key used for the dedupe. `<=>` also treats two NULLs as equal.
# MAGIC - **Matched and changed:** update the row.
# MAGIC - **Not matched:** insert the row.
# MAGIC - **Matched and unchanged:** do nothing, so rerunning a batch changes nothing.

# COMMAND ----------

def merge_batch(batch):
    batch.createOrReplaceTempView("batch")
    return spark.sql(f"""
        MERGE INTO {TARGET} AS t
        USING batch AS s
          ON  t.trade_id = s.trade_id
          AND t.trade_ts = s.trade_ts
          AND t.status   = s.status
        WHEN MATCHED AND NOT (
                t.counterparty_id <=> s.counterparty_id
            AND t.quantity        <=> s.quantity
            AND t.price           <=> s.price
            AND t.currency        <=> s.currency
        ) THEN UPDATE SET *
        WHEN NOT MATCHED THEN INSERT *
    """)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 3 - Load the three days, one at a time
# MAGIC Each output shows how many rows were inserted and updated.

# COMMAND ----------

display(merge_batch(prepare_batch("20261102")))

# COMMAND ----------

display(merge_batch(prepare_batch("20261103")))

# COMMAND ----------

display(merge_batch(prepare_batch("20261104")))

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 4 - Rerun the last day
# MAGIC Predict the inserted and updated counts before running this cell.

# COMMAND ----------

display(merge_batch(prepare_batch("20261104")))

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 5 - Apply a correction from the source
# MAGIC This simulates a resend that fills in one missing counterparty.

# COMMAND ----------

correction = (
    spark.table(TARGET)
    .filter(F.col("counterparty_id").isNull())
    .limit(1)
    .withColumn("counterparty_id", F.lit("C0001"))
)

display(merge_batch(correction))

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 6 - Check the final table and its history
# MAGIC `DESCRIBE HISTORY` lists each write as a version. That's Delta's transaction log.

# COMMAND ----------

display(spark.sql(f"""
  SELECT
    count(*)                          AS total_rows,
    count(DISTINCT trade_id)          AS distinct_trades,
    count_if(counterparty_id IS NULL) AS null_counterparty
  FROM {TARGET}
"""))

# COMMAND ----------

display(spark.sql(f"""
  SELECT version, operation, operationMetrics.numTargetRowsInserted AS inserted,
         operationMetrics.numTargetRowsUpdated AS updated
  FROM (DESCRIBE HISTORY {TARGET})
  ORDER BY version
"""))