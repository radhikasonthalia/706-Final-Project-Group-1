import altair as alt
import pandas as pd
import streamlit as st

# Page configuration
st.set_page_config(page_title="Under-5 Mortality Rate Dashboard", layout="wide")

# Load the data
@st.cache_data
def load_data():
    # Update this path to match your local file location
    df = pd.read_excel('under5_mortality.xlsx')
    return df

df = load_data()

# Title
st.title("📈 Under-5 Mortality Rate Trends")
st.markdown("*Deaths per 1,000 live births*")

# -----------------------------------------------------------------------------
# Interactive Line Charts
# -----------------------------------------------------------------------------
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
            detail='setting:N',  # separate line per country but no legend
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
        
        # Use faceting by country - much clearer than strokeDash legend
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
            width=350,
            height=400,
            title='Under-5 Mortality Rate by Sex'
        ).facet(
            column=alt.Column('setting:N', title='Country')
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
            
            # Color scheme for quintiles (red = poorest, green = richest)
            quintile_colors = ['#d62728', '#ff7f0e', '#bcbd22', '#2ca02c', '#1f77b4']
            
            # Use faceting by country for clear separation
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
                width=350,
                height=400,
                title='Under-5 Mortality Rate by Economic Status (Wealth Quintile)'
            ).facet(
                column=alt.Column('setting:N', title='Country')
            )
            
            st.altair_chart(chart, use_container_width=True)

# -----------------------------------------------------------------------------
# Footer with data information
# -----------------------------------------------------------------------------
st.markdown("---")
st.caption(f"Data Source: UN IGME | Last Updated: {df['update'].iloc[0]} | Countries: {df['setting'].nunique()} | Years: {df['date'].min()}-{df['date'].max()}")
