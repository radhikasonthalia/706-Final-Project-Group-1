import altair as alt
import pandas as pd
import streamlit as st

#load the data:
df = pd.read_excel('health_determinants.xlsx')
df.head() 
#WRAPPED SO IT CACHES

#filter and explore the data

#FIRST INDICATOR: ECONOMIC STATUS using 'share of household income' indicator 
df_filtered = df[df['indicator_name'] == 'Share of household income (%)']

#now keep just the poorest quantile info
df_quintile_1 = df_filtered[df_filtered['subgroup'] == 'Quintile 1 (poorest)']

#now I want to keep just the most common year per country (so I keep most countries and compare)

# sort by 'setting' and 'date' in descending order to bring the most recent year to the top for each country
df_recent_year = df_quintile_1.sort_values(by=['setting', 'date'], ascending=[True, False])

# drop duplicate 'setting' entries, keeping the first (most recent year)
df_recent_year = df_recent_year.drop_duplicates(subset=['setting'])

# --- Country selector ---
country_list = sorted(df_recent_year['setting'].unique())
selected_countries = st.multiselect(
    "Select countries to display:",
    options=country_list,
    default=country_list
)

# Filter based on selection
df_plot = df_recent_year[df_recent_year['setting'].isin(selected_countries)]

# Make sure estimate is numeric
df_plot['estimate'] = pd.to_numeric(df_plot['estimate'], errors='coerce')

# --- Horizontal bar chart ---
chart = (
    alt.Chart(df_plot)
    .mark_bar(color="#4C78A8")
    .encode(
        y=alt.Y("setting:N", sort='-x', title="Country"),
        x=alt.X("estimate:Q", title="Share of household income (%)"),
        tooltip=["setting", "estimate", "date"]
    )
    .properties(
        width=600,
        height=400,
        title="Share of Household Income (%) – Most Recent Year"
    )
)

# Labels at end of bars
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

# Display
st.altair_chart(chart + text, use_container_width=True)