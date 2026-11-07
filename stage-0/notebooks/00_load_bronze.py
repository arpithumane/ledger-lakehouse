# Databricks notebook source
# MAGIC %md
# MAGIC # 00 - Land raw files into Bronze Delta tables
# MAGIC **Ab Initio mapping:** landing volume = input file datasets; this notebook = a graph that reads
# MAGIC delimited files with an all-string DML and writes them untouched, plus audit columns.
# MAGIC **Rule of bronze:** keep everything as strings, fix nothing. Bad data must stay visible.

# COMMAND ----------

# Free Edition's default catalog is usually "workspace". Check in the Catalog sidebar and edit if different.
CATALOG = "workspace"
SCHEMA = "bronze"
VOLUME = "landing"
BASE = f"/Volumes/{CATALOG}/{SCHEMA}/{VOLUME}"

spark.sql(f"CREATE SCHEMA IF NOT EXISTS {CATALOG}.{SCHEMA}")
spark.sql(f"CREATE VOLUME IF NOT EXISTS {CATALOG}.{SCHEMA}.{VOLUME}")
print("Upload your CSV folders into:", BASE)

# COMMAND ----------

from pyspark.sql import functions as F

# folder inside the volume -> bronze table name
SOURCES = {
    "trades": "trades_raw",
    "ledger_entries": "ledger_entries_raw",
    "reference/instruments": "instruments_raw",
    "reference/counterparties": "counterparties_raw",
    "reference/gl_accounts": "gl_accounts_raw",
}

def load_bronze(folder: str, table: str):
    df = (spark.read.option("header", True)
          .option("inferSchema", False)          # everything stays a string
          .csv(f"{BASE}/{folder}/")
          .withColumn("_source_file", F.col("_metadata.file_path"))
          .withColumn("_ingest_ts", F.current_timestamp()))
    (df.write.mode("overwrite").format("delta")
       .saveAsTable(f"{CATALOG}.{SCHEMA}.{table}"))
    print(f"{table}: {df.count():,} rows")

for folder, table in SOURCES.items():
    load_bronze(folder, table)

# COMMAND ----------

# MAGIC %md
# MAGIC ## Sanity queries - run these and look at the results
# MAGIC Overwrite is fine for today. In Phase 1 we switch to incremental loads.

# COMMAND ----------

display(spark.sql(f"""
  SELECT status, count(*) AS n FROM {CATALOG}.{SCHEMA}.trades_raw GROUP BY status
"""))

# COMMAND ----------

# Duplicate trade rows (we planted some - can you find them?)
display(spark.sql(f"""
  SELECT trade_id, status, count(*) AS n
  FROM {CATALOG}.{SCHEMA}.trades_raw
  GROUP BY trade_id, status HAVING count(*) > 1
"""))

# COMMAND ----------

# Trades whose journal lines do not balance (debits != credits) - the heart of accounting DQ
display(spark.sql(f"""
  SELECT trade_id,
         round(sum(cast(debit AS double)) - sum(cast(credit AS double)), 2) AS imbalance
  FROM {CATALOG}.{SCHEMA}.ledger_entries_raw
  GROUP BY trade_id
  HAVING abs(sum(cast(debit AS double)) - sum(cast(credit AS double))) > 0.005
"""))
