# Sales ETL Pipeline (Python + SQLite)

A small data engineering project by **Kavya L K**, M.Sc. Cognitive Systems, University of Potsdam.

It takes a messy sales CSV, cleans and validates it with pandas, loads it into a SQLite database, and answers business questions with SQL.

> The dataset is **synthetic**. `generate_data.py` creates it with deliberate data quality problems so the pipeline has something real to fix.

## What the pipeline does

```
raw_sales.csv  ->  Extract  ->  Transform (clean + validate)  ->  Load (SQLite)  ->  SQL reports + chart
```

| Step | What happens |
|------|--------------|
| Extract | Reads the raw CSV (2,080 rows) |
| Transform | Removes duplicates, trims and normalises text, drops missing values, invalid dates and negative quantities, adds `revenue` and `order_month` |
| Validate | Asserts unique order IDs, positive quantities and prices, and no missing values |
| Load | Writes a `sales` table with indexes into `output/sales.db` |
| Report | Runs the named queries in `queries.sql` and saves `output/monthly_revenue.png` |

Every cleaning rule is logged with the number of rows it affected (for example: 80 duplicates removed, 1,860 of 2,080 rows kept).

## Project structure

```
.
├── generate_data.py     # creates the messy synthetic dataset
├── etl_pipeline.py      # extract, transform, load, report
├── queries.sql          # named SQL queries
├── requirements.txt
└── output/
    └── monthly_revenue.png
```

## How to run

```bash
python -m venv .venv
source .venv/bin/activate        # Windows: .venv\Scripts\activate
pip install -r requirements.txt

python generate_data.py          # creates data/raw_sales.csv
python etl_pipeline.py           # runs the pipeline and prints the reports
```

## Example output

Revenue by city (after cleaning):

| city | revenue | orders |
|------|---------|--------|
| Berlin | 348,037 | 401 |
| Munich | 345,898 | 393 |
| Cologne | 337,289 | 361 |
| Frankfurt | 311,756 | 339 |
| Hamburg | 284,335 | 366 |

![Monthly revenue](output/monthly_revenue.png)

## Skills demonstrated

Python, pandas, NumPy, SQL, SQLite, data cleaning, data validation, logging, Matplotlib.

## Possible next steps

- Add unit tests for each cleaning rule with pytest
- Schedule the pipeline with cron or Apache Airflow
- Split `sales` into fact and dimension tables (star schema)
- Containerise with Docker

## Author

Kavya L K | [GitHub](https://github.com/kavya-gowda-25) | kav9793@gmail.com
