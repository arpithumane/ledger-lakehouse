# Databricks notebook source
# MAGIC %md
# MAGIC # 01 - Silver trades: apply types and remove true duplicates
# MAGIC **Ab Initio mapping:** input table -> Reformat (apply the real DML) -> Dedup Sorted -> output table.
# MAGIC
# MAGIC **What this notebook does not do yet:** it keeps rows with bad business values (negative quantity,
# MAGIC `XXX` currency, missing counterparty). Phase 2 quarantines those with a reason.

# COMMAND ----------

from pyspark.sql import functions as F

CATALOG = "workspace"
BRONZE = f"{CATALOG}.bronze"
SILVER = f"{CATALOG}.silver"

spark.sql(f"CREATE SCHEMA IF NOT EXISTS {SILVER}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 1 - Apply types (Reformat)
# MAGIC `try_cast` returns NULL when a value cannot be converted, instead of failing the whole job.
# MAGIC Nothing runs yet: Spark only records the steps until an action such as `count` or a table write.

# COMMAND ----------

bronze_trades = spark.table(f"{BRONZE}.trades_raw")

typed_trades = bronze_trades.select(
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

typed_trades.printSchema()

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 2 - Remove true duplicates (Dedup Sorted)
# MAGIC The key is one *event*, not one trade: the same trade can have NEW, AMEND and CANCEL rows.
# MAGIC `trade_ts` is in the key so that two different amendments on one trade would both survive.

# COMMAND ----------

EVENT_KEY = ["trade_id", "trade_ts", "status"]

deduped_trades = typed_trades.dropDuplicates(EVENT_KEY)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 3 - Write the Silver table
# MAGIC Overwrite is fine for now. We switch to an incremental MERGE later in Phase 1.

# COMMAND ----------

deduped_trades.write.mode("overwrite").format("delta").saveAsTable(f"{SILVER}.trades")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 4 - Check the result

# COMMAND ----------

display(spark.sql(f"""
  SELECT
    count(*)                                    AS total_rows,
    count(DISTINCT trade_id)                    AS distinct_trades,
    count_if(trade_ts IS NULL)                  AS failed_ts_casts,
    count_if(quantity IS NULL)                  AS failed_quantity_casts,
    count_if(price IS NULL)                     AS failed_price_casts,
    count_if(quantity < 0)                      AS negative_quantity,
    count_if(currency = 'XXX')                  AS bad_currency,
    count_if(counterparty_id IS NULL)           AS null_counterparty
  FROM {SILVER}.trades
"""))
