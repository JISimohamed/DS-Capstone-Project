# Import required libraries
import pandas as pd
from dash import Dash, dcc, html
from dash.dependencies import Input, Output
import plotly.express as px

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv("spacex_launch_dash.csv")

# Inspect the columns to check for 'Launch Site'
print(spacex_df.columns)

# Get the maximum and minimum values for Payload Mass
max_payload = spacex_df['Payload Mass (kg)'].max()
min_payload = spacex_df['Payload Mass (kg)'].min()

# Create a dash application
app = Dash(__name__)

# Dropdown options
dropdown_options = [{'label': 'All Sites', 'value': 'ALL'}] + [
    {'label': site, 'value': site} for site in spacex_df['Launch Site'].unique()  # Corrected 'LaunchSite' to 'Launch Site'
]

# Create an app layout
app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),
    
    # TASK 1: Add a dropdown list to enable Launch Site selection
    dcc.Dropdown(id='site-dropdown',
                 options=dropdown_options,
                 value='ALL',
                 placeholder="Select a Launch Site here",
                 searchable=True),
    html.Br(),

    # TASK 2: Add a pie chart to show the total successful launches count for all sites
    html.Div(dcc.Graph(id='success-pie-chart')),
    html.Br(),

    html.P("Payload range (Kg):"),
    # TASK 3: Add a slider to select payload range
    dcc.RangeSlider(id='payload-slider',
                    min=0,
                    max=10000,
                    step=1000,
                    value=[0, 10000],
                    marks={i: f'{i} Kg' for i in range(0, 10001, 1000)},
                    tooltip={"placement": "bottom", "always_visible": True}),
    html.Div(dcc.Graph(id='success-payload-scatter-chart')),
])

# TASK 2: Add a callback function for `site-dropdown` as input, `success-pie-chart` as output
@app.callback(
    Output(component_id='success-pie-chart', component_property='figure'),
    Input(component_id='site-dropdown', component_property='value')
)
def update_pie_chart(selected_site):
    if selected_site == 'ALL':
        # Aggregate success counts across all sites
        pie_data = spacex_df['class'].value_counts().reset_index()
        pie_data.columns = ['Outcome', 'Count']
        fig = px.pie(
            pie_data,
            values='Count',
            names='Outcome',
            title='Total Success and Failure Launches (All Sites)'
        )
    else:
        # Filter data for the selected site
        filtered_df = spacex_df[spacex_df['Launch Site'] == selected_site]  # Corrected column name
        pie_data = filtered_df['class'].value_counts().reset_index()
        pie_data.columns = ['Outcome', 'Count']
        fig = px.pie(
            pie_data,
            values='Count',
            names='Outcome',
            title=f'Success and Failure Launches for {selected_site}'
        )
    return fig

# TASK 4: Add a callback function for `site-dropdown` and `payload-slider` as inputs, `success-payload-scatter-chart` as output
@app.callback(
    Output(component_id='success-payload-scatter-chart', component_property='figure'),
    [Input(component_id='site-dropdown', component_property='value'),
     Input(component_id='payload-slider', component_property='value')]
)
def update_scatter_plot(selected_site, payload_range):
    # Filter data based on the payload range
    low, high = payload_range
    filtered_df = spacex_df[(spacex_df['Payload Mass (kg)'] >= low) & (spacex_df['Payload Mass (kg)'] <= high)]

    if selected_site == 'ALL':
        # Scatter plot for all sites
        fig = px.scatter(
            filtered_df,
            x='Payload Mass (kg)',
            y='class',
            color='Booster Version Category',  # Corrected column name
            title='Payload vs. Outcome for All Sites',
            labels={'class': 'Launch Outcome'}
        )
    else:
        # Filter data for the selected site
        site_df = filtered_df[filtered_df['Launch Site'] == selected_site]  # Corrected column name
        # Scatter plot for the selected site
        fig = px.scatter(
            site_df,
            x='Payload Mass (kg)',
            y='class',
            color='Booster Version Category',  # Corrected column name
            title=f'Payload vs. Outcome for {selected_site}',
            labels={'class': 'Launch Outcome'}
        )
    return fig

# Run the app
if __name__ == '__main__':
    app.run_server(debug=True, port=8051)
