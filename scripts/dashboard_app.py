import pandas as pd
import plotly.express as px
import streamlit as st
from sqlalchemy import text

from db_config import engine
from queries import QUERIES, TOPIC, run_query

DEBT_CODE = "DT.DOD.DECT.CD"   # total external debt stock (US$)

st.set_page_config(page_title="International Debt Dashboard", layout="wide")

# Plain-English text shown in the SQL Questions list (keyed by query number)
QUESTIONS = {
    "Q1": "List all distinct country names",
    "Q2": "Count the total number of countries available",
    "Q3": "Count the total number of indicators available",
    "Q4": "Show the first 10 records of the dataset",
    "Q5": "What is the total global debt in 2023?",
    "Q6": "List all unique indicator names",
    "Q7": "How many records does each country have?",
    "Q8": "Which countries have debt above 1 billion USD (2023)?",
    "Q9": "What are the minimum, maximum and average debt (2023)?",
    "Q10": "How many records are there in the dataset?",
    "Q11": "What is the total debt of each country (2023)?",
    "Q12": "Which are the top 10 countries with the highest debt?",
    "Q13": "What is the average debt per country?",
    "Q14": "What is the total debt for each indicator?",
    "Q15": "Which indicator contributes the highest total debt?",
    "Q16": "Which country has the lowest total debt?",
    "Q17": "What is the total debt for each country and indicator?",
    "Q18": "How many indicators does each country have?",
    "Q19": "Which countries have debt above the global average?",
    "Q20": "Rank countries by total debt (highest to lowest)",
    "Q21": "Which 5 indicators contribute most to global debt?",
    "Q22": "What percentage of global debt does each country contribute?",
    "Q23": "Who are the top 3 countries for each indicator?",
    "Q24": "What is the difference between max and min debt for each country (2000-2024)?",
    "Q25": "Show the top 10 highest-debt countries (SQL view)",
    "Q26": "Categorize countries as High / Medium / Low debt",
    "Q26b": "How many countries are in each debt category?",
    "Q27": "What is the cumulative debt of each country over the years?",
    "Q28": "Which indicators have above-average debt?",
    "Q29": "Which countries contribute more than 5% of global debt?",
    "Q30": "What is the most dominant debt indicator for each country?",
}


# ---------- Database helper ----------
@st.cache_data                          # remember results so clicks stay fast
def load(sql, params=None):
    with engine.connect() as conn:
        return pd.read_sql(text(sql), conn, params=params)


# ---------- Load the lists for the filters ----------
years = load("""
    SELECT DISTINCT year FROM debt_data
    WHERE indicator_code = :code ORDER BY year
""", {"code": DEBT_CODE})["year"].tolist()

all_regions = load("SELECT DISTINCT region FROM countries ORDER BY region")["region"].tolist()


# ---------- Sidebar filters ----------
st.sidebar.header("Filters")
default_index = years.index(2023) if 2023 in years else len(years) - 1
year = st.sidebar.selectbox("Year", years, index=default_index)
regions = st.sidebar.multiselect("Regions", all_regions, default=all_regions)

if not regions:
    st.warning("Pick at least one region in the sidebar.")
    st.stop()

# One row per country for the chosen year
country_year = load("""
    SELECT c.country_name, c.region, c.income_group, d.value AS debt
    FROM debt_data d
    JOIN countries c ON d.country_code = c.country_code
    WHERE d.indicator_code = :code AND d.year = :year
""", {"code": DEBT_CODE, "year": int(year)})
country_year = country_year[country_year["region"].isin(regions)].copy()
country_year["debt_bn"] = country_year["debt"] / 1e9


# ---------- Title and KPI cards ----------
st.title("International Debt Dashboard")
st.caption(f"Total external debt stock (current US$), {year}. "
           "Source: World Bank International Debt Statistics.")

top_country = country_year.loc[country_year["debt"].idxmax()]
c1, c2, c3, c4 = st.columns(4)
c1.metric("Total debt", f"${country_year['debt'].sum() / 1e12:,.2f} trillion")
c2.metric("Countries", len(country_year))
c3.metric("Average per country", f"${country_year['debt_bn'].mean():,.1f} bn")
c4.metric("Highest debt", top_country["country_name"])


# ---------- Tabs ----------
tab1, tab2, tab3, tab4, tab5 = st.tabs(
    ["Overview", "Country explorer", "Indicators", "Data", "SQL Questions"])

# ----- Tab 1: Overview -----
with tab1:
    left, right = st.columns(2)

    with left:
        n = st.slider("Number of countries to show", 5, 20, 10)
        top_n = country_year.nlargest(n, "debt_bn").sort_values("debt_bn")
        fig = px.bar(top_n, x="debt_bn", y="country_name", orientation="h",
                     title=f"Top {n} countries by debt (billion USD)")
        st.plotly_chart(fig, width="stretch")

    with right:
        by_region = (country_year.groupby("region")["debt_bn"].sum()
                     .sort_values(ascending=False).reset_index())
        fig = px.bar(by_region, x="region", y="debt_bn",
                     title="Debt by region (billion USD)")
        st.plotly_chart(fig, width="stretch")

    by_income = (country_year.groupby("income_group")
                 .agg(total_debt_bn=("debt_bn", "sum"), countries=("debt_bn", "count"))
                 .reset_index())
    st.subheader("Debt by income group")
    st.dataframe(by_income.round(1), width="stretch", hide_index=True)

    trend = load("""
        SELECT d.year, c.region, SUM(d.value) / 1e12 AS debt_trillion
        FROM debt_data d
        JOIN countries c ON d.country_code = c.country_code
        WHERE d.indicator_code = :code
        GROUP BY d.year, c.region
        ORDER BY d.year
    """, {"code": DEBT_CODE})
    trend = trend[trend["region"].isin(regions)]
    fig = px.line(trend, x="year", y="debt_trillion", color="region",
                  title="Debt over time by region (trillion USD)")
    st.plotly_chart(fig, width="stretch")

# ----- Tab 2: Country explorer -----
with tab2:
    country = st.selectbox("Choose a country", sorted(country_year["country_name"]))

    history = load("""
        SELECT d.year, d.value / 1e9 AS debt_bn
        FROM debt_data d
        JOIN countries c ON d.country_code = c.country_code
        WHERE d.indicator_code = :code AND c.country_name = :country
        ORDER BY d.year
    """, {"code": DEBT_CODE, "country": country})
    fig = px.line(history, x="year", y="debt_bn", markers=True,
                  title=f"{country}: total external debt over time (billion USD)")
    st.plotly_chart(fig, width="stretch")

    parts = load("""
        SELECT i.indicator_name, d.value / 1e9 AS debt_bn
        FROM debt_data d
        JOIN countries c  ON d.country_code   = c.country_code
        JOIN indicators i ON d.indicator_code = i.indicator_code
        WHERE i.topic = :topic AND i.is_usd = 1
          AND d.indicator_code <> :code
          AND d.year = :year AND c.country_name = :country
        ORDER BY d.value DESC
        LIMIT 10
    """, {"topic": TOPIC, "code": DEBT_CODE, "year": int(year), "country": country})
    fig = px.bar(parts.sort_values("debt_bn"), x="debt_bn", y="indicator_name",
                 orientation="h",
                 title=f"{country}: largest debt components, {year} (billion USD)")
    st.plotly_chart(fig, width="stretch")

# ----- Tab 3: Indicators -----
with tab3:
    components = load("""
        SELECT i.indicator_name, SUM(d.value) / 1e12 AS debt_trillion
        FROM debt_data d
        JOIN indicators i ON d.indicator_code = i.indicator_code
        WHERE i.topic = :topic AND i.is_usd = 1
          AND d.indicator_code <> :code AND d.year = :year
        GROUP BY i.indicator_name
        ORDER BY debt_trillion DESC
        LIMIT 10
    """, {"topic": TOPIC, "code": DEBT_CODE, "year": int(year)})
    fig = px.bar(components.sort_values("debt_trillion"), x="debt_trillion",
                 y="indicator_name", orientation="h",
                 title=f"Top 10 debt indicators, all countries, {year} (trillion USD)")
    st.plotly_chart(fig, width="stretch")
    st.caption("These indicators overlap (for example, long-term debt includes public and "
               "private parts), so they should not be added together.")

# ----- Tab 4: Data -----
with tab4:
    table = country_year[["country_name", "region", "income_group", "debt_bn"]].sort_values(
        "debt_bn", ascending=False)
    st.dataframe(table.round(2), width="stretch", hide_index=True)
    st.download_button("Download as CSV", table.to_csv(index=False).encode("utf-8"),
                       file_name=f"debt_{year}.csv", mime="text/csv")

# ----- Tab 5: SQL Questions -----
with tab5:
    st.subheader("SQL Questions")

    # label shown in the list  ->  the matching SQL key in QUERIES
    label_to_key = {f"{k.split('.')[0]}. {QUESTIONS[k.split('.')[0]]}": k for k in QUERIES}
    choice = st.selectbox("Select a question", list(label_to_key.keys()))
    sql = QUERIES[label_to_key[choice]]

    try:
        result = run_query(sql)
        # One single value (e.g. total countries): show it as a big number
        if result.shape == (1, 1):
            value = result.iloc[0, 0]
            label = result.columns[0].replace("_", " ").title()
            st.metric(label, f"{value:,.2f}" if isinstance(value, float) else f"{value:,}")
        else:
            st.write(f"**{len(result):,} rows**")
            st.dataframe(result, width="stretch")
    except Exception as e:
        st.error("The query failed:")
        st.exception(e)

    if st.checkbox("Show SQL query"):
        st.code(sql.strip(), language="sql")
