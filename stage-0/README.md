# ledger-lakehouse

A learning project: a trading-to-general-ledger platform on Azure Databricks.
Trades -> positions -> double-entry journals -> reconciliation -> AI agent.

## Phase 0 - generate data and load Bronze (Mac)

### 1. Generate data locally
```bash
cd ledger-lakehouse/stage-0
python3 generator/generate.py --days 3 --trades-per-day 2000 --out data
```
No installs needed (standard library only). You get `data/` with:
`reference/`, `trades/`, `ledger_entries/`, and `manifest/injected_defects.csv`
(the answer key of bad records we planted - **keep it out of Databricks**, it is our test oracle).

Volume knobs for later: `--trades-per-day 5000000 --volume-jitter 0.5 --days 2`.

### 2. Set up Databricks
1. Open your Free Edition workspace -> **Workspace** -> **Create** -> **Git folder** is optional for now;
   simply **Import** `notebooks/00_load_bronze.py` (it imports as a notebook).
2. Run the first cell. It creates schema `bronze` and volume `landing`.
   If your catalog is not `workspace`, edit `CATALOG` first (see the Catalog sidebar).
3. **Catalog** -> `bronze` -> `landing` -> **Create folder** for each of: `trades`, `ledger_entries`,
   `reference/instruments`, `reference/counterparties`, `reference/gl_accounts`.
   Then **Upload to this volume** the matching CSVs into each folder.
4. Run the remaining cells. Read the output of the three sanity queries.

### 3. Push to GitHub
```bash
git add . && git commit -m "Phase 0: generator and bronze loader"
git push -u origin main
```
`data/` is ignored by the `.gitignore` at the repo root, so generated files and the answer key stay out of Git.

## Checkpoint questions (try before we move on)
- How many `trades_raw` rows are there vs. distinct `trade_id`? Why do they differ?
- Which defect types can you find with SQL alone? Compare with `manifest/injected_defects.csv`.
- Why do we keep bronze as strings instead of typing it?
