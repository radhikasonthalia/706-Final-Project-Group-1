import streamlit as st
import pandas as pd
import altair as alt
import plotly.express as px

# Set Streamlit page configuration
st.set_page_config(page_title="Health Equity Dashboards", layout="wide")

# Sidebar for page selection
st.sidebar.title("Navigation")
page = st.sidebar.radio("Select a visualization:", 
                        ["Health Determinants", "Vaccination Coverage", "Under-5 Mortality", ])

# -------------------------------------------------------------------------
# Visualization 1: Under-5 Mortality
# -------------------------------------------------------------------------
if page == "Under-5 Mortality":
    st.header("📈 Under-5 Mortality Rate Trends")
    st.markdown("*Deaths per 1,000 live births*")

    # Load the data
    @st.cache_data
    def load_mortality_data():
        df = pd.read_excel('under5_mortality.xlsx')
        return df

    df = load_mortality_data()

    # -----------------------------------------------------------------------------
    # Interactive Line Charts
    # -----------------------------------------------------------------------------
    st.markdown("""
    **Instructions:** 
    - Select countries to compare
    - Then choose the type of trend analysis: Overall, by Sex, or by Economic Status
    """)

    # Country selector
    country_list = sorted(df['setting'].unique())
    selected_countries = st.multiselect(
        "Select countries to compare:",
        options=country_list,
        default=['Brazil', 'India']
    )

    if len(selected_countries) == 0:
        st.warning("Please select at least one country.")
    else:
        # Trend type selector
        trend_type = st.radio(
            "Select trend breakdown:",
            options=['Overall Trend', 'Split by Sex', 'Split by Economic Status'],
            horizontal=True
        )
        
        # Filter data for selected countries
        df_filtered = df[df['setting'].isin(selected_countries)]
        
        if trend_type == 'Overall Trend':
            # Get ALL countries data for grey background
            df_all = df[df['dimension'] == 'Sex'].copy()
            df_all = df_all.drop_duplicates(subset=['setting', 'date'])
            df_all = df_all[['setting', 'date', 'setting_average']].rename(
                columns={'setting_average': 'estimate'}
            )
            
            # Background: all OTHER countries in grey
            df_background = df_all[~df_all['setting'].isin(selected_countries)]
            
            # Foreground: selected countries
            df_selected = df_all[df_all['setting'].isin(selected_countries)]
            
            # Grey background lines (all other countries)
            background = alt.Chart(df_background).mark_line(strokeWidth=1, opacity=0.3).encode(
                x=alt.X('date:O', title='Year', axis=alt.Axis(labelAngle=-45, values=list(range(1950, 2025, 5)))),
                y=alt.Y('estimate:Q', title='Mortality Rate (per 1,000 live births)'),
                detail='setting:N',
                color=alt.value('#888888'),
                tooltip=[
                    alt.Tooltip('setting:N', title='Country'),
                    alt.Tooltip('date:O', title='Year'),
                    alt.Tooltip('estimate:Q', title='Mortality Rate', format='.1f')
                ]
            )
            
            # Highlighted selected countries
            foreground = alt.Chart(df_selected).mark_line(strokeWidth=3, point=True).encode(
                x=alt.X('date:O', title='Year'),
                y=alt.Y('estimate:Q'),
                color=alt.Color('setting:N', title='Country', 
                               scale=alt.Scale(scheme='category10')),
                tooltip=[
                    alt.Tooltip('setting:N', title='Country'),
                    alt.Tooltip('date:O', title='Year'),
                    alt.Tooltip('estimate:Q', title='Mortality Rate', format='.1f')
                ]
            )
            
            # Layer background + foreground
            chart = (background + foreground).properties(
                width=800,
                height=400,
                title='Under-5 Mortality Rate: Overall Trend'
            )
            
            st.altair_chart(chart, use_container_width=True)
            
        elif trend_type == 'Split by Sex':
            df_plot = df_filtered[df_filtered['dimension'] == 'Sex'].copy()
            df_plot = df_plot[['setting', 'date', 'subgroup', 'estimate']]
            
            # Use faceting by country with max 3 columns per row
            chart = alt.Chart(df_plot).mark_line(strokeWidth=2.5, point=True).encode(
                x=alt.X('date:O', title='Year', axis=alt.Axis(labelAngle=-45, values=list(range(1950, 2025, 10)))),
                y=alt.Y('estimate:Q', title='Mortality Rate (per 1,000 live births)'),
                color=alt.Color('subgroup:N', title='Sex',
                               scale=alt.Scale(domain=['Female', 'Male'], 
                                              range=['#e377c2', '#1f77b4'])),
                tooltip=[
                    alt.Tooltip('setting:N', title='Country'),
                    alt.Tooltip('date:O', title='Year'),
                    alt.Tooltip('subgroup:N', title='Sex'),
                    alt.Tooltip('estimate:Q', title='Mortality Rate', format='.1f')
                ]
            ).properties(
                width=280,
                height=300,
                title='Under-5 Mortality Rate by Sex'
            ).facet(
                facet=alt.Facet('setting:N', title='Country'),
                columns=3
            )
            
            st.altair_chart(chart, use_container_width=True)
        
        else:  # Split by Economic Status
            df_plot = df_filtered[df_filtered['dimension'] == 'Economic status (wealth quintile)'].copy()
            
            if len(df_plot) == 0:
                st.warning("⚠️ No economic status data available for the selected countries. Economic data is available from 1990 onwards for ~105 countries.")
            else:
                df_plot = df_plot[['setting', 'date', 'subgroup', 'estimate']]
                
                # Simplify quintile names for display
                quintile_order = ['Quintile 1 (poorest)', 'Quintile 2', 'Quintile 3', 'Quintile 4', 'Quintile 5 (richest)']
                quintile_labels = ['Q1 (Poorest)', 'Q2', 'Q3', 'Q4', 'Q5 (Richest)']
                df_plot['quintile'] = df_plot['subgroup'].map(dict(zip(quintile_order, quintile_labels)))
                
                # Color scheme for quintiles
                quintile_colors = ['#d62728', '#ff7f0e', '#bcbd22', '#2ca02c', '#1f77b4']
                
                # Faceted chart with max 3 columns
                chart = alt.Chart(df_plot).mark_line(strokeWidth=2.5, point=True).encode(
                    x=alt.X('date:O', title='Year', axis=alt.Axis(labelAngle=-45, values=list(range(1990, 2025, 5)))),
                    y=alt.Y('estimate:Q', title='Mortality Rate (per 1,000 live births)'),
                    color=alt.Color('quintile:N', title='Economic Status',
                                   scale=alt.Scale(domain=quintile_labels, range=quintile_colors),
                                   sort=quintile_labels),
                    tooltip=[
                        alt.Tooltip('setting:N', title='Country'),
                        alt.Tooltip('date:O', title='Year'),
                        alt.Tooltip('quintile:N', title='Economic Status'),
                        alt.Tooltip('estimate:Q', title='Mortality Rate', format='.1f')
                    ]
                ).properties(
                    width=280,
                    height=300,
                    title='Under-5 Mortality Rate by Economic Status'
                ).facet(
                    facet=alt.Facet('setting:N', title='Country'),
                    columns=3
                )
                
                st.altair_chart(chart, use_container_width=True)

    # -----------------------------------------------------------------------------
    # Heatmap: Countries × Years
    # -----------------------------------------------------------------------------
    st.markdown("---")
    st.header("🗓️ Heatmap: Mortality Rate Over Time")

    # Prepare data for heatmap
    df_heatmap = df[df['dimension'] == 'Sex'].copy()
    df_heatmap = df_heatmap.drop_duplicates(subset=['setting', 'date'])
    df_heatmap = df_heatmap[['setting', 'date', 'setting_average', 'whoreg6']].rename(
        columns={'setting_average': 'mortality_rate'}
    )

    # Filter options
    col1, col2 = st.columns(2)

    with col1:
        regions = ['All Regions'] + sorted(df_heatmap['whoreg6'].dropna().unique().tolist())
        selected_region = st.selectbox("Filter by WHO Region:", options=regions)

    with col2:
        year_range = st.slider(
            "Select year range:",
            min_value=int(df_heatmap['date'].min()),
            max_value=int(df_heatmap['date'].max()),
            value=(1990, 2022)
        )

    # Apply filters
    df_heatmap_filtered = df_heatmap[
        (df_heatmap['date'] >= year_range[0]) & 
        (df_heatmap['date'] <= year_range[1])
    ]

    if selected_region != 'All Regions':
        df_heatmap_filtered = df_heatmap_filtered[df_heatmap_filtered['whoreg6'] == selected_region]

    # Sort countries by their most recent mortality rate
    country_order = df_heatmap_filtered[df_heatmap_filtered['date'] == df_heatmap_filtered['date'].max()].sort_values(
        'mortality_rate', ascending=False
    )['setting'].tolist()

    # Create heatmap
    heatmap = alt.Chart(df_heatmap_filtered).mark_rect().encode(
        x=alt.X('date:O', title='Year', axis=alt.Axis(labelAngle=-45, values=list(range(year_range[0], year_range[1]+1, 5)))),
        y=alt.Y('setting:N', title='Country', sort=country_order),
        color=alt.Color('mortality_rate:Q', 
                        title='Mortality Rate',
                        scale=alt.Scale(scheme='redyellowblue', reverse=True, domain=[0, 300])),
        tooltip=[
            alt.Tooltip('setting:N', title='Country'),
            alt.Tooltip('date:O', title='Year'),
            alt.Tooltip('mortality_rate:Q', title='Mortality Rate', format='.1f')
        ]
    ).properties(
        width=800,
        height=max(400, len(country_order) * 12),
        title=f'Under-5 Mortality Rate Heatmap ({year_range[0]}-{year_range[1]})'
    )

    st.altair_chart(heatmap, use_container_width=True)

    # Footer
    st.markdown("---")
    st.caption(f"Data Source: UN IGME | Last Updated: {df['update'].iloc[0]} | Countries: {df['setting'].nunique()} | Years: {df['date'].min()}-{df['date'].max()}")

# -------------------------------------------------------------------------
# Visualization 2: Health Determinants
# -------------------------------------------------------------------------
elif page == "Health Determinants":
    st.header("🏠 Health Determinants Dashboard")

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

    living_countries = sorted(df_living_recent['setting'].unique())

    # Context text
    st.markdown("""
    ## Economic Status
    We are exploring **what percentage of a country’s total household income is received by the poorest 20% of people** (the *poorest quintile*).

    NOTE:

    This value does **not** represent how many people are poor (each quintile always contains 20% of the population).  
    Instead, it shows **how much of the country’s income** is concentrated among those at the bottom of the income distribution.

    This makes the income share of the poorest 20% a **simple, intuitive indicator** of the country’s economic equality.
    """)

    # Countries in BOTH datasets
    country_list = [c for c in income_countries if c in living_countries]

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
            #opacity=alt.condition(selection, alt.value(1), alt.value(0.3))
        )
        #.add_params(selection)
        .properties(width=600, height=400, title="Economic Indicator: Share of household income (%)")
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


    # Context text
    st.markdown("""
    ## Education Levels
    We are exploring the percentage of people with no formal education, broken down by wealth quintile (from poorest to richest), separately for men and women.

    This makes the indicator a clear way to understand how **poverty intersects with education** for men and women.
    """)
    st.markdown("##### Education Indicator: % of people with no education by wealth quintile")

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
    with st.expander("ℹ️ More about this data "):
        st.write("""
        **Data filtering details:**
        - Only the **most recent year** of data per country is used.
        - Education levels come from **self-reported survey responses**, which may vary by country.
        - Wealth quintiles are **relative within each country**, so values are not comparable across countries.
        - Some countries may have **small sample sizes** for certain subgroups (e.g., poorest women), which can affect percentages.
        """)

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




    #LIVING CONDITIONS
    #The following code was written with help of Harvard Sandbox AI
    # I just wanted to learn some tools and practice them, 
    # this doesn't have to be graded!

    st.markdown("""
    ## Living Conditions 
    This map shows the **percentage of people with electricity access** in each subnational region of the selected country.

    The map helps visualize **geographic inequality** by highlighting where service gaps are widest.

    This makes electricity access a powerful indicator of **infrastructure development and regional inequality** within a country.
    """)
    st.markdown("##### Living Conditions Indicator: Population with no electricity (%) ")

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



    # Fuzzy match your region names to GADM NAME_1

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



    # Plot choropleth map

    def plot_setting_map(iso3, df_regions, country):
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
            title=f"{country} "
        )

        return fig

    # Streamlit Integration

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

    fig = plot_setting_map(iso3_selected, df_regions, country_selected)
    fig.update_traces(marker_line_width=0.5, marker_line_color="black")
    fig.update_traces(
        marker_line_color="black",
        marker_line_width=1
    )
    if fig:
        st.plotly_chart(fig, use_container_width=True)

    with st.expander("ℹ️ More about this data"):
        st.write("""
        **Data filtering details:**
        - Regions shown are only the ones that have **electricity-access estimates** available.
        - Only the **latest available year** per country is used; regions may differ in survey year.
        - Administrative boundaries come from external datasets and may not match **current official divisions** exactly.
        - Some regions may have **missing or outdated values**, especially where survey coverage is limited.
        - Electricity access reflects whether a household reports having power, not its **reliability or quality**.
        """)

    # Footer with data information

    st.markdown("---")
    st.caption(f"Data Source: Health determinants (DHS Program and UNICEF Data Warehouse) | Last Updated: {df_living_recent['update'].iloc[0]} | Countries: {df_living_recent['setting'].nunique()} | Years: {df_living_recent['date'].min()}-{df_living_recent['date'].max()}")

    #Sources:
    #Some code sections being reused but updated from 706 Problem Set 3
    #Debugging and errors handled with help of Harvard's Sandbox AI (specifically issues with running the file with anaconda)




# -------------------------------------------------------------------------
# Visualization 3: Vaccination Coverage
# -------------------------------------------------------------------------
elif page == "Vaccination Coverage":
    st.header("💉 Vaccination Coverage by Economic & Educational Status")

    # Load the Excel file
    @st.cache_data
    def load_immunization_data():
        df = pd.read_excel('immunizations.xlsx')
        return df

    df = load_immunization_data()

    # Filter for relevant indicators and dimensions
    df = df[
        (df['indicator_name'] == "Full immunization coverage among one-year-olds (%)") &
        ((df['dimension'] == "Education (3 groups)") |
         (df['dimension'] == "Economic status (wealth decile)"))
    ]

    # Prepare plotting DataFrame
    df = df[['setting', 'date', 'dimension', 'subgroup', 'estimate']].copy()
    df.rename(columns={'estimate': 'vaccination_coverage'}, inplace=True)

    # Clean data: keep only countries with no missing vaccination coverage
    valid_countries = df.groupby('setting')['vaccination_coverage'].apply(lambda x: x.notna().all())
    valid_countries = valid_countries[valid_countries].index.tolist()
    df = df[df['setting'].isin(valid_countries)]

    # Map subgroups to grouped categories
    economic_map = {
        'Decile 1 (poorest)': 'Lowest Economic Status',
        'Decile 2': 'Lowest Economic Status',
        'Decile 3': 'Middle Economic Status',
        'Decile 4': 'Middle Economic Status',
        'Decile 5': 'Middle Economic Status',
        'Decile 6': 'Middle Economic Status',
        'Decile 7': 'Middle Economic Status',
        'Decile 8': 'Middle Economic Status',
        'Decile 9': 'Highest Economic Status',
        'Decile 10 (richest)': 'Highest Economic Status'
    }

    education_map = {
        'No education': 'Lowest Educational Status',
        'Primary education': 'Medium Educational Status',
        'Secondary or higher education': 'Highest Educational Status'
    }

    df['group'] = df.apply(
        lambda row: economic_map.get(row['subgroup']) if row['dimension'] == 'Economic status (wealth decile)'
        else education_map.get(row['subgroup']) if row['dimension'] == 'Education (3 groups)'
        else None,
        axis=1
    )
    df['dimension_type'] = df['dimension'].apply(
        lambda x: 'Economic Status' if 'Economic' in x else 'Education' if 'Education' in x else None
    )
    df = df.dropna(subset=['group'])

    # Aggregate line chart data to avoid duplicate points
    line_data = df.groupby(['setting', 'date', 'dimension_type', 'group'], as_index=False)['vaccination_coverage'].mean()

    # Country selector
    countries = sorted(df['setting'].dropna().unique())
    country_dropdown = alt.binding_select(options=[None] + countries, name='Country: ')
    country_select = alt.selection_point(fields=['setting'], bind=country_dropdown, name='country_select', value=None)

    # Color scale
    color_scale = alt.Scale(domain=[
        'Lowest Economic Status', 'Middle Economic Status', 'Highest Economic Status',
        'Lowest Educational Status', 'Medium Educational Status', 'Highest Educational Status'
    ], range=['#AED6F1', '#5DADE2', '#1F618D', '#D7BDE2', '#AF7AC5', '#6C3483'])

    # Line chart
    line_chart = alt.Chart(line_data).mark_line(point=True, size=4, opacity=0.9).encode(
        x=alt.X('date:Q', title='Year', axis=alt.Axis(format='.0f', tickMinStep=1)),
        y=alt.Y('vaccination_coverage:Q', title='% 1yr Olds Vaccinated', scale=alt.Scale(domain=[0, 105])),
        color=alt.Color('group:N', title='Group', scale=color_scale),
        strokeDash=alt.StrokeDash('dimension_type:N', title='Dimension'),
        tooltip=[
            alt.Tooltip('setting:N', title='Country'),
            alt.Tooltip('date:Q', format='.0f', title='Year'),
            alt.Tooltip('dimension_type:N', title='Dimension'),
            alt.Tooltip('group:N', title='Group'),
            alt.Tooltip('vaccination_coverage:Q', format='.1f', title='% Vaccinated')
        ]
    ).transform_filter(country_select).properties(
        width=700,
        height=400,
        title='Trends of Vaccination Coverage by Economic & Educational Status'
    )

    # Bar chart
    bar_chart = alt.Chart(df).mark_bar().encode(
        x=alt.X('vaccination_coverage:Q', title='Average % Vaccinated'),
        y=alt.Y('group:N', sort='-x', title='Group'),
        color=alt.Color('group:N', scale=color_scale, legend=None),
        tooltip=[
            alt.Tooltip('dimension_type:N', title='Dimension'),
            alt.Tooltip('group:N', title='Group'),
            alt.Tooltip('vaccination_coverage:Q', format='.1f', title='Average % Vaccinated')
        ]
    ).transform_filter(country_select).transform_aggregate(
        vaccination_coverage='mean(vaccination_coverage)',
        groupby=['dimension_type', 'group']
    ).properties(
        width=700,
        height=250,
        title='Average Vaccination Coverage by Group'
    )

    # Combine charts into dashboard
    dashboard = alt.vconcat(line_chart, bar_chart).add_params(country_select).configure_view(strokeWidth=0).configure_title(
        fontSize=16,
        font='Arial',
        anchor='start'
    )

    # Render the dashboard
    st.altair_chart(dashboard)

    # Footer
    st.markdown("---")
    st.caption("Data Source: Immunization surveys (DHS Program and UNICEF Data Warehouse)")
