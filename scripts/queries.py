

from pathlib import Path
import textwrap

import pandas as pd
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL

# ---------- Settings (same as the other scripts) ----------
DB_USER     = "postgres"
DB_PASSWORD = "KAvi"
DB_HOST     = "localhost"
DB_PORT     = 5432
DB_NAME     = "intl_debt"

url = URL.create("postgresql+psycopg2", username=DB_USER, password=DB_PASSWORD,
                 host=DB_HOST, port=DB_PORT, database=DB_NAME)
engine = create_engine(url)

SQL_FILE = Path(__file__).resolve().parent.parent / "docs" / "queries.sql"
SQL_FILE.write_text("-- International Debt Analysis: SQL queries (PostgreSQL)\n\n", encoding="utf-8")


def save_sql(title, sql):
    """Append one query to docs/queries.sql."""
    with open(SQL_FILE, "a", encoding="utf-8") as f:
        f.write(f"-- {title}\n{textwrap.dedent(sql).strip()};\n\n")

pd.set_option("display.float_format", "{:,.2f}".format)   # readable big numbers
pd.set_option("display.width", 200)



def run(title, sql):
    """Run one SQL query and print the number of rows and the first 10."""
    save_sql(title, sql)
    with engine.connect() as conn:
        df = pd.read_sql(text(sql), conn)
    print("\n" + "=" * 70)
    print(title)
    print("=" * 70)
    print(f"({len(df)} rows)")
    print(df.head(10).to_string(index=False))
    return df


# ======================= BASIC QUERIES =======================

# Q1. All distinct country names
run("Q1. Distinct country names", """
    SELECT DISTINCT country_name
    FROM countries
    ORDER BY country_name
""")

# Q2. Total number of countries
run("Q2. Number of countries", """
    SELECT COUNT(*) AS total_countries
    FROM countries
""")

# Q3. Total number of indicators
run("Q3. Number of indicators", """
    SELECT COUNT(*) AS total_indicators
    FROM indicators
""")

# Q4. First 10 records of the dataset
run("Q4. First 10 records", """
    SELECT *
    FROM debt_data
    ORDER BY country_code, indicator_code, year
    LIMIT 10
""")

# Q5. Total global debt (total external debt stock, 2023)
run("Q5. Total global debt, 2023 (USD)", """
    SELECT SUM(value) AS total_global_debt_usd
    FROM debt_data
    WHERE indicator_code = 'DT.DOD.DECT.CD' AND year = 2023
""")

# Q6. All unique indicator names
run("Q6. Unique indicator names", """
    SELECT DISTINCT indicator_name
    FROM indicators
    ORDER BY indicator_name
""")

# Q7. Number of records for each country
run("Q7. Records per country", """
    SELECT c.country_name, COUNT(*) AS records
    FROM debt_data d
    JOIN countries c ON d.country_code = c.country_code
    GROUP BY c.country_name
    ORDER BY records DESC
""")

# Q8. Countries with debt greater than 1 billion USD (2023)
run("Q8. Countries with debt above 1 billion USD, 2023", """
    SELECT c.country_name, d.value AS debt_usd
    FROM debt_data d
    JOIN countries c ON d.country_code = c.country_code
    WHERE d.indicator_code = 'DT.DOD.DECT.CD'
      AND d.year = 2023
      AND d.value > 1000000000
    ORDER BY d.value DESC
""")

# Q9. Minimum, maximum and average debt (2023)
run("Q9. Min, max and average debt, 2023 (USD)", """
    SELECT MIN(value) AS min_debt,
           MAX(value) AS max_debt,
           AVG(value) AS avg_debt
    FROM debt_data
    WHERE indicator_code = 'DT.DOD.DECT.CD' AND year = 2023
""")

# Q10. Total number of records in the dataset
run("Q10. Total records in debt_data", """
    SELECT COUNT(*) AS total_records
    FROM debt_data
""")

# ======================= INTERMEDIATE QUERIES =======================

# Q11. Total debt for each country (2023)
run("Q11. Total debt for each country, 2023", """
    SELECT c.country_name, SUM(d.value) AS total_debt
    FROM debt_data d
    JOIN countries c ON d.country_code = c.country_code
    WHERE d.indicator_code = 'DT.DOD.DECT.CD' AND d.year = 2023
    GROUP BY c.country_name
    ORDER BY total_debt DESC
""")

# Q12. Top 10 countries with the highest total debt
run("Q12. Top 10 countries by total debt, 2023", """
    SELECT c.country_name, SUM(d.value) AS total_debt
    FROM debt_data d
    JOIN countries c ON d.country_code = c.country_code
    WHERE d.indicator_code = 'DT.DOD.DECT.CD' AND d.year = 2023
    GROUP BY c.country_name
    ORDER BY total_debt DESC
    LIMIT 10
""")

# Q13. Average debt per country
run("Q13. Average debt per country, 2023", """
    SELECT AVG(country_debt) AS avg_debt_per_country
    FROM (
        SELECT country_code, SUM(value) AS country_debt
        FROM debt_data
        WHERE indicator_code = 'DT.DOD.DECT.CD' AND year = 2023
        GROUP BY country_code
    ) AS t
""")

# Q14. Total debt for each indicator (debt-stock indicators, 2023)
run("Q14. Total debt for each debt-stock indicator, 2023", """
    SELECT i.indicator_name, SUM(d.value) AS total_debt
    FROM debt_data d
    JOIN indicators i ON d.indicator_code = i.indicator_code
    WHERE i.topic = 'Economic Policy & Debt: External debt: Debt outstanding'
      AND i.is_usd = 1
      AND d.year = 2023
    GROUP BY i.indicator_name
    ORDER BY total_debt DESC
""")

# Q15. Indicator contributing the highest total debt
# We skip the grand total (DT.DOD.DECT.CD), because it is the sum of the others.
run("Q15. Indicator with the highest total debt (excluding the grand total), 2023", """
    SELECT i.indicator_name, SUM(d.value) AS total_debt
    FROM debt_data d
    JOIN indicators i ON d.indicator_code = i.indicator_code
    WHERE i.topic = 'Economic Policy & Debt: External debt: Debt outstanding'
      AND i.is_usd = 1
      AND d.year = 2023
      AND d.indicator_code <> 'DT.DOD.DECT.CD'
    GROUP BY i.indicator_name
    ORDER BY total_debt DESC
    LIMIT 1
""")

# Q16. Country with the lowest total debt
run("Q16. Country with the lowest total debt, 2023", """
    SELECT c.country_name, SUM(d.value) AS total_debt
    FROM debt_data d
    JOIN countries c ON d.country_code = c.country_code
    WHERE d.indicator_code = 'DT.DOD.DECT.CD' AND d.year = 2023
    GROUP BY c.country_name
    ORDER BY total_debt ASC
    LIMIT 1
""")

# Q17. Total debt for each country and indicator combination
run("Q17. Total debt per country and indicator, 2023", """
    SELECT c.country_name, i.indicator_name, SUM(d.value) AS total_debt
    FROM debt_data d
    JOIN countries c  ON d.country_code   = c.country_code
    JOIN indicators i ON d.indicator_code = i.indicator_code
    WHERE i.topic = 'Economic Policy & Debt: External debt: Debt outstanding'
      AND i.is_usd = 1
      AND d.year = 2023
    GROUP BY c.country_name, i.indicator_name
    ORDER BY c.country_name, total_debt DESC
""")

# Q18. How many indicators each country has
run("Q18. Number of indicators per country", """
    SELECT c.country_name, COUNT(DISTINCT d.indicator_code) AS indicator_count
    FROM debt_data d
    JOIN countries c ON d.country_code = c.country_code
    GROUP BY c.country_name
    ORDER BY indicator_count DESC
""")

# Q19. Countries whose total debt is above the global average
run("Q19. Countries with debt above the average, 2023", """
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
""")

# Q20. Rank countries by total debt (highest to lowest)
run("Q20. Country ranking by total debt, 2023", """
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
""")

# ======================= ADVANCED QUERIES =======================

# Q21. Top 5 indicators contributing most to global debt (2023)
# The grand total (DT.DOD.DECT.CD) is skipped because it is the sum of the others.
run("Q21. Top 5 debt indicators, 2023", """
    SELECT i.indicator_name, SUM(d.value) AS total_debt
    FROM debt_data d
    JOIN indicators i ON d.indicator_code = i.indicator_code
    WHERE i.topic = 'Economic Policy & Debt: External debt: Debt outstanding'
      AND i.is_usd = 1
      AND d.year = 2023
      AND d.indicator_code <> 'DT.DOD.DECT.CD'
    GROUP BY i.indicator_name
    ORDER BY total_debt DESC
    LIMIT 5
""")

# Q22. Percentage contribution of each country to total global debt
run("Q22. Each country's share of global debt, 2023", """
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
""")

# Q23. Top 3 countries for each indicator
run("Q23. Top 3 countries for each debt indicator, 2023", """
    WITH ranked AS (
        SELECT i.indicator_name, c.country_name, d.value,
               RANK() OVER (PARTITION BY i.indicator_name ORDER BY d.value DESC) AS rnk
        FROM debt_data d
        JOIN countries c  ON d.country_code   = c.country_code
        JOIN indicators i ON d.indicator_code = i.indicator_code
        WHERE i.topic = 'Economic Policy & Debt: External debt: Debt outstanding'
          AND i.is_usd = 1
          AND d.year = 2023
    )
    SELECT indicator_name, country_name, value, rnk
    FROM ranked
    WHERE rnk <= 3
    ORDER BY indicator_name, rnk
""")

# Q24. Difference between max and min debt for each country (2000-2024)
run("Q24. Max minus min total debt per country, 2000-2024", """
    SELECT c.country_name,
           MAX(d.value) AS max_debt,
           MIN(d.value) AS min_debt,
           MAX(d.value) - MIN(d.value) AS difference
    FROM debt_data d
    JOIN countries c ON d.country_code = c.country_code
    WHERE d.indicator_code = 'DT.DOD.DECT.CD'
    GROUP BY c.country_name
    ORDER BY difference DESC
""")

# Q25. Create a view for the top 10 countries with the highest debt
q25_sql = """
    CREATE OR REPLACE VIEW top10_debt_countries AS
    SELECT c.country_name, SUM(d.value) AS total_debt
    FROM debt_data d
    JOIN countries c ON d.country_code = c.country_code
    WHERE d.indicator_code = 'DT.DOD.DECT.CD' AND d.year = 2023
    GROUP BY c.country_name
    ORDER BY total_debt DESC
    LIMIT 10
"""
with engine.begin() as conn:
    conn.execute(text(q25_sql))
save_sql("Q25. Create view: top 10 countries by debt", q25_sql)
run("Q25. View: top10_debt_countries", "SELECT * FROM top10_debt_countries")

# Q26. Categorize countries: High / Medium / Low debt
# High: 100 billion or more. Medium: 10 to 100 billion. Low: below 10 billion.
run("Q26. Debt category for each country, 2023", """
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
""")

# Q26 (summary): how many countries in each category
run("Q26b. Number of countries in each category", """
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
""")

# Q27. Cumulative debt per country (window function)
q27 = run("Q27. Cumulative debt per country over the years", """
    SELECT c.country_name, d.year, d.value AS debt_usd,
           SUM(d.value) OVER (PARTITION BY c.country_name ORDER BY d.year) AS cumulative_debt
    FROM debt_data d
    JOIN countries c ON d.country_code = c.country_code
    WHERE d.indicator_code = 'DT.DOD.DECT.CD'
    ORDER BY c.country_name, d.year
""")
print(q27[q27["country_name"].str.contains("China")].head(3).to_string(index=False))

# Q28. Indicators whose average debt is above the overall average
run("Q28. Indicators with above-average debt, 2023", """
    WITH debt_values AS (
        SELECT i.indicator_name, d.value
        FROM debt_data d
        JOIN indicators i ON d.indicator_code = i.indicator_code
        WHERE i.topic = 'Economic Policy & Debt: External debt: Debt outstanding'
          AND i.is_usd = 1
          AND d.year = 2023
    )
    SELECT indicator_name, AVG(value) AS avg_debt
    FROM debt_values
    GROUP BY indicator_name
    HAVING AVG(value) > (SELECT AVG(value) FROM debt_values)
    ORDER BY avg_debt DESC
""")

# Q29. Countries contributing more than 5% of global debt
run("Q29. Countries with more than 5% of global debt, 2023", """
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
""")

# Q30. Most dominant indicator for each country (largest debt component)
q30 = run("Q30. Dominant debt indicator for each country, 2023", """
    WITH ranked AS (
        SELECT c.country_name, i.indicator_name, d.value,
               ROW_NUMBER() OVER (PARTITION BY c.country_name
                                  ORDER BY d.value DESC, i.indicator_name) AS rn
        FROM debt_data d
        JOIN countries c  ON d.country_code   = c.country_code
        JOIN indicators i ON d.indicator_code = i.indicator_code
        WHERE i.topic = 'Economic Policy & Debt: External debt: Debt outstanding'
          AND i.is_usd = 1
          AND d.year = 2023
          AND d.indicator_code <> 'DT.DOD.DECT.CD'
    )
    SELECT country_name, indicator_name, value
    FROM ranked
    WHERE rn = 1
    ORDER BY value DESC
""")
print(q30["indicator_name"].value_counts().head(5))