import altair as alt
import pandas as pd
import streamlit as st
import random
import plotly.express as px

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


# ---- LIVING CONDITIONS FILTERING ----

# keep only the countries that appear in df_education_recent
valid_settings = df_education_recent["setting"].unique()

df_living = df[
    df["setting"].isin(valid_settings) &
    df["indicator_name"].str.startswith("Population with electricity (%)") &
    df["dimension"].isin(["Subnational region", "Place of residence"])
].copy()

most_recent_living = (
    df_living.groupby("setting")["date"]
    .max()
    .reset_index()
    .rename(columns={"date": "most_recent_date"})
)

df_living_recent = pd.merge(
    df_living,
    most_recent_living,
    left_on=["setting", "date"],
    right_on=["setting", "most_recent_date"],
    how="inner"
).drop(columns=["most_recent_date"])

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
        x=alt.X("estimate:Q", title="Poorest Quintile Income Share (%)"),
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


#----LIVING CDTS PLOTS-----
df_regions = df_living_recent[
    df_living_recent["dimension"] == "Subnational region"
].copy()

df_regions = df_regions.rename(columns={
    "subgroup": "region",
    "estimate": "value"
})

country_to_iso = dict(zip(df_regions["setting"], df_regions["iso3"]))

country_selected = selected_country_name




import streamlit as st
import geopandas as gpd
import requests
import os
import matplotlib.pyplot as plt
from rapidfuzz import process, fuzz
import json

def load_gadm_adm1(iso3):
    iso3 = iso3.upper()
    os.makedirs("geo_gadm", exist_ok=True)
    path = f"geo_gadm/{iso3}_adm1.json"

    if os.path.exists(path):
        return gpd.read_file(path)

    url = f"https://geodata.ucdavis.edu/gadm/gadm4.1/json/gadm41_{iso3}_1.json"
    r = requests.get(url)
    if r.status_code != 200:
        return None

    with open(path, "wb") as f:
        f.write(r.content)

    return gpd.read_file(path)


# -----------------------------------------------------
# Fuzzy match your region names to GADM NAME_1
# -----------------------------------------------------
def fuzzy_merge_regions(df_setting, gdf):
    gadm_names = list(gdf["NAME_1"])

    matches = df_setting["region"].apply(
        lambda x: process.extractOne(
            x,
            gadm_names,
            scorer=fuzz.WRatio
        )[0]
    )

    df_setting = df_setting.copy()
    df_setting["matched_region"] = matches
    return df_setting


# -----------------------------------------------------
# Plot choropleth map
# -----------------------------------------------------
def plot_setting_map(iso3, df_regions):
    df_setting = df_regions[df_regions["iso3"] == iso3]

    if df_setting.empty:
        st.error(f"No rows found for ISO3 code: {iso3}")
        return None

    gdf = load_gadm_adm1(iso3)
    if gdf is None:
        st.error("Could not load boundaries.")
        return None

    df_setting = fuzzy_merge_regions(df_setting, gdf)

    geojson_dict = json.loads(gdf.to_json())

    # center map on the country geometry
    centroid = gdf.geometry.unary_union.centroid
    center_lat = centroid.y
    center_lon = centroid.x

    fig = px.choropleth_mapbox(
    df_setting,
    geojson=geojson_dict,
    locations="matched_region",
    featureidkey="properties.NAME_1",
    color="value",
    color_continuous_scale="RdBu_r",   
    hover_name="region",
    hover_data={"value": ":.1f"},
    mapbox_style="carto-positron",
    center={"lat": center_lat, "lon": center_lon},
    zoom=5,
    opacity=0.8,
)

    fig.update_layout(
        margin=dict(l=0, r=0, t=40, b=0),
        height=600,
        title=f"{iso3} — Population with electricity (%)"
    )

    return fig

# -----------------------------------------------------
# Streamlit Integration
# -----------------------------------------------------
def app(df_regions):
    st.title("Setting Subregion Choropleth")

    # assuming df_regions has columns: setting, iso3, region, value
    setting_to_iso = dict(zip(df_regions["setting"], df_regions["iso3"]))

    setting = st.selectbox("Choose a setting", sorted(df_regions["setting"].unique()))
    iso3 = setting_to_iso[setting]

    fig = plot_setting_map(iso3, df_regions)
    if fig:
        st.pyplot(fig)


iso3_selected = country_to_iso[country_selected]

fig = plot_setting_map(iso3_selected, df_regions)
fig.update_traces(marker_line_width=0.5, marker_line_color="black")
fig.update_traces(
    marker_line_color="black",
    marker_line_width=1
)
if fig:
    st.plotly_chart(fig, use_container_width=True)

# -----------------------------------------------------------------------------
# Footer with data information
# -----------------------------------------------------------------------------
st.markdown("---")
st.caption(f"Data Source: UN IGME | Last Updated: {df_living_recent['update'].iloc[0]} | Countries: {df_living_recent['setting'].nunique()} | Years: {df_living_recent['date'].min()}-{df_living_recent['date'].max()}")

#Sources:
#Some code sections being reused but updated from 706 Problem Set 3
#Debugging and errors handled with help of Harvard's Sandbox AI (specifically issues with running the file with anaconda)
