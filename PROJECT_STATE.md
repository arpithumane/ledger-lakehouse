# PROJECT_STATE

Last updated: 2026-11-07 (end of Phase 0)
Update this file at the end of every phase. Start each new Claude chat with:
"Continuing ledger-lakehouse. Read PROJECT_STATE.md and PHASE_PLAN.md, then continue from Phase N."

## Goal
Learn Azure Databricks by building a production-style trading-to-general-ledger platform:
batch and streaming ingestion, medallion layers, data quality and reconciliation framework,
orchestration, volume testing, and an AI agent over the gold tables.
Also meant to line up with a 6-9 year pipeline engineering job description.

## Owner context
- 10 years Ab Initio; knows basic Python, SQL, Unix. New to Databricks, Spark and Azure.
- Learning style: explain each concept next to its Ab Initio equivalent, build, then try a variation.
- Laptop: Mac. Go slowly, one step at a time.
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
| Catalog / schema | `workspace` / `bronze` (change here if different) | Free Edition default |

## Status
- [x] Phase 0 code written: generator, bronze notebook, README
- [x] Phase 0 run: generator run on Mac, files uploaded to the landing volume, bronze tables created, checkpoint questions answered
- [ ] Phase 1 onward: see PHASE_PLAN.md (next: Phase 1)

Bronze row counts (`--days 3 --trades-per-day 2000`): trades_raw 6,597 (6,280 distinct trade_id), ledger_entries_raw 27,114, instruments_raw 200, counterparties_raw 50, gl_accounts_raw 4.

## Repo layout
- `stage-0/generator/generate.py` - synthetic trades, ledger entries, reference data, defect manifest
- `stage-0/notebooks/00_load_bronze.py` - Databricks notebook that loads CSVs to bronze Delta tables
- `stage-0/data/` - generated files (not in Git; recreate with the generator)
- `stage-0/data/manifest/injected_defects.csv` - answer key for planted bad records. Never upload to Databricks.

## Planted defect types (answer key)
DUPLICATE_TRADE, NULL_COUNTERPARTY, NEGATIVE_QTY, BAD_CURRENCY, UNBALANCED_JOURNAL, ORPHAN_JOURNAL.
Phase 2 DQ rules must catch all of them.

## Open questions / issues
- (none yet) Add error messages and fixes here as they come up.

## What the owner has learned
Phase 0:
- Unity Catalog naming (catalog.schema.table), volumes as the landing area, bronze Delta tables.
- A `trade_id` repeats for two reasons: AMEND/CANCEL events (311 rows, legitimate) and true duplicates (6 rows, defect). Dedup on `trade_id` alone would destroy the lifecycle events.
- Double-entry: each trade's debits must equal its credits. Corrections are added as REVERSAL rows, never updates.
- The notebook's imbalance query returns 28 trades: 13 UNBALANCED_JOURNAL plus 15 ORPHAN_JOURNAL (single-line entries with no trade).
- All 6 planted defect types can be found with SQL alone.
- Joining to a non-unique key multiplies rows: an INNER JOIN to trades_raw doubled one trade's imbalance while the row count still looked right. Use LEFT SEMI / LEFT ANTI JOIN to test existence.
- Bronze stays as strings so capture does not fail and bad values are not silently turned into NULL. Bad rows are quarantined later with a reason, not just filtered out.

## Cost log
| Date | Item | Cost |
|---|---|---|
| 2026-11-06 | Free Edition setup | $0 |
