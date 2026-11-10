# Databricks notebook source
# /// script
# [tool.databricks.environment]
# environment_version = "6"
# ///
# MAGIC %md
# MAGIC # 03 - Silver ledger entries: apply types and remove true duplicates
# MAGIC **Ab Initio mapping:** input table -> Reformat (apply the real DML) -> Dedup Sorted -> output table.
# MAGIC
# MAGIC Money uses `decimal`, not `double`, because a ledger has to balance to the cent.
# MAGIC Unbalanced and orphan journals stay in this table until Phase 2 quarantines them.

# COMMAND ----------

from pyspark.sql import functions as F

CATALOG = "workspace"
BRONZE = f"{CATALOG}.bronze"
SILVER = f"{CATALOG}.silver"

spark.sql(f"CREATE SCHEMA IF NOT EXISTS {SILVER}")

# COMMAND ----------

typed_entries = spark.table(f"{BRONZE}.ledger_entries_raw").select(
    "entry_id",
    "trade_id",
    F.expr("try_cast(journal_ts AS timestamp)").alias("journal_ts"),
    "account_id",
    F.expr("try_cast(debit AS decimal(18,2))").alias("debit"),
    F.expr("try_cast(credit AS decimal(18,2))").alias("credit"),
    "currency",
    "entry_type",
    "source_system",
    "_source_file",
    "_ingest_ts",
)

# COMMAND ----------

# entry_id identifies one ledger line. A trade has many lines, so trade_id cannot be the key.
deduped_entries = typed_entries.dropDuplicates(["entry_id"])

deduped_entries.write.mode("overwrite").format("delta").saveAsTable(f"{SILVER}.ledger_entries")

# COMMAND ----------

display(spark.sql(f"""
  SELECT
    count(*)                 AS total_rows,
    count(DISTINCT entry_id) AS distinct_entries,
    count(DISTINCT trade_id) AS distinct_trades,
    sum(debit)               AS total_debit,
    sum(credit)              AS total_credit,
    sum(debit) - sum(credit) AS difference
  FROM {SILVER}.ledger_entries
"""))