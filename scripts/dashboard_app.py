import pandas as pd
import plotly.express as px
import streamlit as st
from sqlalchemy import create_engine, text
from sqlalchemy.engine import URL

# ---------- Settings (same as the other scripts) ----------
DB_USER     = "postgres"
DB_PASSWORD = "KAvi"
DB_HOST     = "localhost"
DB_PORT     = 5432
DB_NAME     = "intl_debt"

DEBT_CODE  = "DT.DOD.DECT.CD"   # total external debt stock (US$)
DEBT_TOPIC = "Economic Policy & Debt: External debt: Debt outstanding"

st.set_page_config(page_title="International Debt Dashboard", layout="wide")


# ---------- Database helpers ----------
@st.cache_resource                      # create the connection only once
def get_engine():
    url = URL.create("postgresql+psycopg2", username=DB_USER, password=DB_PASSWORD,
                     host=DB_HOST, port=DB_PORT, database=DB_NAME)
    return create_engine(url)


@st.cache_data                          # remember results so clicks stay fast
def load(sql, params=None):
    with get_engine().connect() as conn:
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
c2.metric("Countries", f"{len(country_year)}")
c3.metric("Average per country", f"${country_year['debt_bn'].mean():,.1f} bn")
c4.metric("Highest debt", top_country["country_name"])


# ---------- Tabs ----------
tab1, tab2, tab3, tab4 = st.tabs(["Overview", "Country explorer", "Indicators", "Data"])

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
    """, {"topic": DEBT_TOPIC, "code": DEBT_CODE, "year": int(year), "country": country})
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
    """, {"topic": DEBT_TOPIC, "code": DEBT_CODE, "year": int(year)})
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