import altair as alt
import pandas as pd
import streamlit as st
import random

@st.cache_data
def load_data():
    df = pd.read_excel('health_determinants.xlsx')
    return df

@st.cache_data
def prepare_recent_income_year(df):
    df_filtered = df[df['indicator_name'] == 'Share of household income (%)']
    df_quintile_1 = df_filtered[df_filtered['subgroup'] == 'Quintile 1 (poorest)']
    df_recent_year = df_quintile_1.sort_values(
        by=['setting', 'date'],
        ascending=[True, False]
    )
    df_recent_year = df_recent_year.drop_duplicates(subset=['setting'])
    return df_recent_year

# Load data
df = load_data()

# Income indicator (poorest quintile)
df_income_recent = prepare_recent_income_year(df)
income_countries = sorted(df_income_recent['setting'].unique())

# ---- EDUCATION FILTERING ----
df_education = df[    (df['setting'].isin(income_countries)) &
    (df['indicator_name'].str.startswith('People with no education (%)')) &
    (df['date'].notna())
]

# >>> INSERT HERE <<<
df_education = df_education.copy()

df_education["sex"] = df_education["indicator_name"].apply(
    lambda x: "Female" if "Female" in x else ("Male" if "Male" in x else None)
)

df_education["indicator_clean"] = (
    df_education["indicator_name"]
    .str.replace(" - Female", "", regex=False)
    .str.replace(" - Male", "", regex=False)
)
# >>> END INSERT <<<

most_recent_years_education = (
    df_education.groupby('setting')['date']
    .max()
    .reset_index()
    .rename(columns={'date': 'most_recent_date'})
)

df_education_recent = pd.merge(
    df_education,
    most_recent_years_education,
    left_on=['setting', 'date'],
    right_on=['setting', 'most_recent_date'],
    how='inner'
).drop(columns=['most_recent_date'])

education_countries = sorted(df_education_recent['setting'].unique())

# Countries in BOTH datasets
country_list = [c for c in income_countries if c in education_countries]

# Context text
st.markdown("""
### Economic Status
We are exploring **what percentage of a country’s total household income is received by the poorest 20% of people** (the *poorest quintile*).

NOTE:

This value does **not** represent how many people are poor (each quintile always contains 20% of the population).  
Instead, it shows **how much of the country’s income** is concentrated among those at the bottom of the income distribution.

This makes the income share of the poorest 20% a **simple, intuitive indicator** of the country’s economic equality.
""")

# Default countries
preferred_defaults = ["Dominican Republic", "Kenya", "Philippines", "Peru", "Bangladesh", "South Africa", "Egypt", "Ghana"]
default_countries = [c for c in preferred_defaults if c in country_list]

# Selector
selected_countries = st.multiselect(
    "Select countries to display:",
    options=country_list,
    default=default_countries
)

# Filter
df_plot = df_income_recent[df_income_recent['setting'].isin(selected_countries)]
df_plot['estimate'] = pd.to_numeric(df_plot['estimate'], errors='coerce')

# Chart
selection = alt.selection_single(fields=["setting"], empty="none")

chart = (
    alt.Chart(df_plot)
    .mark_bar(color="#4C78A8")
    .encode(
        y=alt.Y("setting:N", sort='-x', title="Country"),
        x=alt.X("estimate:Q", title="Poorest Quintile Income Share"),
        tooltip=["setting", "estimate", "date"],
        opacity=alt.condition(selection, alt.value(1), alt.value(0.3))
    )
    .add_params(selection)
    .properties(width=600, height=400, title="Economic Indicator")
)




text = (
    alt.Chart(df_plot)
    .mark_text(align="left", baseline="middle", dx=3, fontSize=12)
    .encode(
        y=alt.Y("setting:N", sort='-x'),
        x=alt.X("estimate:Q"),
        text=alt.Text("estimate:Q", format=".1f")
    )
)

st.altair_chart(chart + text, width="stretch")

with st.expander("ℹ️ More about this data"):
    st.write("""
    **Data filtering details:**
    - Countries shown must have **both income data AND education data** available.
    - Only the **most recent available year per country** is used.
    - The visualization shows the **income share of the poorest quintile (Q1)**.
    """)






#Sources:
#Some code sections being reused but updated from 706 Problem Set 3
#Debugging and errors handled with help of Harvard's Sandbox AI (specifically issues with running the file with anaconda)
