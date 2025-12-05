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


df_education = df_education.copy()

df_education["sex"] = df_education["indicator_name"].str.lower().apply(
    lambda x: "Female" if "female" in x
    else ("Male" if "male" in x
    else "Both")
)

df_education["indicator_clean"] = (
    df_education["indicator_name"]
    .str.replace(" - Female", "", regex=False)
    .str.replace(" - Male", "", regex=False)
)


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

sex_counts = df_education_recent.groupby(["setting", "sex"]).size().unstack(fill_value=0)

valid_countries = sex_counts[
    (sex_counts["Male"] > 0) & (sex_counts["Female"] > 0)
].index.tolist()

df_education_recent = df_education_recent[
    df_education_recent["setting"].isin(valid_countries)
]

education_countries = sorted(df_education_recent['setting'].unique())

# Countries in BOTH datasets
country_list = [c for c in income_countries if c in education_countries]

# Context text
st.markdown("""
## Economic Status
We are exploring **what percentage of a country’s total household income is received by the poorest 20% of people** (the *poorest quintile*).

NOTE:

This value does **not** represent how many people are poor (each quintile always contains 20% of the population).  
Instead, it shows **how much of the country’s income** is concentrated among those at the bottom of the income distribution.

This makes the income share of the poorest 20% a **simple, intuitive indicator** of the country’s economic equality.
""")

# Default countries
preferred_defaults = ["Dominican Republic", "Armenia", "Philippines", "Peru", "Bangladesh", "South Africa", "Brazil", "Ghana"]
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

#st.altair_chart(chart + text, width="stretch")
selected_country = st.altair_chart(
    chart + text, 
    use_container_width=True,
).selection  # <— captures selection



selected_country_name = None
try:
    selected_country_name = selected_country["setting"]
except:
    pass

with st.expander("ℹ️ More about this data"):
    st.write("""
    **Data filtering details:**
    - Countries shown must have **both income data AND education data** available.
    - Only the **most recent available year per country** is used.
    - The visualization shows the **income share of the poorest quintile (Q1)**.
    """)

st.subheader("Choose one of the plotted countries to explore more in depth:")


if selected_countries:
    selected_country_name = st.radio(
        "Select one country:",
        options=selected_countries,
        horizontal=False
    )
else:
    st.warning("Please select at least one country above.")
    st.stop()

#----EDUCATION PLLOTS----
#choose country

if selected_country_name:
    df_ed_country = df_education_recent[
        df_education_recent["setting"] == selected_country_name
    ]
else:
    st.warning("Select a country from the Economic Indicator above.")
    st.stop()



#econ status form education
df_country = df_education_recent[
    df_education_recent["setting"] == selected_country_name
]

df_country = df_country[df_education_recent["dimension"] == "Economic status (wealth quintile)"]

df_male = df_country[df_country["sex"] == "Male"]
df_female = df_country[df_country["sex"] == "Female"]



def pie_chart(data, title):
    return (
        alt.Chart(data)
        .mark_arc()
        .encode(
            theta=alt.Theta("estimate:Q", stack=True),
            color=alt.Color("subgroup:N", title="Wealth Quintile"),
            tooltip=["subgroup", "estimate"]
        )
        .properties(
            width=250,
            height=250,
            title=title   # now only "Male" or "Female"
        )
    )


st.markdown(f"##### Country selected: **{selected_country_name}**")

st.header("Education Levels")
st.markdown("#### % of people with no education by wealth quintile")

col1, col2 = st.columns(2)

with col1:
    st.altair_chart(
        pie_chart(df_male, "Male"),
        use_container_width=True
    )

with col2:
    st.altair_chart(
        pie_chart(df_female, "Female"),
        use_container_width=True
    )




#Sources:
#Some code sections being reused but updated from 706 Problem Set 3
#Debugging and errors handled with help of Harvard's Sandbox AI (specifically issues with running the file with anaconda)
