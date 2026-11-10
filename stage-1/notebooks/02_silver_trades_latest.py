# Databricks notebook source
# /// script
# [tool.databricks.environment]
# environment_version = "6"
# ///
# MAGIC %md
# MAGIC # 02 - Silver trades latest: one row per trade, showing its current state
# MAGIC **Ab Initio mapping:** Sort on trade_id + trade_ts descending -> Dedup Sorted keeping the first row.
# MAGIC
# MAGIC `silver.trades` keeps every event (the history). `silver.trades_latest` answers
# MAGIC "what is this trade now?". Cancelled trades stay in the table, marked CANCEL.

# COMMAND ----------

from pyspark.sql import Window, functions as F

SILVER = "workspace.silver"

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 1 - Number each trade's events, newest first
# MAGIC A window works like a key-partitioned, sorted flow: the numbering restarts for each `trade_id`.
# MAGIC Unlike a rollup, it keeps every row and adds a column.

# COMMAND ----------

newest_first = Window.partitionBy("trade_id").orderBy(F.col("trade_ts").desc())

numbered_trades = spark.table(f"{SILVER}.trades").withColumn(
    "event_rank", F.row_number().over(newest_first)
)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 2 - Keep only the newest event for each trade

# COMMAND ----------

latest_trades = numbered_trades.filter(F.col("event_rank") == 1).drop("event_rank")

latest_trades.write.mode("overwrite").format("delta").saveAsTable(f"{SILVER}.trades_latest")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 3 - Check the result

# COMMAND ----------

display(spark.sql(f"""
  SELECT
    count(*)                 AS total_rows,
    count(DISTINCT trade_id) AS distinct_trades,
    count_if(status = 'NEW')    AS new_trades,
    count_if(status = 'AMEND')  AS amended_trades,
    count_if(status = 'CANCEL') AS cancelled_trades
  FROM {SILVER}.trades_latest
"""))