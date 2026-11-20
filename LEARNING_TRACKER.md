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
5. Pass the Databricks Data Engineer Associate, then the Professional (added 2026-11-16).

## Certification track
Added 2026-11-16 without changing the stages below. Items marked 🎓 exist mainly for the exams.
Exam outlines: [Associate](https://www.databricks.com/learn/certification/data-engineer-associate) (45 questions, 90 min, $200; guide dated August 2026) and [Professional](https://www.databricks.com/learn/certification/data-engineer-professional) (59 questions, 120 min, $200; guide dated 9 October 2026). Read each exam guide PDF for the full topic list before prep.
- Do 🎓 items on Free Edition where possible: they cost nothing and don't use up the 14-day trial. If a feature isn't available on Free Edition, move the item into Stage 2 or 3.
- The exams test SQL syntax and feature names as well as PySpark, so the 🎓 exercises use SQL as much as Python.
- Booking an exam costs $200 each; ask first.

## How we work
- I write the code. Claude gives a problem and checks my answer, and gives hints only after I've tried.
- From Ex 4 on, each exercise also ends with a review task: Claude writes a plausible solution with 2-3 hidden bugs, and I find them by reading before running. It comes after the normal tasks and doesn't replace any of them.
- Predict before running. Explain why after.
- Each session ends with 5 basics questions answered out loud.
- Ask before anything that costs money.

## Claude skills track
Added 2026-11-16. Starts after Ex 3 and runs alongside the stages. It doesn't change any exercise: Stage 1 code is still written by me.
Goal: practise using Claude the way real projects do (delegating, reviewing, automating), not just for learning.
- [ ] Before Ex 4: build a `new-exercise` skill with Claude, writing part of it myself (task format, predictions, out-loud questions, hints, review task, answer key checked in local Spark)
- [ ] With Ex 4: a hook that blocks edits to `stage-0/data/manifest/injected_defects.csv`
- [ ] With Ex 5: run `/code-review` on my module before opening the pull request; note what it found and what it missed
- [ ] Stage 2 or 3: a project `.claude/settings.json` that allows routine commands such as local Spark and pytest
- [ ] Stage 3: delegate one whole feature (for example the Asset Bundle and its GitHub Actions deploy) using plan mode; review the diff as a tech lead and write down what I had to correct
- [ ] Stage 3: two independent pieces built in parallel sessions in separate worktrees, then merged
- [ ] Stage 3: connect one MCP connector (GitHub or Databricks) and use it for a real task

## Stage 1: PySpark by hand ($0, local Mac and Free Edition, about 10-12 hours)
Exercises are in `practice/`. My code goes in `practice/exNN_*.py`; answers to check against are in `practice/answers/`, opened only after trying.
Practise in Databricks Free Edition notebooks (data in `/Volumes/workspace/bronze/landing/`). The Mac `.venv` stays available for running pytest locally in Ex 5.
- [x] Local setup: Java 17 and PySpark in `.venv`, so code runs on the Mac with no cluster (needs `JAVA_HOME=/opt/homebrew/opt/openjdk@17`)
- [x] Ex 1, basics: read CSV, `select`, `withColumn`, casts, `when`, `filter`, NULL behaviour (done 2026-11-13; weak spots: say *why* for decimal vs double, and NULL comparisons give NULL, not true)
- [x] Ex 2, aggregates and joins: `groupBy`/`agg`, pivot, inner/left/semi/anti joins, cause and fix a fan-out, broadcast (done 2026-11-14, 2-3 sessions; lesson: cast price to `decimal(18,2)` and explained the mismatch away as rounding. Chase every mismatch to its cause)
- [x] Ex 3, windows: `row_number`/`rank`, `lag`, running totals and the frame trap, latest row per key, top N, single-partition plans (`practice/ex03_windows.md`) (done 2026-11-19, 3 sessions; weak spots: thought `orderBy` before `dropDuplicates` keeps the latest row (a shuffle loses the order); put tie-breakers in `partitionBy` instead of `orderBy`; thought `rank <= 3` gives exactly 3 rows; mixed up partition and frame; didn't drop exact duplicates before `lag`; read `.explain()` from the wrong DataFrame twice)
- [ ] Ex 4, reading and writing: explicit schemas, Delta write modes, `MERGE` from Python
- [ ] Ex 5, tested functions: move logic into a module, pytest locally, notebooks import the module
- [ ] Ex 6, rebuild bronze to Silver to Gold from a blank notebook
- [ ] 🎓 Ex 7, Spark SQL: redo key tasks from Ex 1-3 in SQL (CTEs, `QUALIFY`, `CASE`, `MERGE INTO`, `INSERT OVERWRITE`, views vs tables, managed vs external)
- [ ] 🎓 Ex 8, Delta maintenance: `DESCRIBE HISTORY`, time travel, `RESTORE`, `OPTIMIZE`, `VACUUM`, liquid clustering, change data feed (my shaky basics list)
- [ ] 🎓 Ex 9, streaming: Structured Streaming and Auto Loader on Free Edition, checkpoints, `trigger(availableNow)`, watermarks, stream-static joins
- [ ] Exit test: 3 timed problems, no docs, explaining my thinking out loud

## Stage 2: Azure foundation (about $5-10, estimate not yet checked against current prices)
Start only when Stage 1 is done: the 14-day Databricks trial clock starts here, and Stages 2-4 should fit inside it.
- [ ] Check prices in the Azure pricing calculator; agree the spend limit
- [ ] I create the Pay-As-You-Go account myself; budget alerts at $20 and $40
- [ ] Resource group, ADLS Gen2, Premium Databricks workspace (check for a NAT gateway that bills all the time)
- [ ] Access connector, Unity Catalog storage credential and external locations
- [ ] Run the pipeline on a real cluster with short auto-termination; read the Spark UI
- [ ] 🎓 Governance exercise: `GRANT`/`REVOKE` on catalog, schema and table; a group-based role; a row filter and a column mask; lineage in Catalog Explorer
- [ ] 🎓 Compute exercise: all-purpose vs job vs serverless vs SQL warehouse; when to use each, and what each costs (from the cost query)

## 🎓 Milestone A: Data Engineer Associate (after Stage 2, about 1-2 weeks of prep)
- [ ] Databricks Academy free self-paced Data Engineering learning path, skimming only the parts I haven't done in labs
- [ ] Lakeflow Jobs drill: triggers, task values, conditional tasks, repair runs, parameters
- [ ] CI/CD drill: Git folders vs Repos, Asset Bundle targets (my shaky basics list)
- [ ] Timed practice exam; every wrong answer goes on a mistakes list with the reason
- [ ] Book and pass the exam (ask before paying $200)

## Stage 3: Production-like (about $10-15, estimate)
- [ ] Generator drops daily files with varying volume; ADF lands them in ADLS
- [ ] Auto Loader ingestion; scheduled Workflows job on job clusters
- [ ] `dev` and `prod` catalogs; Asset Bundle deployed by GitHub Actions as a service principal
- [ ] Failure alerts, a cost query from system tables, and a short runbook
- [ ] 🎓 Lakehouse Monitoring on a Gold table; query history and the job system tables
- [ ] 🎓 Delta Sharing (share a Gold table with another recipient) and Lakehouse Federation (query an external database), small and short-lived to keep cost low

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
- [ ] 🎓 Compliance drill: a customer asks to be deleted (GDPR). Delete them from every layer, then prove it with history and `VACUUM`
- [ ] 🎓 Performance drill: Photon on vs off, AQE settings, right-sizing a job cluster; record the time and cost of each

## 🎓 Milestone B: Data Engineer Professional (after Stage 4, about 2-3 weeks of prep)
- [ ] Read the Professional exam guide and mark every topic: done in labs, partly done, or not done
- [ ] Fill the gaps marked "not done" with short exercises
- [ ] Two timed practice exams, with a mistakes list
- [ ] Book and pass the exam (ask before paying $200)

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
| 2026-11-13 | Exercise 1 reviewed; exercise 2 written with answers checked in local Spark |
| 2026-11-14 | Exercises 1 and 2 done; exercise 3 written with answers checked |
| 2026-11-16 | Certification track added: 🎓 items in Stages 1-4 and Milestones A and B; Claude skills track added, starting after Ex 3; CLAUDE.md created |
| 2026-11-19 | Exercise 3 done and reviewed: all numbers match the answer key after corrections; Claude skills track starts next (`new-exercise` skill before Ex 4) |
