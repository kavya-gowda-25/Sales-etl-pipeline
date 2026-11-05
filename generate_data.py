"""Generate a small, deliberately messy, synthetic sales dataset.

The data is fake. It is created so the ETL pipeline has realistic problems to
fix: duplicate rows, missing values, inconsistent text and invalid dates.

Usage:
    python generate_data.py
"""
from pathlib import Path

import numpy as np
import pandas as pd

SEED = 42
N_ROWS = 2000
OUT_FILE = Path("data/raw_sales.csv")

PRODUCTS = {
    "Laptop": 799.0,
    "Phone": 549.0,
    "Headphones": 89.0,
    "Monitor": 229.0,
    "Keyboard": 49.0,
    "Webcam": 59.0,
}
CITIES = ["Berlin", "Munich", "Hamburg", "Cologne", "Frankfurt"]


def main() -> None:
    rng = np.random.default_rng(SEED)

    dates = pd.to_datetime("2025-01-01") + pd.to_timedelta(rng.integers(0, 365, N_ROWS), unit="D")
    product = rng.choice(list(PRODUCTS), N_ROWS)
    df = pd.DataFrame(
        {
            "order_id": np.arange(1, N_ROWS + 1),
            "order_date": dates.strftime("%Y-%m-%d"),
            "customer_id": rng.integers(1000, 1300, N_ROWS),
            "city": rng.choice(CITIES, N_ROWS),
            "product": product,
            "quantity": rng.integers(1, 6, N_ROWS),
            "unit_price": [PRODUCTS[p] for p in product],
        }
    )

    # --- inject data quality problems ---
    # 1. inconsistent text (lower case, extra spaces)
    idx = rng.choice(df.index, 150, replace=False)
    df.loc[idx, "city"] = df.loc[idx, "city"].str.lower().add("  ")
    # 2. missing values
    df.loc[rng.choice(df.index, 60, replace=False), "quantity"] = np.nan
    df.loc[rng.choice(df.index, 40, replace=False), "city"] = np.nan
    # 3. invalid dates
    df.loc[rng.choice(df.index, 25, replace=False), "order_date"] = "not-a-date"
    # 4. negative quantities (data entry errors)
    df.loc[rng.choice(df.index, 20, replace=False), "quantity"] = -1
    # 5. duplicate rows
    df = pd.concat([df, df.sample(80, random_state=SEED)], ignore_index=True)

    OUT_FILE.parent.mkdir(exist_ok=True)
    df.sample(frac=1, random_state=SEED).to_csv(OUT_FILE, index=False)
    print(f"Wrote {len(df)} rows to {OUT_FILE}")


if __name__ == "__main__":
    main()
