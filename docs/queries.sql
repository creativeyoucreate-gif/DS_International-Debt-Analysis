-- International Debt Analysis: SQL queries (PostgreSQL)

-- Q1. Distinct country names
SELECT DISTINCT country_name
FROM countries
ORDER BY country_name;

-- Q2. Number of countries
SELECT COUNT(*) AS total_countries
FROM countries;

-- Q3. Number of indicators
SELECT COUNT(*) AS total_indicators
FROM indicators;

-- Q4. First 10 records
SELECT *
FROM debt_data
ORDER BY country_code, indicator_code, year
LIMIT 10;

-- Q5. Total global debt, 2023 (USD)
SELECT SUM(value) AS total_global_debt_usd
FROM debt_data
WHERE indicator_code = 'DT.DOD.DECT.CD' AND year = 2023;

-- Q6. Unique indicator names
SELECT DISTINCT indicator_name
FROM indicators
ORDER BY indicator_name;

-- Q7. Records per country
SELECT c.country_name, COUNT(*) AS records
FROM debt_data d
JOIN countries c ON d.country_code = c.country_code
GROUP BY c.country_name
ORDER BY records DESC;

-- Q8. Countries with debt above 1 billion USD, 2023
SELECT c.country_name, d.value AS debt_usd
FROM debt_data d
JOIN countries c ON d.country_code = c.country_code
WHERE d.indicator_code = 'DT.DOD.DECT.CD'
  AND d.year = 2023
  AND d.value > 1000000000
ORDER BY d.value DESC;

-- Q9. Min, max and average debt, 2023 (USD)
SELECT MIN(value) AS min_debt,
       MAX(value) AS max_debt,
       AVG(value) AS avg_debt
FROM debt_data
WHERE indicator_code = 'DT.DOD.DECT.CD' AND year = 2023;

-- Q10. Total records in debt_data
SELECT COUNT(*) AS total_records
FROM debt_data;

-- Q11. Total debt for each country, 2023
SELECT c.country_name, SUM(d.value) AS total_debt
FROM debt_data d
JOIN countries c ON d.country_code = c.country_code
WHERE d.indicator_code = 'DT.DOD.DECT.CD' AND d.year = 2023
GROUP BY c.country_name
ORDER BY total_debt DESC;

-- Q12. Top 10 countries by total debt, 2023
SELECT c.country_name, SUM(d.value) AS total_debt
FROM debt_data d
JOIN countries c ON d.country_code = c.country_code
WHERE d.indicator_code = 'DT.DOD.DECT.CD' AND d.year = 2023
GROUP BY c.country_name
ORDER BY total_debt DESC
LIMIT 10;

-- Q13. Average debt per country, 2023
SELECT AVG(country_debt) AS avg_debt_per_country
FROM (
    SELECT country_code, SUM(value) AS country_debt
    FROM debt_data
    WHERE indicator_code = 'DT.DOD.DECT.CD' AND year = 2023
    GROUP BY country_code
) AS t;

-- Q14. Total debt for each debt-stock indicator, 2023
SELECT i.indicator_name, SUM(d.value) AS total_debt
FROM debt_data d
JOIN indicators i ON d.indicator_code = i.indicator_code
WHERE i.topic = 'Economic Policy & Debt: External debt: Debt outstanding'
  AND i.is_usd = 1
  AND d.year = 2023
GROUP BY i.indicator_name
ORDER BY total_debt DESC;

-- Q15. Indicator with the highest total debt (excluding the grand total), 2023
SELECT i.indicator_name, SUM(d.value) AS total_debt
FROM debt_data d
JOIN indicators i ON d.indicator_code = i.indicator_code
WHERE i.topic = 'Economic Policy & Debt: External debt: Debt outstanding'
  AND i.is_usd = 1
  AND d.year = 2023
  AND d.indicator_code <> 'DT.DOD.DECT.CD'
GROUP BY i.indicator_name
ORDER BY total_debt DESC
LIMIT 1;

-- Q16. Country with the lowest total debt, 2023
SELECT c.country_name, SUM(d.value) AS total_debt
FROM debt_data d
JOIN countries c ON d.country_code = c.country_code
WHERE d.indicator_code = 'DT.DOD.DECT.CD' AND d.year = 2023
GROUP BY c.country_name
ORDER BY total_debt ASC
LIMIT 1;

-- Q17. Total debt per country and indicator, 2023
SELECT c.country_name, i.indicator_name, SUM(d.value) AS total_debt
FROM debt_data d
JOIN countries c  ON d.country_code   = c.country_code
JOIN indicators i ON d.indicator_code = i.indicator_code
WHERE i.topic = 'Economic Policy & Debt: External debt: Debt outstanding'
  AND i.is_usd = 1
  AND d.year = 2023
GROUP BY c.country_name, i.indicator_name
ORDER BY c.country_name, total_debt DESC;

-- Q18. Number of indicators per country
SELECT c.country_name, COUNT(DISTINCT d.indicator_code) AS indicator_count
FROM debt_data d
JOIN countries c ON d.country_code = c.country_code
GROUP BY c.country_name
ORDER BY indicator_count DESC;

-- Q19. Countries with debt above the average, 2023
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
ORDER BY total_debt DESC;

-- Q20. Country ranking by total debt, 2023
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
ORDER BY debt_rank;

-- Q21. Top 5 debt indicators, 2023
SELECT i.indicator_name, SUM(d.value) AS total_debt
FROM debt_data d
JOIN indicators i ON d.indicator_code = i.indicator_code
WHERE i.topic = 'Economic Policy & Debt: External debt: Debt outstanding'
  AND i.is_usd = 1
  AND d.year = 2023
  AND d.indicator_code <> 'DT.DOD.DECT.CD'
GROUP BY i.indicator_name
ORDER BY total_debt DESC
LIMIT 5;

-- Q22. Each country's share of global debt, 2023
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
ORDER BY total_debt DESC;

-- Q23. Top 3 countries for each debt indicator, 2023
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
ORDER BY indicator_name, rnk;

-- Q24. Max minus min total debt per country, 2000-2024
SELECT c.country_name,
       MAX(d.value) AS max_debt,
       MIN(d.value) AS min_debt,
       MAX(d.value) - MIN(d.value) AS difference
FROM debt_data d
JOIN countries c ON d.country_code = c.country_code
WHERE d.indicator_code = 'DT.DOD.DECT.CD'
GROUP BY c.country_name
ORDER BY difference DESC;

-- Q25. Create view: top 10 countries by debt
CREATE OR REPLACE VIEW top10_debt_countries AS
SELECT c.country_name, SUM(d.value) AS total_debt
FROM debt_data d
JOIN countries c ON d.country_code = c.country_code
WHERE d.indicator_code = 'DT.DOD.DECT.CD' AND d.year = 2023
GROUP BY c.country_name
ORDER BY total_debt DESC
LIMIT 10;

-- Q25. View: top10_debt_countries
SELECT * FROM top10_debt_countries;

-- Q26. Debt category for each country, 2023
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
ORDER BY total_debt DESC;

-- Q26b. Number of countries in each category
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
ORDER BY countries DESC;

-- Q27. Cumulative debt per country over the years
SELECT c.country_name, d.year, d.value AS debt_usd,
       SUM(d.value) OVER (PARTITION BY c.country_name ORDER BY d.year) AS cumulative_debt
FROM debt_data d
JOIN countries c ON d.country_code = c.country_code
WHERE d.indicator_code = 'DT.DOD.DECT.CD'
ORDER BY c.country_name, d.year;

-- Q28. Indicators with above-average debt, 2023
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
ORDER BY avg_debt DESC;

-- Q29. Countries with more than 5% of global debt, 2023
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
ORDER BY pct_of_global DESC;

-- Q30. Dominant debt indicator for each country, 2023
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
ORDER BY value DESC;

