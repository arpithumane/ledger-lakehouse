# Databricks notebook source
# /// script
# [tool.databricks.environment]
# environment_version = "6"
# dependencies = [
#   "pyyaml==6.0.2",
# ]
# ///
# MAGIC %md
# MAGIC # 06 - Rule-driven data quality and reconciliation
# MAGIC **Ab Initio mapping:** a generic graph driven by a parameter set. The rules live in
# MAGIC `rules/dq_rules.yml`, and this notebook only runs them. Quarantine is the reject port plus a reason.
# MAGIC
# MAGIC Run this from a Databricks Git folder so it can find the rules file and the `src` module.

# COMMAND ----------

# MAGIC %pip install pyyaml==6.0.2

# COMMAND ----------

import os
import sys

sys.path.append(os.path.abspath("../src"))

from dq_framework import load_config, run_reconciliation, run_rules

config = load_config("../rules/dq_rules.yml")
print(f"Loaded {len(config['rules'])} rules and {len(config['reconciliation'])} reconciliation checks")

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 1 - Run the rules and write the quarantine table
# MAGIC Overwrite keeps this simple. Production would append with a run ID, to keep a history across runs.

# COMMAND ----------

quarantine = run_rules(spark, config["rules"])
quarantine.write.mode("overwrite").format("delta").saveAsTable(config["quarantine_table"])

display(spark.sql(f"""
  SELECT rule_id, count(*) AS failures
  FROM {config['quarantine_table']}
  GROUP BY rule_id
  ORDER BY rule_id
"""))



# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 2 - Run the reconciliation report

# COMMAND ----------

report = run_reconciliation(spark, config["reconciliation"])
report.write.mode("overwrite").format("delta").saveAsTable(config["report_table"])

display(spark.table(config["report_table"]))

# COMMAND ----------

# MAGIC %md
# MAGIC ## Step 3 - Export the quarantine for the local answer-key check
# MAGIC Use the download option on this result to save it as a CSV on your Mac.
# MAGIC The answer key stays out of Databricks, so the comparison runs locally.

# COMMAND ----------

display(spark.sql(f"SELECT rule_id, record_key FROM {config['quarantine_table']}"))