import psycopg2

from db_config import DB_USER, DB_PASSWORD, DB_HOST, DB_PORT, DB_NAME


# ---------- Step 1: create the database if it does not exist ----------
# We first connect to the default "postgres" database, because we cannot
# connect to a database that does not exist yet.
conn = psycopg2.connect(dbname="postgres", user=DB_USER, password=DB_PASSWORD,
                        host=DB_HOST, port=DB_PORT)
conn.autocommit = True          # CREATE DATABASE cannot run inside a transaction
cur = conn.cursor()

cur.execute("SELECT 1 FROM pg_database WHERE datname = %s", (DB_NAME,))
if cur.fetchone() is None:
    cur.execute(f"CREATE DATABASE {DB_NAME}")
    print(f"Database '{DB_NAME}' created.")
else:
    print(f"Database '{DB_NAME}' already exists.")

cur.close()
conn.close()


# ---------- Step 2: create the tables ----------
conn = psycopg2.connect(dbname=DB_NAME, user=DB_USER, password=DB_PASSWORD,
                        host=DB_HOST, port=DB_PORT)
cur = conn.cursor()

# Drop old tables first so you can safely re-run this file.
# Order matters: debt_data depends on the other two, so it goes first.
# WARNING: this deletes any data already in these tables.
cur.execute("DROP TABLE IF EXISTS debt_data")
cur.execute("DROP TABLE IF EXISTS indicators")
cur.execute("DROP TABLE IF EXISTS countries")

# Table 1: countries (one row per country)
cur.execute("""
    CREATE TABLE countries (
        country_code  VARCHAR(3)   PRIMARY KEY,
        country_name  VARCHAR(100) NOT NULL,
        region        VARCHAR(50),
        income_group  VARCHAR(50)
    )
""")

# Table 2: indicators (one row per indicator)
cur.execute("""
    CREATE TABLE indicators (
        indicator_code  VARCHAR(50) PRIMARY KEY,
        indicator_name  TEXT        NOT NULL,
        topic           TEXT,
        is_usd          SMALLINT
    )
""")

# Table 3: debt_data (one row per country + indicator + year)
cur.execute("""
    CREATE TABLE debt_data (
        country_code    VARCHAR(3)  NOT NULL REFERENCES countries(country_code),
        indicator_code  VARCHAR(50) NOT NULL REFERENCES indicators(indicator_code),
        year            SMALLINT    NOT NULL,
        value           DOUBLE PRECISION NOT NULL,
        PRIMARY KEY (country_code, indicator_code, year)
    )
""")

# An index makes queries that filter by indicator and year much faster
cur.execute("CREATE INDEX idx_debt_indicator_year ON debt_data (indicator_code, year)")

conn.commit()


# ---------- Step 3: check that the tables exist ----------
cur.execute("""
    SELECT table_name FROM information_schema.tables
    WHERE table_schema = 'public' ORDER BY table_name
""")
print("Tables in database:", [row[0] for row in cur.fetchall()])

cur.close()
conn.close()
