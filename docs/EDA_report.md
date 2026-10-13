# Exploratory Data Analysis Report: International Debt Statistics

## 1. Dataset overview
- Source: World Bank International Debt Statistics (last updated 12/03/2025)
- Main file: 62,983 rows x 39 columns (6 descriptive columns + one column per year, 2000-2032)
- Metadata files: country metadata (134 rows), series metadata (574 rows)
- Coverage after cleaning: 120 countries, 576 indicators, years 2000-2024

## 2. Data quality and cleaning
| Issue found | What I did | Result |
|---|---|---|
| Files not UTF-8 | Read with latin-1 encoding | Files load correctly |
| 5 junk rows at the bottom (3 blank, 2 footer lines) | Dropped rows with no Country Code | 62,978 rows |
| Hidden spaces in Country Code | Applied str.strip() | Joins match |
| 14 of 134 entries are groups (e.g. "Low income"), not countries | Kept only entries that have a Region | 120 countries |
| Counterpart-Area columns were "World" in every row | Dropped both columns | Fewer columns |
| One column per year (wide format) | Reshaped with melt() | 1,816,617 rows |
| Missing year values | Removed empty values | 1,142,836 rows |
| 2025-2032 are projections (mostly empty) | Kept 2000-2024 only | 1,060,074 rows |
| Duplicates | Checked on country + indicator + year | 0 found |
| 73 indicators have no row in series metadata | Topic set to "Unknown" | 576 indicators kept |

[YOUR NOTE: why does it matter to remove the 14 groups before analysing debt?]

## 3. How "debt" is measured
The dataset has 576 indicators, and they are not all debt (some are GNI, imports or percentages).
For country comparisons I used total external debt stock (DT.DOD.DECT.CD) in current US$, year 2023.
For indicator comparisons I used the 65 US$ indicators in the topic "Debt outstanding".
These indicators overlap (e.g. long-term debt includes public and private parts), so they cannot be added together.

## 4. Key findings (2023)

### 4.1 Overall size and spread
- Total external debt of the 120 countries: 8.84 trillion USD
- Mean 73.7 bn, median 12.5 bn, minimum 0.2 bn, maximum 2,450 bn
- Countries by debt size: below 1 bn: 11 | 1-10 bn: 41 | 10-100 bn: 50 | 100 bn-1 tn: 17 | above 1 tn: 1

[YOUR NOTE: the mean is about six times the median. What does that tell you about the distribution?]

### 4.2 Highest and lowest
| Rank | Highest debt | bn USD |
|---|---|---|
| 1 | China | 2,450 |
| 2 | India | 648 |
| 3 | Brazil | 607 |
| 4 | Mexico | 596 |
| 5 | Turkiye | 500 |
| 6 | Indonesia | 400 |
| 7 | Argentina | 253 |
| 8 | Colombia | 196 |
| 9 | Thailand | 195 |
| 10 | Ukraine | 179 |

Lowest: Tonga (0.2 bn), Timor-Leste (0.3), Sao Tome and Principe (0.3), Comoros (0.4), Samoa (0.4).

The top 5 countries hold 54.3% of the total. China alone holds 27.7%.

[YOUR NOTE: high debt is not the same as high risk. What other data would you need to judge risk?]

### 4.3 By region
| Region | Debt (bn USD) |
|---|---|
| East Asia & Pacific | 3,420 |
| Latin America & Caribbean | 2,010 |
| Europe & Central Asia | 1,136 |
| Sub-Saharan Africa | 871 |
| South Asia | 827 |
| Middle East & North Africa | 578 |

### 4.4 By income group
| Income group | Countries | Debt (bn USD) |
|---|---|---|
| Upper middle income | 49 | 6,341 |
| Lower middle income | 46 | 2,262 |
| Low income | 23 | 202 |
| High income | 1 | 3 |
| Unclassified | 1 | 33 |

The dataset covers mainly low- and middle-income borrowers, so high income is almost absent.

### 4.5 Trend over time
- 2000: 1.83 trillion | 2010: 3.84 trillion | 2020: 8.15 trillion | 2023: 8.84 trillion | 2024: 8.94 trillion
- Total debt grew about 4.8 times between 2000 and 2023.

[YOUR NOTE: describe the shape of the line chart: when was growth fastest, and when did it flatten?]

### 4.6 Indicators
- 538 of 576 indicators are in US$; 38 are not (rates, ratios, years)
- Among US$ indicators, GNI is the largest in 2023, ahead of imports and exports, so "all US$ indicators" is not the same as debt.
- Largest debt component (excluding the grand total): long-term external debt, about 6.12 trillion.
- Long-term debt is the dominant component for most countries.

## 5. Charts
[Insert your charts here. See the tip below.]

## 6. Limitations
- Values are in current US dollars, so they are not adjusted for inflation or country size.
- Debt-stock indicators overlap and cannot be summed.
- Projections (2025-2032) were excluded.
- Only reporting countries are included, mostly low- and middle-income.
- [YOUR NOTE: add one limitation you noticed yourself.]

## 7. Conclusions
1. [YOUR NOTE: biggest finding about concentration]
2. [YOUR NOTE: biggest finding about regions or income groups]
3. [YOUR NOTE: biggest finding about the trend]
4. [YOUR NOTE: one idea for further analysis, e.g. debt relative to GNI]