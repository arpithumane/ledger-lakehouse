"""Rule-driven data quality and reconciliation. Rules live in YAML, so a new check needs no new code."""
from decimal import Decimal
from functools import reduce

import yaml
from pyspark.sql import functions as F

REPORT_SCHEMA = "check_name string, left_value string, right_value string, passed boolean"


def load_config(path):
    with open(path) as config_file:
        return yaml.safe_load(config_file)


def run_rule(spark, rule):
    """Return one row per failing record: rule_id, source_table, record_key."""
    if "query" in rule:
        failures = spark.sql(rule["query"])
    else:
        failures = (
            spark.table(rule["source"])
            .filter(F.expr(rule["failure_condition"]))
            .select(F.col(rule["key"]).alias("record_key"))
        )
    return failures.select(
        F.lit(rule["id"]).alias("rule_id"),
        F.lit(rule["source"]).alias("source_table"),
        F.col("record_key").cast("string").alias("record_key"),
    )


def run_rules(spark, rules):
    """Run every rule and combine the failures, like a generic graph driven by a parameter set."""
    results = [run_rule(spark, rule) for rule in rules]
    return reduce(lambda left, right: left.unionByName(right), results)


def scalar(spark, query):
    return spark.sql(query).first()[0]


def run_reconciliation(spark, checks):
    """Compare two single-value queries per check. Exact comparison, because a ledger balances to the cent."""
    rows = []
    for check in checks:
        left, right = scalar(spark, check["left"]), scalar(spark, check["right"])
        passed = left is not None and right is not None and Decimal(str(left)) == Decimal(str(right))
        rows.append((check["name"], str(left), str(right), passed))
    return spark.createDataFrame(rows, REPORT_SCHEMA)
