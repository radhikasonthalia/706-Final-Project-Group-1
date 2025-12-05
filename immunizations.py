import pandas as pd
import altair as alt

# Load the Excel file
df = pd.read_excel('immunizations.xlsx')

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

