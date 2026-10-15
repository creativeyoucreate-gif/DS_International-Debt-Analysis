# International Debt Analysis

A beginner-friendly data project that studies the **external debt of 120 countries** using World Bank data. It covers the full workflow: cleaning the data, exploring it, storing it in a PostgreSQL database, answering 30 SQL questions, and showing everything in an interactive Streamlit dashboard.

## What is "external debt"?

External debt is money a country owes to lenders outside the country (foreign banks, other governments, institutions like the IMF). In this project the main measure is **total external debt stock in current US dollars** (indicator code `DT.DOD.DECT.CD`), mostly for the year **2023**.

## Data source

World Bank, **International Debt Statistics (IDS)**, last updated 12/03/2025. Download the raw files from the World Bank website and place them in the `data/` folder.

## Project structure

```
project/
├── data/
│   ├── IDS_ALLCountries_Data.csv      # raw: debt figures (wide format, one column per year)
│   ├── IDS_CountryMetaData.csv        # raw: country details (region, income group)
│   ├── IDS_SeriesMetaData.csv         # raw: indicator details (topic, definition)
│   ├── IDS_FootNoteMetaData.csv       # raw: footnotes
│   ├── Country-Series_-_Metadata.csv  # raw: country/series notes
│   ├── clean_countries.csv            # cleaned: one row per country
│   ├── clean_indicators.csv           # cleaned: one row per indicator
│   └── clean_debt_data.csv            # cleaned: country + indicator + year + value
├── notebooks/
│   ├── 01_data_loading.ipynb          # load and look at the raw files
│   ├── 02_data_cleaning.ipynb         # clean the data and save the clean CSVs
│   └── 03_eda.ipynb                   # exploratory data analysis and charts
├── scripts/
│   ├── db_config.py                   # database connection settings
│   ├── db_setup.py                    # creates the database and the 3 tables
│   ├── insert_data.py                 # loads the clean CSVs into PostgreSQL
│   ├── queries.py                     # the 30 SQL questions (also rewrites queries.sql)
│   └── dashboard_app.py               # the Streamlit dashboard
├── docs/
│   ├── EDA_report.md                  # written report of the findings
│   └── queries.sql                    # all SQL queries in one file
├── requirements.txt                   # Python packages needed
└── README.md
```

## How the project flows

```
Raw CSV files  ->  Notebooks 01-03  ->  Clean CSV files  ->  PostgreSQL  ->  SQL queries + Dashboard
```

1. **Load** the raw files (notebook 01).
2. **Clean** them and save three tidy tables (notebook 02).
3. **Explore** the data with tables and charts (notebook 03, summarized in `EDA_report.md`).
4. **Store** the clean tables in PostgreSQL (`db_setup.py`, `insert_data.py`).
5. **Query** the data with 30 SQL questions (`queries.py`).
6. **Show** the results in a dashboard (`dashboard_app.py`).

## Data cleaning in short

| Problem | Fix |
|---|---|
| Files are not UTF-8 | Read them with `latin-1` encoding |
| Blank and footer rows at the bottom | Dropped rows with no Country Code |
| Hidden spaces in country codes | Trimmed with `str.strip()` |
| 14 groups such as "Low income" mixed in with countries | Kept only entries that have a Region (120 countries) |
| One column per year (wide format) | Reshaped to one row per year with `melt()` |
| Empty values and projections (2025-2032) | Removed them and kept 2000-2024 |
| Duplicate rows | Checked, none found |

Removing the groups matters because they are already totals of many countries. Keeping them would count the same debt twice.

## The database

PostgreSQL database `intl_debt` with three tables:

| Table | What it holds | Key |
|---|---|---|
| `countries` | country name, region, income group | `country_code` |
| `indicators` | indicator name, topic, `is_usd` flag | `indicator_code` |
| `debt_data` | the values: country + indicator + year + value | all three together |

## How to run it

### 1. Install the tools

- Python 3.8 or newer
- PostgreSQL (running on `localhost`, port `5432`)

### 2. Install the Python packages

```
pip install -r requirements.txt
```

### 3. Set your database password

The scripts read the password from an environment variable called `DB_PASSWORD`.

- Windows (Command Prompt): `set DB_PASSWORD=your_password`
- Mac / Linux: `export DB_PASSWORD=your_password`

The user is `postgres` and the database name is `intl_debt` (you can change these in `scripts/db_config.py`).

### 4. Create the cleaned data

Run the notebooks in order: `01_data_loading`, `02_data_cleaning`, `03_eda`.
This creates the three `clean_*.csv` files in `data/`. (Ready-made copies are already included.)

### 5. Build the database

```
python scripts/db_setup.py
python scripts/insert_data.py
```

> **Warning:** `db_setup.py` deletes and recreates the three tables, and `insert_data.py` empties them before loading. Re-running them replaces any data already there.

### 6. Start the dashboard

```
streamlit run scripts/dashboard_app.py
```

Your browser will open the dashboard.

### 7. (Optional) Regenerate the SQL file

```
python scripts/queries.py
```

This rewrites `docs/queries.sql` with all the queries.

## The dashboard

Use the sidebar to pick a **year** and the **regions** to include. Then explore five tabs:

| Tab | What you see |
|---|---|
| Overview | Top countries, debt by region and income group, debt over time |
| Country explorer | Pick a country to see its debt history and biggest debt components |
| Indicators | The largest debt indicators across all countries |
| Data | A table of the data with a CSV download button |
| SQL Questions | Pick any of the 30 questions, see the result and the SQL |

## SQL questions

`queries.py` holds 30 questions in three levels:

- **Basic (Q1-Q10):** counts, distinct values, totals, min / max / average
- **Intermediate (Q11-Q20):** joins, grouping, subqueries, ranking
- **Advanced (Q21-Q30):** percentages of the total, window functions, a view (`top10_debt_countries`), CASE categories, cumulative sums

## Key findings (2023)

- Total external debt of the 120 countries: **8.84 trillion USD**
- The **top 5 countries hold 54.3%** of the total. **China alone holds 27.7%** (about 2,450 bn USD).
- The **median country owes 12.5 bn**, while the mean is 73.7 bn. A few very large debtors pull the average up.
- **East Asia & Pacific** has the most debt (3,420 bn), followed by Latin America & Caribbean.
- Total debt grew about **4.8 times** between 2000 and 2023, fastest during 2010-2020.
- **Long-term external debt** is the largest debt component.

See `docs/EDA_report.md` for the full report.

## Limitations

- Values are in current US dollars, so they are not adjusted for inflation or country size.
- Debt indicators overlap (for example, long-term debt includes public and private parts), so they should not be added together.
- Only external debt is covered, not money a country owes to its own citizens and banks.
- Mostly low- and middle-income countries are included.
- High debt does not always mean high risk. A big economy can carry big debt more easily.

## Ideas for next steps

- Compare debt to the size of the economy (a debt-to-GNI ratio) to find the most heavily indebted countries for their size.
- Add debt service payments to see whether repayments are affordable.

## Tools used

Python, pandas, Plotly, Streamlit, SQLAlchemy, PostgreSQL, Jupyter.
