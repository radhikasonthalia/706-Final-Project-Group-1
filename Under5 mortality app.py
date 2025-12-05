import altair as alt
import pandas as pd
import streamlit as st
from vega_datasets import data as vega_data

# Page configuration
st.set_page_config(page_title="Under-5 Mortality Rate Dashboard", layout="wide")

# ISO3 to numeric country code mapping (embedded to avoid network issues)
ISO3_TO_ID = {
    'AFG': 4, 'ALB': 8, 'DZA': 12, 'AND': 20, 'AGO': 24, 'ATG': 28, 'ARG': 32, 'ARM': 51, 
    'AUS': 36, 'AUT': 40, 'AZE': 31, 'BHS': 44, 'BHR': 48, 'BGD': 50, 'BRB': 52, 'BLR': 112, 
    'BEL': 56, 'BLZ': 84, 'BEN': 204, 'BTN': 64, 'BOL': 68, 'BIH': 70, 'BWA': 72, 'BRA': 76, 
    'BRN': 96, 'BGR': 100, 'BFA': 854, 'BDI': 108, 'KHM': 116, 'CMR': 120, 'CAN': 124, 
    'CPV': 132, 'CAF': 140, 'TCD': 148, 'CHL': 152, 'CHN': 156, 'COL': 170, 'COM': 174, 
    'COG': 178, 'COD': 180, 'CRI': 188, 'CIV': 384, 'HRV': 191, 'CUB': 192, 'CYP': 196, 
    'CZE': 203, 'DNK': 208, 'DJI': 262, 'DMA': 212, 'DOM': 214, 'ECU': 218, 'EGY': 818, 
    'SLV': 222, 'GNQ': 226, 'ERI': 232, 'EST': 233, 'ETH': 231, 'FJI': 242, 'FIN': 246, 
    'FRA': 250, 'GAB': 266, 'GMB': 270, 'GEO': 268, 'DEU': 276, 'GHA': 288, 'GRC': 300, 
    'GRD': 308, 'GTM': 320, 'GIN': 324, 'GNB': 624, 'GUY': 328, 'HTI': 332, 'HND': 340, 
    'HUN': 348, 'ISL': 352, 'IND': 356, 'IDN': 360, 'IRN': 364, 'IRQ': 368, 'IRL': 372, 
    'ISR': 376, 'ITA': 380, 'JAM': 388, 'JPN': 392, 'JOR': 400, 'KAZ': 398, 'KEN': 404, 
    'KIR': 296, 'PRK': 408, 'KOR': 410, 'KWT': 414, 'KGZ': 417, 'LAO': 418, 'LVA': 428, 
    'LBN': 422, 'LSO': 426, 'LBR': 430, 'LBY': 434, 'LIE': 438, 'LTU': 440, 'LUX': 442, 
    'MKD': 807, 'MDG': 450, 'MWI': 454, 'MYS': 458, 'MDV': 462, 'MLI': 466, 'MLT': 470, 
    'MHL': 584, 'MRT': 478, 'MUS': 480, 'MEX': 484, 'FSM': 583, 'MDA': 498, 'MCO': 492, 
    'MNG': 496, 'MNE': 499, 'MAR': 504, 'MOZ': 508, 'MMR': 104, 'NAM': 516, 'NRU': 520, 
    'NPL': 524, 'NLD': 528, 'NZL': 554, 'NIC': 558, 'NER': 562, 'NGA': 566, 'NOR': 578, 
    'OMN': 512, 'PAK': 586, 'PLW': 585, 'PAN': 591, 'PNG': 598, 'PRY': 600, 'PER': 604, 
    'PHL': 608, 'POL': 616, 'PRT': 620, 'QAT': 634, 'ROU': 642, 'RUS': 643, 'RWA': 646, 
    'KNA': 659, 'LCA': 662, 'VCT': 670, 'WSM': 882, 'SMR': 674, 'STP': 678, 'SAU': 682, 
    'SEN': 686, 'SRB': 688, 'SYC': 690, 'SLE': 694, 'SGP': 702, 'SVK': 703, 'SVN': 705, 
    'SLB': 90, 'SOM': 706, 'ZAF': 710, 'SSD': 728, 'ESP': 724, 'LKA': 144, 'SDN': 736, 
    'SUR': 740, 'SWZ': 748, 'SWE': 752, 'CHE': 756, 'SYR': 760, 'TJK': 762, 'TZA': 834, 
    'THA': 764, 'TLS': 626, 'TGO': 768, 'TON': 776, 'TTO': 780, 'TUN': 788, 'TUR': 792, 
    'TKM': 795, 'TUV': 798, 'UGA': 800, 'UKR': 804, 'ARE': 784, 'GBR': 826, 'USA': 840, 
    'URY': 858, 'UZB': 860, 'VUT': 548, 'VEN': 862, 'VNM': 704, 'YEM': 887, 'ZMB': 894, 
    'ZWE': 716, 'PSE': 275, 'TWN': 158
}

# Load the data
@st.cache_data
def load_data():
    # Update this path to match your local file location
    df = pd.read_excel('under5_mortality.xlsx')
    return df

df = load_data()

# Title
st.title("🌍 Under-5 Mortality Rate Trends")
st.markdown("*Deaths per 1,000 live births*")

# -----------------------------------------------------------------------------
# SECTION 1: World Map - Overall Mortality Rate (Most Recent Year)
# -----------------------------------------------------------------------------
st.header("Global Overview: Under-5 Mortality Rate")

# Get the overall data (by sex dimension, use setting_average)
df_overall = df[df['dimension'] == 'Sex'].copy()

# Year selector for the map
available_years = sorted(df_overall['date'].unique())
selected_map_year = st.selectbox(
    "Select year for map:",
    options=available_years,
    index=len(available_years) - 1,  # Default to most recent year
    key='map_year'
)

# Filter data for selected year
df_map_year = df_overall[df_overall['date'] == selected_map_year].copy()
df_map_year = df_map_year.drop_duplicates(subset=['setting', 'iso3'])
df_map_year = df_map_year[['setting', 'iso3', 'date', 'setting_average']].rename(
    columns={'setting_average': 'mortality_rate'}
)

# Add numeric country IDs
df_map_year['id'] = df_map_year['iso3'].map(ISO3_TO_ID)

# Load world map
countries = alt.topo_feature(vega_data.world_110m.url, 'countries')

# Create the choropleth map
map_chart = alt.Chart(countries).mark_geoshape(
    stroke='white',
    strokeWidth=0.5
).encode(
    color=alt.condition(
        alt.datum.mortality_rate != None,
        alt.Color('mortality_rate:Q',
                  scale=alt.Scale(scheme='reds', domain=[0, 200]),
                  title='Mortality Rate',
                  legend=alt.Legend(orient='bottom')),
        alt.value('#e0e0e0')
    ),
    tooltip=[
        alt.Tooltip('setting:N', title='Country'),
        alt.Tooltip('mortality_rate:Q', title='Mortality Rate', format='.1f'),
        alt.Tooltip('date:O', title='Year')
    ]
).transform_lookup(
    lookup='id',
    from_=alt.LookupData(df_map_year, 'id', ['setting', 'mortality_rate', 'date'])
).project(
    type='naturalEarth1'
).properties(
    width=900,
    height=500,
    title=f'Under-5 Mortality Rate by Country ({selected_map_year})'
)

st.altair_chart(map_chart, use_container_width=True)

# -----------------------------------------------------------------------------
# SECTION 2: Interactive Line Charts
# -----------------------------------------------------------------------------
st.header("📈 Year Trends Analysis")

st.markdown("""
**Instructions:** 
- First, select 1-2 countries to compare
- Then choose the type of trend analysis: Overall, by Sex, or by Economic Status
""")

# Country selector (max 2)
country_list = sorted(df['setting'].unique())
selected_countries = st.multiselect(
    "Select up to 2 countries to compare:",
    options=country_list,
    default=['Brazil', 'India'],
    max_selections=2
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
        # Use setting_average for overall trend
        df_plot = df_filtered[df_filtered['dimension'] == 'Sex'].copy()
        df_plot = df_plot.drop_duplicates(subset=['setting', 'date'])
        df_plot = df_plot[['setting', 'date', 'setting_average']].rename(
            columns={'setting_average': 'estimate'}
        )
        df_plot['category'] = 'Overall'
        
        # Create line chart
        chart = alt.Chart(df_plot).mark_line(strokeWidth=2.5, point=True).encode(
            x=alt.X('date:O', title='Year', axis=alt.Axis(labelAngle=-45, values=list(range(1950, 2025, 5)))),
            y=alt.Y('estimate:Q', title='Mortality Rate (per 1,000 live births)'),
            color=alt.Color('setting:N', title='Country', 
                           scale=alt.Scale(scheme='category10')),
            tooltip=[
                alt.Tooltip('setting:N', title='Country'),
                alt.Tooltip('date:O', title='Year'),
                alt.Tooltip('estimate:Q', title='Mortality Rate', format='.1f')
            ]
        ).properties(
            width=800,
            height=400,
            title='Under-5 Mortality Rate: Overall Trend'
        )
        
        st.altair_chart(chart, use_container_width=True)
        
    elif trend_type == 'Split by Sex':
        df_plot = df_filtered[df_filtered['dimension'] == 'Sex'].copy()
        df_plot = df_plot[['setting', 'date', 'subgroup', 'estimate']]
        
        # Create line chart with facets
        chart = alt.Chart(df_plot).mark_line(strokeWidth=2, point=True).encode(
            x=alt.X('date:O', title='Year', axis=alt.Axis(labelAngle=-45, values=list(range(1950, 2025, 10)))),
            y=alt.Y('estimate:Q', title='Mortality Rate (per 1,000 live births)'),
            color=alt.Color('subgroup:N', title='Sex',
                           scale=alt.Scale(domain=['Female', 'Male'], 
                                          range=['#e377c2', '#1f77b4'])),
            strokeDash=alt.StrokeDash('setting:N', title='Country'),
            tooltip=[
                alt.Tooltip('setting:N', title='Country'),
                alt.Tooltip('date:O', title='Year'),
                alt.Tooltip('subgroup:N', title='Sex'),
                alt.Tooltip('estimate:Q', title='Mortality Rate', format='.1f')
            ]
        ).properties(
            width=800,
            height=400,
            title='Under-5 Mortality Rate by Sex'
        )
        
        st.altair_chart(chart, use_container_width=True)
        
        # Add a faceted view if two countries selected
        if len(selected_countries) == 2:
            st.subheader("Side-by-Side Comparison")
            facet_chart = alt.Chart(df_plot).mark_line(strokeWidth=2, point=True).encode(
                x=alt.X('date:O', title='Year', axis=alt.Axis(labelAngle=-45, values=list(range(1950, 2025, 10)))),
                y=alt.Y('estimate:Q', title='Mortality Rate'),
                color=alt.Color('subgroup:N', title='Sex',
                               scale=alt.Scale(domain=['Female', 'Male'], 
                                              range=['#e377c2', '#1f77b4'])),
                tooltip=[
                    alt.Tooltip('setting:N', title='Country'),
                    alt.Tooltip('date:O', title='Year'),
                    alt.Tooltip('subgroup:N', title='Sex'),
                    alt.Tooltip('estimate:Q', title='Mortality Rate', format='.1f')
                ]
            ).facet(
                column=alt.Column('setting:N', title='Country')
            ).properties(
                title='Under-5 Mortality Rate by Sex - Country Comparison'
            )
            st.altair_chart(facet_chart, use_container_width=True)
    
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
            
            # Color scheme for quintiles (red = poorest, green = richest)
            quintile_colors = ['#d62728', '#ff7f0e', '#bcbd22', '#2ca02c', '#1f77b4']
            
            chart = alt.Chart(df_plot).mark_line(strokeWidth=2, point=True).encode(
                x=alt.X('date:O', title='Year', axis=alt.Axis(labelAngle=-45, values=list(range(1990, 2025, 5)))),
                y=alt.Y('estimate:Q', title='Mortality Rate (per 1,000 live births)'),
                color=alt.Color('quintile:N', title='Economic Status',
                               scale=alt.Scale(domain=quintile_labels, range=quintile_colors),
                               sort=quintile_labels),
                strokeDash=alt.StrokeDash('setting:N', title='Country'),
                tooltip=[
                    alt.Tooltip('setting:N', title='Country'),
                    alt.Tooltip('date:O', title='Year'),
                    alt.Tooltip('quintile:N', title='Economic Status'),
                    alt.Tooltip('estimate:Q', title='Mortality Rate', format='.1f')
                ]
            ).properties(
                width=800,
                height=400,
                title='Under-5 Mortality Rate by Economic Status (Wealth Quintile)'
            )
            
            st.altair_chart(chart, use_container_width=True)
            
            # Add faceted view for two countries
            if len(selected_countries) == 2:
                st.subheader("Side-by-Side Comparison")
                facet_chart = alt.Chart(df_plot).mark_line(strokeWidth=2, point=True).encode(
                    x=alt.X('date:O', title='Year', axis=alt.Axis(labelAngle=-45, values=list(range(1990, 2025, 5)))),
                    y=alt.Y('estimate:Q', title='Mortality Rate'),
                    color=alt.Color('quintile:N', title='Economic Status',
                                   scale=alt.Scale(domain=quintile_labels, range=quintile_colors),
                                   sort=quintile_labels),
                    tooltip=[
                        alt.Tooltip('setting:N', title='Country'),
                        alt.Tooltip('date:O', title='Year'),
                        alt.Tooltip('quintile:N', title='Economic Status'),
                        alt.Tooltip('estimate:Q', title='Mortality Rate', format='.1f')
                    ]
                ).facet(
                    column=alt.Column('setting:N', title='Country')
                ).properties(
                    title='Under-5 Mortality Rate by Economic Status - Country Comparison'
                )
                st.altair_chart(facet_chart, use_container_width=True)

# -----------------------------------------------------------------------------
# Footer with data information
# -----------------------------------------------------------------------------
st.markdown("---")
st.caption(f"Data Source: UN IGME | Last Updated: {df['update'].iloc[0]} | Countries: {df['setting'].nunique()} | Years: {df['date'].min()}-{df['date'].max()}")
