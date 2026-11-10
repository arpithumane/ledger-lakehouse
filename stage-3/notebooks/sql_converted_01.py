# Databricks notebook source
# MAGIC %md
# MAGIC ### Migration: Postgres query on `employee_historic` -> PySpark
# MAGIC Aggregates salary per employee and department for ACTIVE records only.

# COMMAND ----------

from pyspark.sql import functions as F

# COMMAND ----------

# Configuration
SOURCE_TABLE = "employee_historic"   # Adjust to catalog.schema.table if using Unity Catalog
STATUS_FILTER = "ACTIVE"

# COMMAND ----------

# Read source table
employee_historic_df = spark.table(SOURCE_TABLE)

# COMMAND ----------

# Filter, aggregate (equivalent of WHERE + GROUP BY + SUM)
result_df = (
    employee_historic_df
    .filter(F.col("status") == STATUS_FILTER)
    .groupBy("employee_id", "department_id")
    .agg(F.sum("salary").alias("total_salary"))
)

# COMMAND ----------

# Preview results
display(result_df)

# COMMAND ----------

# Optional: persist results
# result_df.write.format("delta").mode("overwrite").saveAsTable("employee_salary_summary")