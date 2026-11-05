"""Extract -> Transform -> Load pipeline for the raw sales CSV.

Steps:
    1. Extract   read the raw CSV
    2. Transform clean the data and record how many rows each rule removed
    3. Load      write clean data into a SQLite database
    4. Report    run the SQL queries in queries.sql and save a chart

Usage:
    python generate_data.py
    python etl_pipeline.py
"""
import logging
import sqlite3
from pathlib import Path

import matplotlib

matplotlib.use("Agg")  
import matplotlib.pyplot as plt
import pandas as pd

RAW_FILE = Path("data/raw_sales.csv")
DB_FILE = Path("output/sales.db")
CHART_FILE = Path("output/monthly_revenue.png")
QUERIES_FILE = Path("queries.sql")

logging.basicConfig(level=logging.INFO, format="%(asctime)s %(levelname)s %(message)s")
log = logging.getLogger("etl")


def extract(path: Path) -> pd.DataFrame:
    df = pd.read_csv(path)
    log.info("Extracted %d rows from %s", len(df), path)
    return df


def transform(df: pd.DataFrame) -> pd.DataFrame:
    """Clean the data. Each rule logs how many rows it affected."""
    start = len(df)

    df = df.drop_duplicates()
    log.info("Removed %d duplicate rows", start - len(df))

    df["city"] = df["city"].str.strip().str.title()

    before = len(df)
    df = df.dropna(subset=["city", "quantity"])
    log.info("Dropped %d rows with missing city or quantity", before - len(df))

    before = len(df)
    df["order_date"] = pd.to_datetime(df["order_date"], errors="coerce")
    df = df.dropna(subset=["order_date"])
    log.info("Dropped %d rows with invalid dates", before - len(df))

    before = len(df)
    df = df[df["quantity"] > 0]
    log.info("Dropped %d rows with non-positive quantity", before - len(df))

    df = df.astype({"quantity": "int64"})
    df["revenue"] = (df["quantity"] * df["unit_price"]).round(2)
    df["order_month"] = df["order_date"].dt.strftime("%Y-%m")
    df["order_date"] = df["order_date"].dt.strftime("%Y-%m-%d")

    validate(df)
    log.info("Transform finished: %d of %d rows kept", len(df), start)
    return df


def validate(df: pd.DataFrame) -> None:
    """Fail loudly if the cleaned data breaks basic expectations."""
    assert df["order_id"].is_unique, "order_id must be unique"
    assert (df["quantity"] > 0).all(), "quantity must be positive"
    assert (df["unit_price"] > 0).all(), "unit_price must be positive"
    assert df.notna().all().all(), "no missing values allowed after cleaning"


def load(df: pd.DataFrame, db_path: Path) -> None:
    db_path.parent.mkdir(exist_ok=True)
    with sqlite3.connect(db_path) as conn:
        df.to_sql("sales", conn, if_exists="replace", index=False)
        conn.execute("CREATE INDEX IF NOT EXISTS idx_sales_month ON sales(order_month)")
        conn.execute("CREATE INDEX IF NOT EXISTS idx_sales_city ON sales(city)")
    log.info("Loaded %d rows into %s", len(df), db_path)


def run_queries(db_path: Path, queries_file: Path) -> dict[str, pd.DataFrame]:
    """queries.sql holds named queries: '-- name: <name>' above each statement."""
    results, name, buffer = {}, None, []
    with sqlite3.connect(db_path) as conn:
        for line in queries_file.read_text().splitlines() + ["-- name: __end__"]:
            if line.startswith("-- name:"):
                if name and buffer:
                    results[name] = pd.read_sql_query("\n".join(buffer), conn)
                name, buffer = line.split(":", 1)[1].strip(), []
            elif name:
                buffer.append(line)
    return results


def save_chart(monthly: pd.DataFrame, path: Path) -> None:
    fig, ax = plt.subplots(figsize=(9, 4.5))
    ax.plot(monthly["order_month"], monthly["revenue"], marker="o")
    ax.set_title("Monthly revenue (synthetic data)")
    ax.set_xlabel("Month")
    ax.set_ylabel("Revenue (EUR)")
    ax.tick_params(axis="x", rotation=45)
    ax.grid(alpha=0.3)
    fig.tight_layout()
    fig.savefig(path, dpi=150)
    plt.close(fig)
    log.info("Saved chart to %s", path)


def main() -> None:
    df = extract(RAW_FILE)
    clean = transform(df)
    load(clean, DB_FILE)

    results = run_queries(DB_FILE, QUERIES_FILE)
    for name, table in results.items():
        print(f"\n=== {name} ===")
        print(table.to_string(index=False))
    save_chart(results["monthly_revenue"], CHART_FILE)


if __name__ == "__main__":
    main()
