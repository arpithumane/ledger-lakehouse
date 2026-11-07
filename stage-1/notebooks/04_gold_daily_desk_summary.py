# Databricks notebook source
# MAGIC %md
# MAGIC # 04 - Gold daily desk summary: live trades by day, desk, asset class and currency
# MAGIC **Ab Initio mapping:** Filter by Expression -> Join to a lookup -> Rollup -> output table.
# MAGIC
# MAGIC **Known limitation until Phase 2:** bad rows from Silver still reach this table, so you will
# MAGIC see an `XXX` currency group and some negative quantities reducing the notional.

# COMMAND ----------

from pyspark.sql import functions as F

CATALOG = "workspace"
BRONZE = f"{CATALOG}.bronze"
SILVER = f"{CATALOG}.silver"
GOLD = f"{CATALOG}.gold"

spark.sql(f"CREATE SCHEMA IF NOT EXISTS {GOLD}")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 1 - Keep live trades only (Filter by Expression)

# COMMAND ----------

live_trades = spark.table(f"{SILVER}.trades_latest").filter(F.col("status") != "CANCEL")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 2 - Add the asset class (Join)
# MAGIC `instrument_id` is unique in the instruments table, so this join cannot multiply rows.
# MAGIC A left join keeps a trade with an unknown instrument, showing a NULL asset class.

# COMMAND ----------

instruments = spark.table(f"{BRONZE}.instruments_raw").select("instrument_id", "asset_class")

enriched_trades = live_trades.join(instruments, on="instrument_id", how="left")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 3 - Summarise (Rollup)
# MAGIC The `groupBy` columns are the rollup key. Each `agg` line is one output field.

# COMMAND ----------

notional = F.col("quantity") * F.col("price")

daily_summary = (
    enriched_trades
    .withColumn("trade_date", F.to_date("trade_ts"))
    .groupBy("trade_date", "desk", "asset_class", "currency")
    .agg(
        F.count("*").alias("trade_count"),
        F.round(F.sum(F.when(F.col("side") == "BUY", notional).otherwise(0)), 2).alias("buy_notional"),
        F.round(F.sum(F.when(F.col("side") == "SELL", notional).otherwise(0)), 2).alias("sell_notional"),
    )
)

daily_summary.write.mode("overwrite").format("delta").saveAsTable(f"{GOLD}.daily_desk_summary")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 4 - Check the result, one row per currency

# COMMAND ----------

display(spark.sql(f"""
  SELECT
    currency,
    sum(trade_count)   AS trades,
    sum(buy_notional)  AS buy_notional,
    sum(sell_notional) AS sell_notional
  FROM {GOLD}.daily_desk_summary
  GROUP BY currency
  ORDER BY currency
"""))
