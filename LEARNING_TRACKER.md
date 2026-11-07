# LEARNING_TRACKER

Interview prep plan and progress. Interview: **Monday 2026-11-09**, discussion only, no demo, depth unknown.
Work finishes by the night of Sunday 2026-11-08. [PHASE_PLAN.md](PHASE_PLAN.md) stays as the longer-term plan.

Start a new chat with: "Continuing ledger-lakehouse. Read LEARNING_TRACKER.md and PROJECT_STATE.md, then continue from the first unticked item."

**Key:** `[x]` done, `[ ]` to do, `[~]` started or needs confirming. Tick an item only when it has been run or practised.
Time estimates are rough.

## Current focus
Push `phase-1-silver`, open a pull request and get the tests passing in GitHub Actions.

## Saturday 2026-11-07: hands-on (about 5-7 hours)

### Phase 0: bronze
- [x] Generate data and upload it to the landing volume
- [x] Load 5 bronze tables; row counts match the source files
- [x] Answer the 3 checkpoint questions
- [~] Find all 6 planted defect types with SQL (4 confirmed; confirm 15 orphans and the semi join's 13 unbalanced journals)
- [x] Commit, push, open a pull request and merge to `main`

### Phase 1: Silver and Gold
Branch: `phase-1-silver`. Notebooks are in `stage-1/notebooks/`.
- [x] `01_silver_trades`: apply types and dedupe (6,591 rows)
- [x] Variation: dedupe on `trade_id` alone and see defects disappear
- [x] `02_silver_trades_latest`: latest status with a window (6,280 rows)
- [x] Find why `trades_latest` shows 3 negative quantities instead of 6
- [x] `03_silver_ledger`: write it yourself (difference 7,806.44)
- [x] `04_gold_daily_desk_summary`: results match the expected table
- [x] Incremental load with `MERGE`: `05_incremental_merge_lab` results match, and a rerun changes nothing
- [~] A few pytest tests: written, first run will be in GitHub Actions
- [~] GitHub Actions running the tests on a pull request: workflow written, not yet run
- [ ] Commit, push and merge `phase-1-silver`

### Small data quality framework (reduced Phase 2)
- [ ] YAML rules, with no per-table code
- [ ] Quarantine table with a reason for each row
- [ ] Reconciliation report
- [ ] Check every planted defect is caught, using the manifest as the answer key

## Sunday 2026-11-08: labs, theory and practice (about 5-6 hours)

### Hands-on labs
Check each lab runs on Free Edition first. If it doesn't, cover it as theory instead.
- [ ] Declarative Pipeline with expectations: rebuild one Silver table (45 min)
- [ ] Workflows job: chain notebooks with dependencies and a retry (30 min)
- [ ] Profiling, overlap query and a short source-to-target mapping (45 min)
- [ ] Read an `EXPLAIN` or query profile for a join (30 min)
- [ ] Convert a small made-up Ab Initio transform to PySpark with Claude, plus a test (30 min)

### Theory (60-90 min)
- [ ] ADF compared with Workflows and Control>Center
- [ ] Azure: ADLS, access connectors, external locations, Unity Catalog
- [ ] Spark tuning: skew, small files, AQE, liquid clustering
- [ ] Cost control: what drives cost and how to monitor it
- [ ] Semantic layer, context layer, knowledge graph, agents
- [ ] Databricks compared with Snowflake
- [ ] dbt compared with Declarative Pipelines

### Interview practice (60-90 min)
- [ ] Project story, 2-minute version
- [ ] Project story, 10-minute version, with architecture and trade-offs
- [ ] Mock interview: general questions
- [ ] Mock interview: deep-dive questions
- [ ] Review weak answers and repeat them

## Job description coverage
| JD line | How it's covered | Depth | Status |
|---|---|---|---|
| PySpark and SQL | Silver and Gold notebooks | Hands-on | Mostly done |
| Delta Live Tables or dbt | Declarative Pipeline lab, dbt comparison | Lab and theory | To do |
| ADF | Comparison with Workflows | Theory | To do |
| Databricks Workflows | Workflows lab | Lab | To do |
| Snowflake | Comparison with Databricks | Theory | To do |
| Reusable ingestion, DQ and reconciliation frameworks | Small data quality framework | Hands-on | To do |
| Profiling, overlap, source-to-target mapping | Profiling lab | Lab | To do |
| Spark tuning | Query plan lab, tuning theory | Lab and theory | To do |
| Cost control | Cost theory | Theory | To do |
| CI/CD and automated testing | pytest and GitHub Actions | Hands-on | To do |
| BI semantic models and SQL layers | Gold table, semantic layer theory | Hands-on and theory | Started |
| Semantic layer, context layer, knowledge graph | Theory, using project tables | Theory | To do |
| GenAI for code conversion, tests and docs | Conversion lab | Lab | To do |

## Out of scope before the interview
Azure setup and spend, 10M-row runs, the dashboard, a second source system and a full Ab Initio conversion.
These are discussion topics only, except the dashboard, which only needs a brief mention.

## How to describe the project
A hands-on project built on Databricks Free Edition to move Ab Initio experience onto the platform.
It is not production Azure experience. For anything covered only as theory, say so and explain the approach.

## Project stories to practise
| Story | What happened | Lesson |
|---|---|---|
| Dedup key | Deduping on `trade_id` alone removed 311 lifecycle rows and hid defects, with no error | The key must match the grain; `dropDuplicates` keeps an arbitrary row |
| Join fan-out | An inner join to `trades_raw` doubled one trade's imbalance (123.86 instead of 61.93), but the row count looked right | Use a semi join to test existence; row counts alone don't prove correctness |
| Hidden defects | `trades_latest` shows 3 negative quantities, but the history has 6 | Run data quality checks on the full history |
| 28 vs 13 | The imbalance query returned 28 trades: 13 unbalanced journals plus 15 orphans | Separate the causes; the 7,806.44 difference is fully explained |
| Safe reruns | Rerunning a batch through `MERGE` inserted 0 and updated 0 rows; a correction updated exactly 1 | Idempotent loads make failed jobs safe to restart |
| Strings in bronze | Bronze keeps raw strings; Silver uses `try_cast` and counts failures | Capture must not fail or silently lose values |

## Questions to resolve
- [ ] What does "Avery reporting" refer to? Ask the recruiter if possible.
- [ ] How many hours are available this weekend? If time is short, shrink the data quality framework first and keep the mock interview.

## Session log
| Date | What happened |
|---|---|
| 2026-11-06 | Accounts and Phase 0 code set up |
| 2026-11-07 | Phase 0 finished and merged. Silver trades, latest status and Silver ledger built. Plan changed for the interview. |
