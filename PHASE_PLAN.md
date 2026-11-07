# PHASE_PLAN

Reference this file with: "Continue ledger-lakehouse, Phase N from PHASE_PLAN.md".
Each phase follows the same pattern: concept (with the Ab Initio equivalent) -> build -> you try a variation -> checkpoint -> update PROJECT_STATE.md.

## Phase 0 - Sandbox and data generator (Free Edition, $0)
- Build: data generator, landing volume, bronze Delta tables
- Learn: workspace, Unity Catalog (catalog.schema.table), volumes, Delta tables
- Ab Initio: input datasets, DML
- Done when: bronze tables exist and the 3 checkpoint questions in README are answered

## Phase 1 - Medallion layers plus CI/CD skeleton
- Build: typed Silver tables (casting, dedupe, latest-status-per-trade), simple Gold table, pytest tests, GitHub Actions, Databricks CLI, first Asset Bundle
- Learn: PySpark DataFrames, Delta MERGE, incremental loads, Declarative Pipelines intro
- Ab Initio: reformat, dedup sorted, join, rollup, graph parameters
- Done when: Silver and Gold build from Bronze, tests pass in GitHub Actions

## Phase 2 - Metadata-driven framework and accounting logic
- Build: YAML-driven ingestion, DQ rules and reconciliation checks (no per-table code); double-entry validation; positions and P&L; quarantine tables
- Learn: reusable accelerator design, expectations, data quality patterns
- Ab Initio: generic graphs, parameter sets, DQ components
- Done when: all planted defects in the manifest are caught and quarantined, with a recon report

## Phase 3 - Azure foundation
- Build: Azure account (Pay-As-You-Go), budget alerts at $20 and $40, resource group, ADLS Gen2, Azure Databricks workspace, Unity Catalog metastore and external locations
- Learn: Azure basics, storage accounts, access connector, RBAC
- Ab Initio: environment and infrastructure setup
- Done when: Phase 1-2 code runs on Azure Databricks, cost alert tested
- Warning: start the Databricks trial clock only when ready to use it

## Phase 4 - Orchestration (ADF + Workflows)
- Build: Azure Data Factory pipeline to land files, Databricks Workflows job, schedule for a 1-2 day run, retries, failure alerts
- Learn: triggers, job dependencies, monitoring
- Ab Initio: Control>Center / scheduler plans
- Done when: unattended 1-2 day scheduled run completes with daily variable volume

## Phase 5 - Second source, profiling, volume and tuning
- Build: second overlapping trading source with duplicate counterparties and instruments; profiling notebook; source-to-target mapping document; entity consolidation; high-volume runs (10M+ trades); Spark tuning; cost dashboard from system tables
- Learn: skew, small files, partitioning and liquid clustering, AQE, cost control
- Ab Initio: parallelism, layouts, partitioning by key
- Done when: high-volume run meets a target time at a recorded cost

## Phase 6 - Semantic layer, context layer, knowledge graph, agent
- Build: metric definitions (semantic layer), Unity Catalog comments and tags (context layer), entity and relationship tables (knowledge graph), natural-language agent over gold tables with guardrails and evaluation questions
- Learn: Genie or custom agent with tools, evaluation of agent answers
- Ab Initio: none (new territory)
- Done when: agent answers a fixed set of test questions correctly, with sources

## Phase 7 - Dashboard, hardening, conversion exercise
- Build: Power BI or AI/BI dashboard on the semantic layer; monitoring; CI/CD to deploy dev -> prod; convert 2-3 Ab Initio graphs and .xfr files to PySpark using Claude, with equivalence tests; architecture decision records and handoff docs
- Learn: promotion process, release practices, AI-assisted code conversion
- Ab Initio: release/promotion, code migration
- Done when: a fresh engineer can run the project from the docs

## Skills map to the job description
| JD requirement | Where covered |
|---|---|
| Production PySpark/SQL, DLT or dbt, ADF and Workflows | Phases 1, 2, 4 |
| Rapid POCs and reusable accelerators (ingestion, DQ, recon) | Phase 2 |
| Profiling, consolidation, source-to-target mapping, Spark tuning, cost control | Phase 5 |
| CI/CD, automated testing, BI semantic models | Phases 1, 7 |
| Data for AI: semantic layer, context layer, knowledge graph | Phase 6 |
| AI-assisted productivity: code conversion, tests, docs; written English | Phase 7, ongoing |
