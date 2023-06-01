import pandas as pd
import dash
from dash import html
from dash import dcc
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
import plotly.express as px
from dash import no_update

# Create a dash application
app = dash.Dash(__name__)

# REVIEW1: Clear the layout and do not display exception till callback gets executed
app.config.suppress_callback_exceptions = True

# Read the airline data into pandas dataframe
spacex_df = pd.read_csv('https://cf-courses-data.s3.us.cloud-object-storage.appdomain.cloud/IBM-DS0321EN-SkillsNetwork/datasets/spacex_launch_dash.csv',
                        encoding="ISO-8859-1",
                        dtype={'Div1Airport': str, 'Div1TailNum': str,
                               'Div2Airport': str, 'Div2TailNum': str})

# get the unique sites and also add 'All' to the beginning, this list will be used in the dropdown for launch site selection
sites = set(spacex_df['Launch Site'])
sites = list(sites)
sites.insert(0, 'All')

payload_mass_min=spacex_df['Payload Mass (kg)'].min()
payload_mass_max=spacex_df['Payload Mass (kg)'].max()

app.layout = html.Div(children=[
    html.H1('SpaceX Launch Records Dashboard',
            style={'textAlign': 'center', 'color': '#503D36', 'font-size': 40}),

    html.Br(),
    dcc.Dropdown(id='launch-site-dropdown',
                 options=[{'label': i, 'value': i} for i in sites],
                 value='All',
                 placeholder="Please select site(s)",
                 searchable=True),  # replace with your real site names
   
    html.Div(dcc.Graph(id='success-pie-chart')),
  

    html.Br(),

    html.P("Payload range (Kg):"),
    dcc.RangeSlider(
        id='payload-range-slider',
        marks={i: str(i) for i in range(0, 17501, 2500)},
        min=0,
        max=17500,
        step=1,
        value=[0, 17500]
    ),
    dcc.Graph(id='success-payload-scatter-chart'),
])

# Function decorator to specify function input and output
@app.callback(Output(component_id='success-pie-chart', component_property='figure'),
              Input(component_id='launch-site-dropdown', component_property='value')
              )
def get_pie_chart(entered_site):
    # Step 1: Calculate the total number of successful launches
    filtered_df = spacex_df[spacex_df['Launch Site'] == entered_site]
    if entered_site == 'All':
        # Step 1: Calculate the total number of successful launches
        total_successes = spacex_df[spacex_df['class'] == 1]['class'].count()
        # Step 2: Calculate the number of successes for each launch site
        site_successes = spacex_df[spacex_df['class'] == 1].groupby('Launch Site')['class'].count()
        # Step 3: Calculate the proportion of successes for each launch site
        site_success_proportions = site_successes / total_successes
        # Step 4: Create the pie chart using Plotly Express
        fig_pie_chart_all = px.pie(spacex_df, values=site_success_proportions.values, names=site_success_proportions.index,
            title='Success launch all site(s)')
        return fig_pie_chart_all
    else:
        filtered_df['class_label'] = filtered_df['class'].map({0: 'Success', 1: 'Failure'})
        value_counts = filtered_df['class_label'].value_counts()
        fig_pie_chart_by_site = px.pie(names=value_counts.index, values=value_counts.values, title='Total success launches for site ' + entered_site)
        return fig_pie_chart_by_site
    
@app.callback(Output(component_id='success-payload-scatter-chart', component_property='figure'),
              [Input(component_id='launch-site-dropdown', component_property='value'), 
               Input(component_id="payload-range-slider", component_property="value")])
def update_scatter_chart(selected_site, payload_range):
   
    low, high = payload_range
    if selected_site == 'All':
        filtered_df = spacex_df[spacex_df['Payload Mass (kg)'].between(low, high)]
    else:
        filtered_df = spacex_df[(spacex_df['Launch Site'] == selected_site) & 
                                (spacex_df['Payload Mass (kg)'].between(low, high))]
    
    fig = px.scatter(filtered_df, x='Payload Mass (kg)', y='class', color='Booster Version Category')
    return fig



if __name__ == '__main__':
    app.run_server(debug=True)
