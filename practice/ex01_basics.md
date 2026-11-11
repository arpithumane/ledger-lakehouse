# Exercise 1: PySpark basics (60-90 min)

Write everything yourself. No copying from the stage notebooks.
For each task: write your prediction as a comment first, then run, then compare.
Check against `practice/answers/ex01.md` only after finishing a task.

**On Databricks (Free Edition):** create a notebook named `ex01_basics` and use serverless compute.
`spark` already exists, so skip creating a session in task 1.
Data: `/Volumes/workspace/bronze/landing/trades/` (3 CSV files with a header row). Read the files, not the bronze table.

**On the Mac:** write `practice/ex01_basics.py` and run it from the repo root with `.venv/bin/python practice/ex01_basics.py`.
Data: `stage-0/data/trades/*.csv`.

## Tasks

**1. Read.** On the Mac, create a SparkSession yourself. On Databricks, `spark` already exists.
Read all three trade files into one DataFrame with the header option on and no schema inference.
- Predict: what data type will `quantity` be?
- Print the schema, the row count and the number of distinct `trade_id` values.

**2. Cast.** Turn `quantity` into `int`, `price` into `decimal(18,4)` and `trade_ts` into `timestamp`, using `cast`.
Then, separately, build a one-row DataFrame holding the string `'12x'` and cast it to `int`, first with `cast`, then with `try_cast`.
- Predict: what does each one do with `'12x'`?
- Explain: why does the Silver code use `try_cast`?

**3. Derive.** Add `notional` = quantity × price, rounded to 2 decimal places.
- Show the top 3 trades by notional: `trade_id` and `notional` only.
- Predict, then check: what data type is `notional`, and why not `double`?

**4. Branch.** Add `signed_qty`: positive for `BUY`, negative for `SELL`, using `when`.
- Sum `signed_qty` over all rows.
- Predict: if you leave out `otherwise` and a row has side `HOLD`, what does `signed_qty` become?

**5. Filter.** Count each of these with `filter`:
- a. currency is `XXX`
- b. quantity below zero
- c. side is `BUY` **and** quantity above 5000. Write it once without brackets around each condition first, and read the error.

**6. NULL trap.** Predict all three numbers before running:
- a. rows where `counterparty_id == 'C0001'`
- b. rows where `counterparty_id != 'C0001'`
- c. Do a + b equal the total row count? If not, why not?
- d. Write one filter that counts every row that is not `C0001`, including NULLs.

**7. Combine.** For `USD` trades whose status is not `CANCEL`: count the rows and sum `notional`.

## Say out loud when done (no notes)
1. What's the difference between a transformation and an action? Name 3 of each.
2. Your code ran `withColumn` 5 times before anything happened. Why was nothing computed until `count()`?
3. When would you use `select` and when `withColumn`?
4. Why use `decimal` rather than `double` for money?
5. Why can `!=` silently lose rows, and how do you guard against it?

## Hints (only after 10 minutes stuck)
<details><summary>Task 1</summary>Look up `SparkSession.builder`, then `spark.read.option(...).csv(path)`. A path can contain `*`.</details>
<details><summary>Task 2</summary>`F.col("x").cast("int")`. For `try_cast`, look at `F.expr`, or the `try_cast` method on a column.</details>
<details><summary>Task 5c</summary>Python's `&` binds tighter than `==` and `>`.</details>
<details><summary>Task 6d</summary>Look up `eqNullSafe`, or combine `isNull()` with `|`.</details>
