# SpaceX Launch Records Dashboard - Complete Solution
# All 4 Tasks Answered

import pandas as pd
import dash
from dash import dcc, html
from dash.dependencies import Input, Output
import plotly.express as px

# ── Load dataset ─────────────────────────────────────────────────────────────
# When running locally, download the CSV first:
# wget "https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBM-DS0321EN-SkillsNetwork/datasets/spacex_launch_dash.csv"

spacex_df = pd.read_csv("spacex_launch_dash.csv")
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# ── Initialise the Dash app ───────────────────────────────────────────────────
app = dash.Dash(__name__)

# ── App Layout ────────────────────────────────────────────────────────────────
app.layout = html.Div(children=[

    html.H1(
        'SpaceX Launch Records Dashboard',
        style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}
    ),

    # ── TASK 1: Launch Site Drop-down Input Component ─────────────────────────
    dcc.Dropdown(
        id='site-dropdown',
        options=[
            {'label': 'All Sites', 'value': 'ALL'},
            {'label': 'CCAFS LC-40',  'value': 'CCAFS LC-40'},
            {'label': 'CCAFS SLC-40', 'value': 'CCAFS SLC-40'},
            {'label': 'KSC LC-39A',   'value': 'KSC LC-39A'},
            {'label': 'VAFB SLC-4E',  'value': 'VAFB SLC-4E'},
        ],
        value='ALL',                          # default: all sites selected
        placeholder='Select a Launch Site here',
        searchable=True
    ),

    html.Br(),

    # Pie chart output
    html.Div(dcc.Graph(id='success-pie-chart')),

    html.Br(),

    html.P("Payload range (Kg):"),

    # ── TASK 3: Range Slider to Select Payload ────────────────────────────────
    dcc.RangeSlider(
        id='payload-slider',
        min=0,
        max=10000,
        step=1000,
        marks={
            0:     '0',
            2500:  '2500',
            5000:  '5000',
            7500:  '7500',
            10000: '10000'
        },
        value=[min_payload, max_payload]      # default: full range selected
    ),

    html.Br(),

    # Scatter chart output
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])


# ── TASK 2: Callback – Pie Chart ──────────────────────────────────────────────
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown',      component_property='value')
)
def get_pie_chart(entered_site):
    if entered_site == 'ALL':
        # Show total successful launches broken down by site
        fig = px.pie(
            spacex_df,
            values='class',
            names='Launch Site',
            title='Total Success Launches By Site'
        )
    else:
        # Filter to selected site and count class=0 vs class=1
        filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
        site_counts = filtered_df['class'].value_counts().reset_index()
        site_counts.columns = ['class', 'count']
        site_counts['outcome'] = site_counts['class'].map({1: 'Success', 0: 'Failure'})

        fig = px.pie(
            site_counts,
            values='count',
            names='outcome',
            title=f'Total Success Launches for site {entered_site}'
        )
    return fig


# ── TASK 4: Callback – Scatter Chart ─────────────────────────────────────────
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [
        Input(component_id='site-dropdown',   component_property='value'),
        Input(component_id='payload-slider',  component_property='value')
    ]
)
def get_scatter_chart(entered_site, payload_range):
    low, high = payload_range

    # Filter by payload range first
    mask = (
        (spacex_df['Payload Mass (kg)'] >= low) &
        (spacex_df['Payload Mass (kg)'] <= high)
    )
    filtered_df = spacex_df[mask]

    if entered_site == 'ALL':
        fig = px.scatter(
            filtered_df,
            x='Payload Mass (kg)',
            y='class',
            color='Booster Version Category',
            title='Correlation between Payload and Success for all Sites',
            labels={'class': 'Launch Outcome (1=Success, 0=Failure)'}
        )
    else:
        # Further filter to selected site
        site_df = filtered_df[filtered_df['Launch Site'] == entered_site]
        fig = px.scatter(
            site_df,
            x='Payload Mass (kg)',
            y='class',
            color='Booster Version Category',
            title=f'Correlation between Payload and Success for site {entered_site}',
            labels={'class': 'Launch Outcome (1=Success, 0=Failure)'}
        )
    return fig


# ── Run ───────────────────────────────────────────────────────────────────────
if __name__ == '__main__':
    app.run_server(debug=True, port=8050)
