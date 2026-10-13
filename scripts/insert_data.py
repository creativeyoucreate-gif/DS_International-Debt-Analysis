from pathlib import Path

import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL

# ---------- Settings (same as db_setup.py) ----------
DB_USER     = "postgres"
DB_PASSWORD = "KAvi"
DB_HOST     = "localhost"
DB_PORT     = 5432
DB_NAME     = "intl_debt"

# Build the data folder path from this file's location, so the script works
# no matter which folder you run it from.
DATA = Path(__file__).resolve().parent.parent / "data"


# ---------- Step 1: read the clean CSV files ----------
countries  = pd.read_csv(DATA / "clean_countries.csv")
indicators = pd.read_csv(DATA / "clean_indicators.csv")
debt_data  = pd.read_csv(DATA / "clean_debt_data.csv")
print("CSV files read:", len(countries), len(indicators), len(debt_data))


# ---------- Step 2: connect to PostgreSQL ----------
url = URL.create("postgresql+psycopg2", username=DB_USER, password=DB_PASSWORD,
                 host=DB_HOST, port=DB_PORT, database=DB_NAME)
engine = create_engine(url)


# ---------- Step 3: empty the tables so you can re-run safely ----------
with engine.begin() as conn:
    conn.execute(text("TRUNCATE TABLE debt_data, indicators, countries"))


# ---------- Step 4: insert the data ----------
# Order matters: the two small tables first, because debt_data refers to them.
countries.to_sql("countries", engine, if_exists="append", index=False)
print("countries inserted")

indicators.to_sql("indicators", engine, if_exists="append", index=False)
print("indicators inserted")

debt_data.to_sql("debt_data", engine, if_exists="append", index=False,
                 chunksize=10000, method="multi")
print("debt_data inserted")


# ---------- Step 5: check the row counts ----------
with engine.connect() as conn:
    for table in ["countries", "indicators", "debt_data"]:
        n = conn.execute(text(f"SELECT COUNT(*) FROM {table}")).scalar()
        print(f"{table}: {n} rows")