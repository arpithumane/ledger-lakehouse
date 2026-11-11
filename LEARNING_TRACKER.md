# LEARNING_TRACKER

The active plan, changed on 2026-11-10 after the interview. [PHASE_PLAN.md](PHASE_PLAN.md) is the older, longer plan; this file replaces it where they differ.

Start a new chat with: "Continuing ledger-lakehouse. Read LEARNING_TRACKER.md and PROJECT_STATE.md, then continue from the first unticked item."

**Key:** `[x]` done, `[ ]` to do, `[~]` started or needs confirming. Tick an item only when you did it yourself.
Time estimates are rough.

## Why the plan changed
The interview on 2026-11-09 went badly: nerves, and basic questions I couldn't answer.
Guided labs built recognition, not recall. The new goal is real ability:
1. Write PySpark on my own.
2. Run the pipeline on real Azure, under $50 for the month.
3. Run it like production.
4. Diagnose production-style failures.

## How we work
- I write the code. Claude gives a problem and checks my answer, and gives hints only after I've tried.
- Predict before running. Explain why after.
- Each session ends with 5 basics questions answered out loud.
- Ask before anything that costs money.

## Stage 1: PySpark by hand ($0, local Mac and Free Edition, about 10-12 hours)
Exercises are in `practice/`. My code goes in `practice/exNN_*.py`; answers to check against are in `practice/answers/`, opened only after trying.
Practise in Databricks Free Edition notebooks (data in `/Volumes/workspace/bronze/landing/`). The Mac `.venv` stays available for running pytest locally in Ex 5.
- [x] Local setup: Java 17 and PySpark in `.venv`, so code runs on the Mac with no cluster (needs `JAVA_HOME=/opt/homebrew/opt/openjdk@17`)
- [ ] Ex 1, basics: read CSV, `select`, `withColumn`, casts, `when`, `filter`, NULL behaviour
- [ ] Ex 2, aggregates and joins: `groupBy`/`agg`, inner/left/semi/anti joins, cause and fix a fan-out
- [ ] Ex 3, windows: `row_number`, `lag`, running totals, latest row per key
- [ ] Ex 4, reading and writing: explicit schemas, Delta write modes, `MERGE` from Python
- [ ] Ex 5, tested functions: move logic into a module, pytest locally, notebooks import the module
- [ ] Ex 6, rebuild bronze to Silver to Gold from a blank notebook
- [ ] Exit test: 3 timed problems, no docs, explaining my thinking out loud

## Stage 2: Azure foundation (about $5-10, estimate not yet checked against current prices)
Start only when Stage 1 is done: the 14-day Databricks trial clock starts here, and Stages 2-4 should fit inside it.
- [ ] Check prices in the Azure pricing calculator; agree the spend limit
- [ ] I create the Pay-As-You-Go account myself; budget alerts at $20 and $40
- [ ] Resource group, ADLS Gen2, Premium Databricks workspace (check for a NAT gateway that bills all the time)
- [ ] Access connector, Unity Catalog storage credential and external locations
- [ ] Run the pipeline on a real cluster with short auto-termination; read the Spark UI

## Stage 3: Production-like (about $10-15, estimate)
- [ ] Generator drops daily files with varying volume; ADF lands them in ADLS
- [ ] Auto Loader ingestion; scheduled Workflows job on job clusters
- [ ] `dev` and `prod` catalogs; Asset Bundle deployed by GitHub Actions as a service principal
- [ ] Failure alerts, a cost query from system tables, and a short runbook

## Stage 4: Production issues (about $10-15, estimate)
Claude plants a hidden failure with an answer key. I get only the symptom, then diagnose, fix and write a short postmortem.
- [ ] Schema drift: new column or changed type
- [ ] File delivered twice, or late
- [ ] Bad-data spike blocks downstream through the DQ gate
- [ ] Skewed join: stragglers or out of memory
- [ ] Small files slow queries down
- [ ] Bad deploy corrupts a table: `RESTORE` and backfill
- [ ] Storage permission revoked: 403 errors
- [ ] Two writers conflict on one Delta table
- [ ] Ledger reconciliation breaks by a small amount
- [ ] Cluster left running: cost spike

## Parked
Second source system, dashboard, 10M-row runs (except as needed for the skew drill), knowledge graph.

## Done before the change (interview sprint, 2026-11-06 to 2026-11-08)
- Bronze, Silver, Gold, incremental `MERGE`, pytest tests and GitHub Actions CI
- YAML data quality framework: 61 of 61 planted defects caught, 3 of 3 reconciliation checks pass
- Declarative Pipeline with expectations; `AUTO CDC` as SCD Type 1 and Type 2
- Workflows job `ledger_daily` with a retry and a repair run
- Profiling and overlap query (source-to-target mapping not written)
- Genie agent and a Playground agent with a Unity Catalog function tool, tested with fixed questions
- Basics drill: still shaky on Git folders vs Repos, service principals, `RESTORE`, `OPTIMIZE` vs `VACUUM`, clustering vs partitioning, change data feed

## Project stories
| Story | What happened | Lesson |
|---|---|---|
| Dedup key | Deduping on `trade_id` alone removed 311 lifecycle rows and hid defects, with no error | The key must match the grain; `dropDuplicates` keeps an arbitrary row |
| Join fan-out | An inner join to `trades_raw` doubled one trade's imbalance (123.86 instead of 61.93), but the row count looked right | Use a semi join to test existence; row counts alone don't prove correctness |
| Hidden defects | `trades_latest` shows 3 negative quantities, but the history has 6 | Run data quality checks on the full history |
| 28 vs 13 | The imbalance query returned 28 trades: 13 unbalanced journals plus 15 orphans | Separate the causes; the 7,806.44 difference is fully explained |
| Safe reruns | Rerunning a batch through `MERGE` inserted 0 and updated 0 rows; a correction updated exactly 1 | Idempotent loads make failed jobs safe to restart |
| CI catches a real bug | Changing the dedup key to `trade_id` turned the pull request red; reverting it turned it green | Tests encode what you've learned, so the mistake can't return unnoticed |
| Every defect caught | YAML-driven rules quarantined 61 of 61 planted defects; the ledger imbalance reconciled to the cent | Prove a framework against a known answer key |
| A passing rule disappears | Rules with 0 failures didn't appear in the summary, so you can't tell "passed" from "never ran" | Report every rule, including zero counts |
| Expectations vs quarantine | The pipeline dropped 16 rows but only kept counts; the framework keeps every failing record and its reason | Use expectations to monitor and gate, and quarantine when failing rows must be traced and fixed |
| Retry vs repair | `dq_checks` failed on a code bug, so the retry failed the same way; after the fix, a repair run reran only that task | Retries are for temporary failures; bugs need a fix and a repair run |
| Strings in bronze | Bronze keeps raw strings; Silver uses `try_cast` and counts failures | Capture must not fail or silently lose values |
| Valid SQL, wrong answer | Genie summed four currencies into one number with no warning; comments and instructions fixed it, but excluding `XXX` then wrongly cut the trade count from 6,156 to 6,147 | Rerun a fixed question set with known answers after every change |
| Structure beats prompts | A required `currency` parameter stopped cross-currency sums; the agent still skipped JPY and called it "all" until the prompt was fixed and tests ran in fresh chats; it couldn't delete because it had no delete tool | Enforce limits with tools and permissions; prompts only guide |

## Session log
| Date | What happened |
|---|---|
| 2026-11-06 | Accounts and Phase 0 code set up |
| 2026-11-07 | Phase 0 to the data quality framework built and merged |
| 2026-11-08 | Pipeline, Workflows, `AUTO CDC` and agent labs; basics drill |
| 2026-11-09 | Interview went badly on basics and nerves |
| 2026-11-10 | Plan changed to 4 stages; local PySpark setup and exercise 1 started |
