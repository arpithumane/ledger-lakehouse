"""Synthetic trading + ledger data generator (stdlib only, no installs needed).

Produces, under --out:
  reference/instruments.csv, counterparties.csv, gl_accounts.csv
  trades/trades_YYYYMMDD.csv          (one file per business day)
  ledger_entries/ledger_YYYYMMDD.csv  (double-entry journals for those trades)
  manifest/injected_defects.csv       (answer key: which bad records we planted)

Volume is controlled by --trades-per-day and --volume-jitter, so the same
script produces a tiny laptop run or a multi-million-row stress run later.

Example:
  python3 generator/generate.py --days 3 --trades-per-day 2000 --out data
"""
import argparse
import csv
import random
import datetime as dt
from pathlib import Path

DESKS = ["EQ_CASH", "EQ_DERIV", "FX", "FIXED_INCOME"]
CURRENCIES = ["USD", "EUR", "GBP", "JPY"]
ASSET_CLASSES = ["EQUITY", "BOND", "ETF", "FX_SPOT"]
COUNTRIES = ["US", "GB", "DE", "JP", "SG", "CH"]
RATINGS = ["AAA", "AA", "A", "BBB", "BB"]

GL_ACCOUNTS = [
    ("1000", "Cash", "ASSET"),
    ("1100", "Securities Inventory", "ASSET"),
    ("2000", "Settlement Payable", "LIABILITY"),
    ("6100", "Brokerage Fee Expense", "EXPENSE"),
]
CASH, INVENTORY, FEE = "1000", "1100", "6100"

TRADE_COLS = ["trade_id", "trade_ts", "desk", "instrument_id", "counterparty_id",
              "side", "quantity", "price", "currency", "status", "source_system"]
LEDGER_COLS = ["entry_id", "trade_id", "journal_ts", "account_id", "debit", "credit",
               "currency", "entry_type", "source_system"]


def write_csv(path, cols, rows):
    path.parent.mkdir(parents=True, exist_ok=True)
    with path.open("w", newline="") as f:
        w = csv.writer(f)
        w.writerow(cols)
        w.writerows(rows)


def make_reference(rng, n_instruments, n_counterparties):
    instruments = []
    for i in range(1, n_instruments + 1):
        sym = "".join(rng.choices("ABCDEFGHIJKLMNOPQRSTUVWXYZ", k=rng.choice([3, 4])))
        instruments.append({
            "instrument_id": f"I{i:05d}", "symbol": sym,
            "asset_class": rng.choice(ASSET_CLASSES),
            "currency": rng.choice(CURRENCIES),
            "base_price": round(rng.uniform(5, 500), 2),
        })
    counterparties = [{
        "counterparty_id": f"C{i:04d}", "name": f"Counterparty {i:04d}",
        "country": rng.choice(COUNTRIES), "rating": rng.choice(RATINGS),
    } for i in range(1, n_counterparties + 1)]
    return instruments, counterparties


def journal_lines(trade, reverse=False):
    """Balanced double-entry lines for one trade: list of (account, debit, credit)."""
    notional = round(trade["quantity"] * trade["price"], 2)
    fee = round(notional * 0.0005, 2)
    if trade["side"] == "BUY":
        lines = [(INVENTORY, notional, 0.0), (CASH, 0.0, notional)]
    else:
        lines = [(CASH, notional, 0.0), (INVENTORY, 0.0, notional)]
    lines += [(FEE, fee, 0.0), (CASH, 0.0, fee)]
    if reverse:
        lines = [(a, c, d) for a, d, c in lines]
    return lines


def main():
    ap = argparse.ArgumentParser()
    ap.add_argument("--out", default="data")
    ap.add_argument("--start-date", default="2026-11-02")
    ap.add_argument("--days", type=int, default=3)
    ap.add_argument("--trades-per-day", type=int, default=2000)
    ap.add_argument("--volume-jitter", type=float, default=0.3,
                    help="daily volume varies +/- this fraction (0.3 = +/-30%%)")
    ap.add_argument("--bad-rate", type=float, default=0.01,
                    help="fraction of trades per day that get a planted defect")
    ap.add_argument("--instruments", type=int, default=200)
    ap.add_argument("--counterparties", type=int, default=50)
    ap.add_argument("--seed", type=int, default=42)
    ap.add_argument("--source-system", default="TRADEPLAT_A")
    args = ap.parse_args()

    rng = random.Random(args.seed)
    out = Path(args.out)
    instruments, counterparties = make_reference(rng, args.instruments, args.counterparties)

    write_csv(out / "reference" / "instruments.csv",
              ["instrument_id", "symbol", "asset_class", "currency", "base_price"],
              [[i[k] for k in ("instrument_id", "symbol", "asset_class", "currency", "base_price")]
               for i in instruments])
    write_csv(out / "reference" / "counterparties.csv",
              ["counterparty_id", "name", "country", "rating"],
              [[c[k] for k in ("counterparty_id", "name", "country", "rating")] for c in counterparties])
    write_csv(out / "reference" / "gl_accounts.csv",
              ["account_id", "account_name", "account_type"], GL_ACCOUNTS)

    manifest = []
    entry_seq = 0
    start = dt.date.fromisoformat(args.start_date)
    day_n = 0
    d = start
    while day_n < args.days:
        if d.weekday() >= 5:  # skip weekends
            d += dt.timedelta(days=1)
            continue
        ds = d.strftime("%Y%m%d")
        n = max(1, int(args.trades_per_day * (1 + rng.uniform(-args.volume_jitter, args.volume_jitter))))
        trades, ledger = [], []

        def ts(minute_offset=0):
            base = dt.datetime.combine(d, dt.time(8, 0)) + dt.timedelta(seconds=rng.randint(0, 9 * 3600))
            return (base + dt.timedelta(minutes=minute_offset)).isoformat(sep=" ")

        def post(trade, journal_ts, reverse, entry_type):
            nonlocal entry_seq
            for acct, deb, cred in journal_lines(trade, reverse):
                entry_seq += 1
                ledger.append([f"E{entry_seq:010d}", trade["trade_id"], journal_ts, acct,
                               f"{deb:.2f}", f"{cred:.2f}", trade["currency"], entry_type,
                               args.source_system])

        def trade_row(t):
            return [t["trade_id"], t["trade_ts"], t["desk"], t["instrument_id"],
                    t["counterparty_id"], t["side"], t["quantity"], f"{t['price']:.4f}",
                    t["currency"], t["status"], args.source_system]

        live = []
        for k in range(1, n + 1):
            ins = rng.choice(instruments)
            t = {
                "trade_id": f"T{ds}{k:07d}", "trade_ts": ts(), "desk": rng.choice(DESKS),
                "instrument_id": ins["instrument_id"],
                "counterparty_id": rng.choice(counterparties)["counterparty_id"],
                "side": rng.choice(["BUY", "SELL"]), "quantity": rng.randint(10, 10000),
                "price": ins["base_price"] * (1 + rng.gauss(0, 0.02)),
                "currency": ins["currency"], "status": "NEW",
            }
            t["price"] = round(t["price"], 4)
            trades.append(trade_row(t))
            post(t, t["trade_ts"], False, "POSTING")
            live.append(t)

        # lifecycle events: ~3% amendments, ~2% cancels (reverse + repost / reverse)
        for t in rng.sample(live, int(n * 0.03)):
            new = dict(t, quantity=max(10, int(t["quantity"] * rng.uniform(0.5, 1.5))),
                       status="AMEND", trade_ts=t["trade_ts"][:11] + "17:00:00")
            trades.append(trade_row(new))
            post(t, new["trade_ts"], True, "REVERSAL")
            post(new, new["trade_ts"], False, "POSTING")
        for t in rng.sample(live, int(n * 0.02)):
            c = dict(t, status="CANCEL", trade_ts=t["trade_ts"][:11] + "17:30:00")
            trades.append(trade_row(c))
            post(t, c["trade_ts"], True, "REVERSAL")

        # planted defects (answer key goes to the manifest)
        fname_t, fname_l = f"trades_{ds}.csv", f"ledger_{ds}.csv"
        for _ in range(int(n * args.bad_rate)):
            kind = rng.choice(["DUPLICATE_TRADE", "NULL_COUNTERPARTY", "NEGATIVE_QTY",
                               "BAD_CURRENCY", "UNBALANCED_JOURNAL", "ORPHAN_JOURNAL"])
            if kind == "ORPHAN_JOURNAL":
                entry_seq += 1
                oid = f"T{ds}9{rng.randint(0, 999999):06d}"
                ledger.append([f"E{entry_seq:010d}", oid, ts(), CASH, "100.00", "0.00",
                               "USD", "POSTING", args.source_system])
                manifest.append([fname_l, kind, oid])
                continue
            if kind == "UNBALANCED_JOURNAL":
                victim = rng.choice(live)["trade_id"]
                idx = [i for i, r in enumerate(ledger) if r[1] == victim and r[7] == "POSTING"
                       and float(r[5]) > 0]
                if idx:
                    ledger.pop(idx[-1])
                    manifest.append([fname_l, kind, victim])
                continue
            i = rng.randrange(n)  # one of the original NEW rows
            row = trades[i]
            if kind == "DUPLICATE_TRADE":
                trades.append(list(row))
            elif kind == "NULL_COUNTERPARTY":
                row[4] = ""
            elif kind == "NEGATIVE_QTY":
                row[6] = -abs(int(row[6]))
            elif kind == "BAD_CURRENCY":
                row[8] = "XXX"
            manifest.append([fname_t, kind, row[0]])

        rng.shuffle(trades)
        write_csv(out / "trades" / fname_t, TRADE_COLS, trades)
        write_csv(out / "ledger_entries" / fname_l, LEDGER_COLS, ledger)
        print(f"{d}: {len(trades):>8,} trade rows, {len(ledger):>9,} ledger rows")
        d += dt.timedelta(days=1)
        day_n += 1

    write_csv(out / "manifest" / "injected_defects.csv", ["file", "defect_type", "key"], manifest)
    print(f"Planted {len(manifest)} defects -> {out/'manifest'/'injected_defects.csv'}")


if __name__ == "__main__":
    main()
