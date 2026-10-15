from pathlib import Path

import pandas as pd
from sqlalchemy import text

from db_config import engine

DATA = Path(__file__).resolve().parent.parent / "data"


# ---------- Step 1: read the clean CSV files ----------
countries  = pd.read_csv(DATA / "clean_countries.csv")
indicators = pd.read_csv(DATA / "clean_indicators.csv")
debt_data  = pd.read_csv(DATA / "clean_debt_data.csv")
print("CSV files read:", len(countries), len(indicators), len(debt_data))


# ---------- Step 2: empty the tables so you can re-run safely ----------
with engine.begin() as conn:
    conn.execute(text("TRUNCATE TABLE debt_data, indicators, countries"))


# ---------- Step 3: insert the data ----------
# Order matters: the two small tables first, because debt_data refers to them.
countries.to_sql("countries", engine, if_exists="append", index=False)
print("countries inserted")

indicators.to_sql("indicators", engine, if_exists="append", index=False)
print("indicators inserted")

debt_data.to_sql("debt_data", engine, if_exists="append", index=False,
                 chunksize=10000, method="multi")
print("debt_data inserted")


# ---------- Step 4: check the row counts ----------
with engine.connect() as conn:
    for table in ["countries", "indicators", "debt_data"]:
        n = conn.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
        print(f"{table}: {n} rows")
