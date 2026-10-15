"""
queries.py - the 30 SQL questions for the International Debt Analysis project.

Two ways to use this file:
  1. Imported by dashboard_app.py  -> use QUERIES and run_query()
  2. Run directly: python scripts/queries.py -> rewrites docs/queries.sql
"""
import textwrap
from pathlib import Path

import pandas as pd
from sqlalchemy import text

from db_config import engine

SQL_FILE = Path(__file__).resolve().parent.parent / "docs" / "queries.sql"

# Reused filter: only the "debt outstanding" indicators, in USD
TOPIC = "Economic Policy & Debt: External debt: Debt outstanding"

# Q25 needs a view to exist first. It is created once, when needed.
VIEW_SQL = """
    CREATE OR REPLACE VIEW top10_debt_countries AS
    SELECT c.country_name, SUM(d.value) AS total_debt
    FROM debt_data d
    JOIN countries c ON d.country_code = c.country_code
    WHERE d.indicator_code = 'DT.DOD.DECT.CD' AND d.year = 2023
    GROUP BY c.country_name
    ORDER BY total_debt DESC
    LIMIT 10
"""

# ---------- All queries: {title: sql} ----------
QUERIES = {}

# ======================= BASIC QUERIES =======================
QUERIES["Q1. Distinct country names"] = """
    SELECT DISTINCT country_name
    FROM countries
    ORDER BY country_name
"""

QUERIES["Q2. Number of countries"] = """
    SELECT COUNT(*) AS total_countries
    FROM countries
"""

QUERIES["Q3. Number of indicators"] = """
    SELECT COUNT(*) AS total_indicators
    FROM indicators
"""

QUERIES["Q4. First 10 records"] = """
    SELECT *
    FROM debt_data
    ORDER BY country_code, indicator_code, year
    LIMIT 10
"""

QUERIES["Q5. Total global debt, 2023 (USD)"] = """
    SELECT SUM(value) AS total_global_debt_usd
    FROM debt_data
    WHERE indicator_code = 'DT.DOD.DECT.CD' AND year = 2023
"""

QUERIES["Q6. Unique indicator names"] = """
    SELECT DISTINCT indicator_name
    FROM indicators
    ORDER BY indicator_name
"""

QUERIES["Q7. Records per country"] = """
    SELECT c.country_name, COUNT(*) AS records
    FROM debt_data d
    JOIN countries c ON d.country_code = c.country_code
    GROUP BY c.country_name
    ORDER BY records DESC
"""

QUERIES["Q8. Countries with debt above 1 billion USD, 2023"] = """
    SELECT c.country_name, d.value AS debt_usd
    FROM debt_data d
    JOIN countries c ON d.country_code = c.country_code
    WHERE d.indicator_code = 'DT.DOD.DECT.CD'
      AND d.year = 2023
      AND d.value > 1000000000
    ORDER BY d.value DESC
"""

QUERIES["Q9. Min, max and average debt, 2023 (USD)"] = """
    SELECT MIN(value) AS min_debt,
           MAX(value) AS max_debt,
           AVG(value) AS avg_debt
    FROM debt_data
    WHERE indicator_code = 'DT.DOD.DECT.CD' AND year = 2023
"""

QUERIES["Q10. Total records in debt_data"] = """
    SELECT COUNT(*) AS total_records
    FROM debt_data
"""

# ======================= INTERMEDIATE QUERIES =======================
QUERIES["Q11. Total debt for each country, 2023"] = """
    SELECT c.country_name, SUM(d.value) AS total_debt
    FROM debt_data d
    JOIN countries c ON d.country_code = c.country_code
    WHERE d.indicator_code = 'DT.DOD.DECT.CD' AND d.year = 2023
    GROUP BY c.country_name
    ORDER BY total_debt DESC
"""

QUERIES["Q12. Top 10 countries by total debt, 2023"] = """
    SELECT c.country_name, SUM(d.value) AS total_debt
    FROM debt_data d
    JOIN countries c ON d.country_code = c.country_code
    WHERE d.indicator_code = 'DT.DOD.DECT.CD' AND d.year = 2023
    GROUP BY c.country_name
    ORDER BY total_debt DESC
    LIMIT 10
"""

QUERIES["Q13. Average debt per country, 2023"] = """
    SELECT AVG(country_debt) AS avg_debt_per_country
    FROM (
        SELECT country_code, SUM(value) AS country_debt
        FROM debt_data
        WHERE indicator_code = 'DT.DOD.DECT.CD' AND year = 2023
        GROUP BY country_code
    ) AS t
"""

QUERIES["Q14. Total debt for each debt-stock indicator, 2023"] = f"""
    SELECT i.indicator_name, SUM(d.value) AS total_debt
    FROM debt_data d
    JOIN indicators i ON d.indicator_code = i.indicator_code
    WHERE i.topic = '{TOPIC}'
      AND i.is_usd = 1
      AND d.year = 2023
    GROUP BY i.indicator_name
    ORDER BY total_debt DESC
"""

# Q15 and Q21 skip the grand total (DT.DOD.DECT.CD) because it is the sum of the others.
QUERIES["Q15. Indicator with the highest total debt (excluding the grand total), 2023"] = f"""
    SELECT i.indicator_name, SUM(d.value) AS total_debt
    FROM debt_data d
    JOIN indicators i ON d.indicator_code = i.indicator_code
    WHERE i.topic = '{TOPIC}'
      AND i.is_usd = 1
      AND d.year = 2023
      AND d.indicator_code <> 'DT.DOD.DECT.CD'
    GROUP BY i.indicator_name
    ORDER BY total_debt DESC
    LIMIT 1
"""

QUERIES["Q16. Country with the lowest total debt, 2023"] = """
    SELECT c.country_name, SUM(d.value) AS total_debt
    FROM debt_data d
    JOIN countries c ON d.country_code = c.country_code
    WHERE d.indicator_code = 'DT.DOD.DECT.CD' AND d.year = 2023
    GROUP BY c.country_name
    ORDER BY total_debt ASC
    LIMIT 1
"""

QUERIES["Q17. Total debt per country and indicator, 2023"] = f"""
    SELECT c.country_name, i.indicator_name, SUM(d.value) AS total_debt
    FROM debt_data d
    JOIN countries c  ON d.country_code   = c.country_code
    JOIN indicators i ON d.indicator_code = i.indicator_code
    WHERE i.topic = '{TOPIC}'
      AND i.is_usd = 1
      AND d.year = 2023
    GROUP BY c.country_name, i.indicator_name
    ORDER BY c.country_name, total_debt DESC
"""

QUERIES["Q18. Number of indicators per country"] = """
    SELECT c.country_name, COUNT(DISTINCT d.indicator_code) AS indicator_count
    FROM debt_data d
    JOIN countries c ON d.country_code = c.country_code
    GROUP BY c.country_name
    ORDER BY indicator_count DESC
"""

QUERIES["Q19. Countries with debt above the average, 2023"] = """
    WITH country_debt AS (
        SELECT c.country_name, SUM(d.value) AS total_debt
        FROM debt_data d
        JOIN countries c ON d.country_code = c.country_code
        WHERE d.indicator_code = 'DT.DOD.DECT.CD' AND d.year = 2023
        GROUP BY c.country_name
    )
    SELECT country_name, total_debt
    FROM country_debt
    WHERE total_debt > (SELECT AVG(total_debt) FROM country_debt)
    ORDER BY total_debt DESC
"""

QUERIES["Q20. Country ranking by total debt, 2023"] = """
    WITH country_debt AS (
        SELECT c.country_name, SUM(d.value) AS total_debt
        FROM debt_data d
        JOIN countries c ON d.country_code = c.country_code
        WHERE d.indicator_code = 'DT.DOD.DECT.CD' AND d.year = 2023
        GROUP BY c.country_name
    )
    SELECT RANK() OVER (ORDER BY total_debt DESC) AS debt_rank,
           country_name, total_debt
    FROM country_debt
    ORDER BY debt_rank
"""

# ======================= ADVANCED QUERIES =======================
QUERIES["Q21. Top 5 debt indicators, 2023"] = f"""
    SELECT i.indicator_name, SUM(d.value) AS total_debt
    FROM debt_data d
    JOIN indicators i ON d.indicator_code = i.indicator_code
    WHERE i.topic = '{TOPIC}'
      AND i.is_usd = 1
      AND d.year = 2023
      AND d.indicator_code <> 'DT.DOD.DECT.CD'
    GROUP BY i.indicator_name
    ORDER BY total_debt DESC
    LIMIT 5
"""

QUERIES["Q22. Each country's share of global debt, 2023"] = """
    WITH country_debt AS (
        SELECT c.country_name, SUM(d.value) AS total_debt
        FROM debt_data d
        JOIN countries c ON d.country_code = c.country_code
        WHERE d.indicator_code = 'DT.DOD.DECT.CD' AND d.year = 2023
        GROUP BY c.country_name
    )
    SELECT country_name,
           total_debt,
           ROUND((total_debt * 100.0 / SUM(total_debt) OVER ())::numeric, 2) AS pct_of_global
    FROM country_debt
    ORDER BY total_debt DESC
"""

QUERIES["Q23. Top 3 countries for each debt indicator, 2023"] = f"""
    WITH ranked AS (
        SELECT i.indicator_name, c.country_name, d.value,
               RANK() OVER (PARTITION BY i.indicator_name ORDER BY d.value DESC) AS rnk
        FROM debt_data d
        JOIN countries c  ON d.country_code   = c.country_code
        JOIN indicators i ON d.indicator_code = i.indicator_code
        WHERE i.topic = '{TOPIC}'
          AND i.is_usd = 1
          AND d.year = 2023
    )
    SELECT indicator_name, country_name, value, rnk
    FROM ranked
    WHERE rnk <= 3
    ORDER BY indicator_name, rnk
"""

QUERIES["Q24. Max minus min total debt per country, 2000-2024"] = """
    SELECT c.country_name,
           MAX(d.value) AS max_debt,
           MIN(d.value) AS min_debt,
           MAX(d.value) - MIN(d.value) AS difference
    FROM debt_data d
    JOIN countries c ON d.country_code = c.country_code
    WHERE d.indicator_code = 'DT.DOD.DECT.CD'
    GROUP BY c.country_name
    ORDER BY difference DESC
"""

# Q25: the view itself is created from VIEW_SQL (see ensure_view below)
QUERIES["Q25. View: top10_debt_countries"] = """
    SELECT * FROM top10_debt_countries
"""

# High: 100 billion or more. Medium: 10 to 100 billion. Low: below 10 billion.
QUERIES["Q26. Debt category for each country, 2023"] = """
    WITH country_debt AS (
        SELECT c.country_name, SUM(d.value) AS total_debt
        FROM debt_data d
        JOIN countries c ON d.country_code = c.country_code
        WHERE d.indicator_code = 'DT.DOD.DECT.CD' AND d.year = 2023
        GROUP BY c.country_name
    )
    SELECT country_name, total_debt,
           CASE WHEN total_debt >= 100000000000 THEN 'High Debt'
                WHEN total_debt >= 10000000000  THEN 'Medium Debt'
                ELSE 'Low Debt' END AS debt_category
    FROM country_debt
    ORDER BY total_debt DESC
"""

QUERIES["Q26b. Number of countries in each category"] = """
    WITH country_debt AS (
        SELECT c.country_name, SUM(d.value) AS total_debt
        FROM debt_data d
        JOIN countries c ON d.country_code = c.country_code
        WHERE d.indicator_code = 'DT.DOD.DECT.CD' AND d.year = 2023
        GROUP BY c.country_name
    )
    SELECT CASE WHEN total_debt >= 100000000000 THEN 'High Debt'
                WHEN total_debt >= 10000000000  THEN 'Medium Debt'
                ELSE 'Low Debt' END AS debt_category,
           COUNT(*) AS countries
    FROM country_debt
    GROUP BY debt_category
    ORDER BY countries DESC
"""

QUERIES["Q27. Cumulative debt per country over the years"] = """
    SELECT c.country_name, d.year, d.value AS debt_usd,
           SUM(d.value) OVER (PARTITION BY c.country_name ORDER BY d.year) AS cumulative_debt
    FROM debt_data d
    JOIN countries c ON d.country_code = c.country_code
    WHERE d.indicator_code = 'DT.DOD.DECT.CD'
    ORDER BY c.country_name, d.year
"""

QUERIES["Q28. Indicators with above-average debt, 2023"] = f"""
    WITH debt_values AS (
        SELECT i.indicator_name, d.value
        FROM debt_data d
        JOIN indicators i ON d.indicator_code = i.indicator_code
        WHERE i.topic = '{TOPIC}'
          AND i.is_usd = 1
          AND d.year = 2023
    )
    SELECT indicator_name, AVG(value) AS avg_debt
    FROM debt_values
    GROUP BY indicator_name
    HAVING AVG(value) > (SELECT AVG(value) FROM debt_values)
    ORDER BY avg_debt DESC
"""

QUERIES["Q29. Countries with more than 5% of global debt, 2023"] = """
    SELECT *
    FROM (
        SELECT c.country_name,
               SUM(d.value) AS total_debt,
               ROUND((SUM(d.value) * 100.0 / SUM(SUM(d.value)) OVER ())::numeric, 2) AS pct_of_global
        FROM debt_data d
        JOIN countries c ON d.country_code = c.country_code
        WHERE d.indicator_code = 'DT.DOD.DECT.CD' AND d.year = 2023
        GROUP BY c.country_name
    ) AS t
    WHERE pct_of_global > 5
    ORDER BY pct_of_global DESC
"""

QUERIES["Q30. Dominant debt indicator for each country, 2023"] = f"""
    WITH ranked AS (
        SELECT c.country_name, i.indicator_name, d.value,
               ROW_NUMBER() OVER (PARTITION BY c.country_name
                                  ORDER BY d.value DESC, i.indicator_name) AS rn
        FROM debt_data d
        JOIN countries c  ON d.country_code   = c.country_code
        JOIN indicators i ON d.indicator_code = i.indicator_code
        WHERE i.topic = '{TOPIC}'
          AND i.is_usd = 1
          AND d.year = 2023
          AND d.indicator_code <> 'DT.DOD.DECT.CD'
    )
    SELECT country_name, indicator_name, value
    FROM ranked
    WHERE rn = 1
    ORDER BY value DESC
"""


# ---------- Helper functions ----------
def ensure_view():
    """Create the Q25 view if it does not exist yet (safe to run many times)."""
    with engine.begin() as conn:
        conn.execute(text(VIEW_SQL))


def run_query(sql):
    """Run one SQL query and return the result as a DataFrame."""
    if "top10_debt_countries" in sql:      # only Q25 needs the view
        ensure_view()
    with engine.connect() as conn:
        return pd.read_sql(text(sql), conn)


def save_all_sql():
    """Write every query into docs/queries.sql (for your documentation)."""
    SQL_FILE.parent.mkdir(exist_ok=True)
    with open(SQL_FILE, "w", encoding="utf-8") as f:
        f.write("-- International Debt Analysis: SQL queries (PostgreSQL)\n\n")
        f.write(f"-- Q25 setup: create view\n{textwrap.dedent(VIEW_SQL).strip()};\n\n")
        for title, sql in QUERIES.items():
            f.write(f"-- {title}\n{textwrap.dedent(sql).strip()};\n\n")


# ---------- Run directly: python scripts/queries.py ----------
if __name__ == "__main__":
    save_all_sql()
    print(f"Written: {SQL_FILE}")
