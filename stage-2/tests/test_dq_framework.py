from pathlib import Path

from dq_framework import load_config, run_reconciliation, run_rule, run_rules

RULES_FILE = Path(__file__).parent.parent / "rules" / "dq_rules.yml"
EXPECTED_DEFECT_TYPES = {
    "DUPLICATE_TRADE",
    "NULL_COUNTERPARTY",
    "NEGATIVE_QTY",
    "BAD_CURRENCY",
    "UNBALANCED_JOURNAL",
    "ORPHAN_JOURNAL",
}


def make_trades_view(spark):
    rows = [("T1", 100), ("T2", -5), ("T3", 20)]
    spark.createDataFrame(rows, "trade_id string, quantity int").createOrReplaceTempView("test_trades")


NEGATIVE_RULE = {
    "id": "NEGATIVE_QTY",
    "source": "test_trades",
    "key": "trade_id",
    "failure_condition": "quantity < 0",
}
HIGH_RULE = {
    "id": "HIGH_QTY",
    "source": "test_trades",
    "query": "SELECT trade_id AS record_key FROM test_trades WHERE quantity >= 100",
}


def test_config_has_a_rule_for_every_planted_defect_type():
    config = load_config(RULES_FILE)
    assert EXPECTED_DEFECT_TYPES <= {rule["id"] for rule in config["rules"]}


def test_condition_rule_returns_only_failing_records(spark):
    make_trades_view(spark)
    rows = run_rule(spark, NEGATIVE_RULE).collect()
    assert [(r.rule_id, r.source_table, r.record_key) for r in rows] == [("NEGATIVE_QTY", "test_trades", "T2")]


def test_query_rule_returns_failing_records(spark):
    make_trades_view(spark)
    rows = run_rule(spark, HIGH_RULE).collect()
    assert [(r.rule_id, r.record_key) for r in rows] == [("HIGH_QTY", "T1")]


def test_run_rules_combines_failures_from_every_rule(spark):
    make_trades_view(spark)
    rows = run_rules(spark, [NEGATIVE_RULE, HIGH_RULE]).collect()
    assert {(r.rule_id, r.record_key) for r in rows} == {("NEGATIVE_QTY", "T2"), ("HIGH_QTY", "T1")}


def test_reconciliation_reports_pass_and_fail(spark):
    checks = [
        {"name": "same", "left": "SELECT 7806.44", "right": "SELECT 7806.44"},
        {"name": "one_cent_off", "left": "SELECT 7806.44", "right": "SELECT 7806.45"},
        {"name": "no_data", "left": "SELECT CAST(NULL AS int)", "right": "SELECT 1"},
    ]
    results = {row.check_name: row.passed for row in run_reconciliation(spark, checks).collect()}
    assert results == {"same": True, "one_cent_off": False, "no_data": False}
