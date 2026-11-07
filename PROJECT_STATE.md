# PROJECT_STATE

Last updated: 2026-11-07 (Phase 1 in progress, plan changed for the interview)
Update this file at the end of every phase. Start each new Claude chat with:
"Continuing ledger-lakehouse. Read LEARNING_TRACKER.md and PROJECT_STATE.md, then continue from the first unticked item."

**Interview on Monday 2026-11-09 (discussion only).** `LEARNING_TRACKER.md` is the active plan until then; `PHASE_PLAN.md` is the longer-term plan.

## Goal
Learn Azure Databricks by building a production-style trading-to-general-ledger platform:
batch and streaming ingestion, medallion layers, data quality and reconciliation framework,
orchestration, volume testing, and an AI agent over the gold tables.
Also meant to line up with a 6-9 year pipeline engineering job description.

## Owner context
- 10 years Ab Initio; knows basic Python, SQL, Unix. New to Databricks, Spark and Azure.
- Learning style: explain each concept next to its Ab Initio equivalent, build, then try a variation.
- Laptop: Mac. One step at a time, but keep up the pace until the interview: skip optional variations.
- Budget: $20-50 for the first week of Azure learning. Do not exceed without asking.

## Decisions so far
| Decision | Choice | Why |
|---|---|---|
| Domain | Trading, accounting, ledger | Hard correctness rules; good for DQ and recon |
| Early environment | Databricks Free Edition (serverless, $0) | Learn with no cost |
| Azure start | Phase 3, not before | Trial credits have clocks (Databricks trial: 14 days) |
| Azure subscription type | Pay-As-You-Go with budget alerts | Azure free trial has a 4-core limit; clusters do not run |
| Compute | Serverless first | No idle cluster cost, fewer settings |
| Bronze rule | Everything as strings, add _source_file and _ingest_ts | Bad data must stay visible |
| Data generator | Python stdlib only, seeded, volume knobs | Reproducible; scales to millions of rows |
| Agent scope | Agent over gold tables | Chosen by owner |
| Catalog / schemas | `workspace` / `bronze`, `silver`, `gold` | Free Edition default |
| Trade event dedup key | `trade_id`, `trade_ts`, `status` | Keeps lifecycle events; `trade_id` alone hides defects |
| Ledger dedup key | `entry_id` | One ledger line; a trade has many |
| Money type | `decimal`, not `double` | A ledger must balance to the cent |
| Bad values in Silver | Keep them for now, `try_cast` for types | Phase 2 quarantines them with a reason |
| Data quality rules run on | `silver.trades`, not `trades_latest` | `trades_latest` hides defects on earlier events |
| Interview scope | Hands-on: Phase 1 essentials, small Phase 2, short labs. Theory: Azure, ADF, tuning, cost, AI layers | Full plan is too large for the deadline; a discussion rewards explainable understanding |
| Azure before the interview | None | Avoids spend and starting the trial clock |
| Added to interview scope | Asset Bundle lab to a `dev` target; small agent over Gold | Owner wants agentic AI hands-on; the JD covers CI/CD and data for AI |
| Way of working | Owner reads and predicts, writes part of each lab, and answers before moving on | Running code and matching numbers wasn't building understanding |

## Status
- [x] Phase 0 code written: generator, bronze notebook, README
- [x] Phase 0 run: generator run on Mac, files uploaded to the landing volume, bronze tables created, checkpoint questions answered
- [x] Phase 1 essentials: Silver trades, latest status and Silver ledger done; Gold done; `MERGE` lab, tests and CI done and merged. Asset Bundle deferred.
- [x] Small data quality framework (reduced Phase 2): 61 of 61 defects caught, 3 of 3 reconciliation checks pass. Branch `phase-2-dq`, not yet merged.
- [ ] Phases 3-7: paused until after the interview; covered by labs and theory in LEARNING_TRACKER.md

Bronze row counts (`--days 3 --trades-per-day 2000`): trades_raw 6,597 (6,280 distinct trade_id), ledger_entries_raw 27,114, instruments_raw 200, counterparties_raw 50, gl_accounts_raw 4.

## Repo layout
- `stage-0/generator/generate.py` - synthetic trades, ledger entries, reference data, defect manifest
- `stage-0/notebooks/00_load_bronze.py` - Databricks notebook that loads CSVs to bronze Delta tables
- `stage-0/data/` - generated files (not in Git; recreate with the generator)
- `stage-1/notebooks/01_silver_trades.py` - types and dedupe to `silver.trades`
- `stage-1/notebooks/02_silver_trades_latest.py` - latest status to `silver.trades_latest`
- `stage-1/notebooks/03_silver_ledger.py` - reference copy; the owner wrote their own version in Databricks
- `stage-1/notebooks/04_gold_daily_desk_summary.py` - Gold rollup to `gold.daily_desk_summary`
- `stage-1/notebooks/05_incremental_merge_lab.py` - MERGE lab on its own table, `silver.trades_incremental`
- `stage-1/src/transforms.py` - tested Silver transformations
- `stage-1/tests/` - pytest tests, run in GitHub Actions
- `.github/workflows/tests.yml` - runs the tests on pull requests and pushes to main
- `stage-2/rules/dq_rules.yml` - data quality rules and reconciliation checks
- `stage-2/src/dq_framework.py` - runs the rules; has no per-table code
- `stage-2/notebooks/06_dq_framework.py` - writes `silver.quarantine` and `gold.dq_recon_report`
- `stage-2/scripts/check_against_manifest.py` - compares the quarantine with the answer key on the Mac
- `LEARNING_TRACKER.md` - interview plan, hands-on checklist and JD coverage
- `stage-0/data/manifest/injected_defects.csv` - answer key for planted bad records. Never upload to Databricks.

## Planted defect types (answer key)
DUPLICATE_TRADE, NULL_COUNTERPARTY, NEGATIVE_QTY, BAD_CURRENCY, UNBALANCED_JOURNAL, ORPHAN_JOURNAL.
Phase 2 DQ rules must catch all of them.

## Open questions / issues
- GitHub pushes need a personal access token; it's saved in Keychain after the first push.
- No Java on the Mac, so PySpark tests run only in GitHub Actions.
- Notebooks still have their own copies of the logic in `stage-1/src/transforms.py`. So tests prove the module, not the notebooks, until the notebooks import it.
- Pushing workflow files needs a GitHub token with the `workflow` scope.
- The `MERGE` lab only detects changes in 4 columns, so a change to another column such as `desk` would not update the row.
- `gold.daily_desk_summary` still contains bad rows (`XXX` currency, negative quantities) until the data quality framework exists.
- What does "Avery reporting" in the job description refer to?

## What the owner has learned
Phase 0:
- Unity Catalog naming (catalog.schema.table), volumes as the landing area, bronze Delta tables.
- A `trade_id` repeats for two reasons: AMEND/CANCEL events (311 rows, legitimate) and true duplicates (6 rows, defect). Dedup on `trade_id` alone would destroy the lifecycle events.
- Double-entry: each trade's debits must equal its credits. Corrections are added as REVERSAL rows, never updates.
- The notebook's imbalance query returns 28 trades: 13 UNBALANCED_JOURNAL plus 15 ORPHAN_JOURNAL (single-line entries with no trade).
- Joining to a non-unique key multiplies rows: an INNER JOIN to trades_raw doubled one trade's imbalance while the row count still looked right. Use LEFT SEMI / LEFT ANTI JOIN to test existence.
- Bronze stays as strings so capture does not fail and bad values are not silently turned into NULL. Bad rows are quarantined later with a reason, not just filtered out.

Phase 1 so far:
- Spark is lazy: transformations build a plan, and actions such as `count`, `display` or a table write run it.
- `dropDuplicates` keeps an arbitrary row, so it's only safe for true duplicates. Deduping on `trade_id` alone removed lifecycle rows and hid defects with no error.
- A window (`partitionBy` + `orderBy` + `row_number`) does what Sort + Dedup Sorted does, and keeps every row until you filter.
- `trades_latest` shows 3 negative quantities while the history has 6, so data quality checks belong on the full history.
- Data quality rules come in two kinds: row-level conditions (like Filter by Expression) and set-level queries that need aggregation or joins (like Rollup or Join).
- A check can pass by looking in the wrong place: duplicate detection must run on bronze, because Silver has already removed them.
- The rule summary hides rules with 0 failures, so it can't show the difference between "passed" and "never ran".
- `MERGE` is idempotent here: rerunning a batch inserted 0 and updated 0 rows, and a correction updated exactly 1.
- Silver ledger control total: 7,806.44 difference = 6,306.44 from unbalanced journals + 1,500.00 from orphans.

## Cost log
| Date | Item | Cost |
|---|---|---|
| 2026-11-06 | Free Edition setup | $0 |
