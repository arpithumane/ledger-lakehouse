from decimal import Decimal

from transforms import cast_trades, dedupe_events, latest_status, unbalanced_trades

TRADE_SCHEMA = "trade_id string, trade_ts string, status string, quantity string, price string"
LEDGER_SCHEMA = "trade_id string, debit decimal(18,2), credit decimal(18,2)"


def trade(trade_id, trade_ts, status, quantity="100", price="10.5000"):
    return (trade_id, trade_ts, status, quantity, price)


def test_bad_quantity_becomes_null_and_other_rows_survive(spark):
    rows = [
        trade("T1", "2026-11-02 09:00:00", "NEW", quantity="abc"),
        trade("T2", "2026-11-02 09:00:00", "NEW", quantity="250"),
    ]
    result = cast_trades(spark.createDataFrame(rows, TRADE_SCHEMA))
    quantities = {row.trade_id: row.quantity for row in result.collect()}
    assert quantities == {"T1": None, "T2": 250}


def test_dedupe_removes_true_duplicate(spark):
    row = trade("T1", "2026-11-02 09:00:00", "NEW")
    result = dedupe_events(spark.createDataFrame([row, row], TRADE_SCHEMA))
    assert result.count() == 1


def test_dedupe_keeps_lifecycle_events(spark):
    rows = [
        trade("T1", "2026-11-02 09:00:00", "NEW"),
        trade("T1", "2026-11-02 17:00:00", "AMEND"),
        trade("T1", "2026-11-02 17:30:00", "CANCEL"),
    ]
    result = dedupe_events(spark.createDataFrame(rows, TRADE_SCHEMA))
    assert result.count() == 3


def test_latest_status_keeps_newest_event_per_trade(spark):
    rows = [
        trade("T1", "2026-11-02 09:00:00", "NEW"),
        trade("T1", "2026-11-02 17:00:00", "AMEND"),
        trade("T1", "2026-11-02 17:30:00", "CANCEL"),
        trade("T2", "2026-11-02 10:00:00", "NEW"),
    ]
    result = latest_status(cast_trades(spark.createDataFrame(rows, TRADE_SCHEMA)))
    statuses = {row.trade_id: row.status for row in result.collect()}
    assert statuses == {"T1": "CANCEL", "T2": "NEW"}


def test_unbalanced_amount_is_not_multiplied_by_repeated_trade_rows(spark):
    trades = spark.createDataFrame(
        [
            trade("T1", "2026-11-02 09:00:00", "NEW"),
            trade("T1", "2026-11-02 17:00:00", "AMEND"),
        ],
        TRADE_SCHEMA,
    )
    ledger = spark.createDataFrame(
        [("T1", Decimal("61.93"), Decimal("0.00"))],
        LEDGER_SCHEMA,
    )
    result = unbalanced_trades(ledger, trades).collect()
    assert [(row.trade_id, row.diff) for row in result] == [("T1", Decimal("61.93"))]


def test_unbalanced_ignores_balanced_trades_and_orphans(spark):
    trades = spark.createDataFrame([trade("T1", "2026-11-02 09:00:00", "NEW")], TRADE_SCHEMA)
    ledger = spark.createDataFrame(
        [
            ("T1", Decimal("500.00"), Decimal("0.00")),
            ("T1", Decimal("0.00"), Decimal("500.00")),
            ("ORPHAN", Decimal("100.00"), Decimal("0.00")),
        ],
        LEDGER_SCHEMA,
    )
    assert unbalanced_trades(ledger, trades).count() == 0
