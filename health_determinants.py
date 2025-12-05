import altair as alt
import pandas as pd
import streamlit as st
import random

@st.cache_data
def load_data():
    df = pd.read_excel('health_determinants.xlsx')
    return df

@st.cache_data
def prepare_recent_year(df):
    # FIRST INDICATOR: ECONOMIC STATUS using 'share of household income' indicator 
    df_filtered = df[df['indicator_name'] == 'Share of household income (%)']

    # keep poorest quintile
    df_quintile_1 = df_filtered[df_filtered['subgroup'] == 'Quintile 1 (poorest)']

    # sort so most recent year is first within each country
    df_recent_year = df_quintile_1.sort_values(
        by=['setting', 'date'],
        ascending=[True, False]
    )

    # keep most recent year per country
    df_recent_year = df_recent_year.drop_duplicates(subset=['setting'])

    return df_recent_year




# ----- Load + prepare data (cached) -----
df = load_data()
df_recent_year = prepare_recent_year(df)

#COntext for the data

st.markdown("""
### Economic Status
We are exploring **what percentage of a country’s total household income is received by the poorest 20% of people** (the *poorest quintile*).

NOTE: 
            
This value does **not** represent how many people are poor (each quintile always contains 20% of the population).  
Instead, it shows **how much of the country’s income** is concentrated among those at the bottom of the income distribution.


This makes the income share of the poorest 20% a **simple, intuitive indicator** of the country’s economic equality and general socioeconomic conditions.
""")


# --- Country selector ---
country_list = sorted(df_recent_year['setting'].unique())

preferred_defaults = ["Sweden", "Germany", "Mexico", "Ecuador", "Brazil"]
default_countries = [c for c in preferred_defaults if c in country_list]

selected_countries = st.multiselect(
    "Select countries to display:",
    options=country_list,
    default= default_countries 
)

# Filter based on selection
df_plot = df_recent_year[df_recent_year['setting'].isin(selected_countries)]

# Ensure numeric
df_plot['estimate'] = pd.to_numeric(df_plot['estimate'], errors='coerce')



# --- Horizontal bar chart ---
chart = (
    alt.Chart(df_plot)
    .mark_bar(color="#4C78A8")
    .encode(
        y=alt.Y("setting:N", sort='-x', title="Country"),
        x=alt.X("estimate:Q", title="Poorest Quintile Income Share"),
        tooltip=["setting", "estimate", "date"]
    )
    .properties(
        width=600,
        height=400,
        title=alt.TitleParams(
            "Economic Indicator",
            anchor="middle"
        )
    )
)


# Labels
text = (
    alt.Chart(df_plot)
    .mark_text(
        align="left",
        baseline="middle",
        dx=3,
        fontSize=12
    )
    .encode(
        y=alt.Y("setting:N", sort='-x'),
        x=alt.X("estimate:Q"),
        text=alt.Text("estimate:Q", format=".1f")
    )
)



# Display (update Streamlit warning)
st.altair_chart(chart + text, width="stretch")


with st.expander("ℹ️ More about this data"):
    st.write("""
    **Data filtering details:**
    - We use the **most recent available year for each country**, and these years may **not** be the same across countries.
    - The visualization shows the **share of household income**, specifically for the **Poorest quintile (Q1)**.
    - Countries with missing or incomplete data for their latest available year are excluded.
    """)






#Sources:
#Some code sections being reused but updated from 706 Problem Set 3
#Debugging and errors handled with help of Harvard's Sandbox AI (specifically issues with running the file with anaconda)
