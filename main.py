### toolkit
import data_manager as dm

import os
import pandas as pd

import plotly.express as px
import plotly.graph_objs as go

import dash
from dash import dcc
from dash import html
import dash_bootstrap_components as dbc
from dash.dependencies import Input, Output


### load data
df_name = 'energy_data_clean.csv'
data_manager = dm.DataManager(df_name)
df = data_manager.df


app = dash.Dash(__name__, external_stylesheets=[dbc.themes.BOOTSTRAP])

# -------------------------------------------------#
def empty_choropleth():
    # empty choropleth map
    fig = px.choropleth(
        pd.DataFrame({'country': [], 'bin': []}), 
        locations='country', 
        locationmode='country names', 
        color='bin',
        color_discrete_sequence=[], 
        labels={},
        category_orders={'bin': []}, 
        hover_name='country',
        hover_data={'country':False, 'bin':True}
    )
    fig.update_layout(
        legend_title_text=''
    )
    return fig


def empty_trend():
    # empty trend chart
    fig = px.line(
        pd.DataFrame({'year': [], 'value': []}), 
        x='year', 
        y='value', 
        labels={'value': ''}
    )
    return fig
# -------------------------------------------------#
def filter_by_country(desired_source, desired_metric, desired_country, desired_year):
    desired_col = desired_source + '_' + desired_metric

    necessary_cols = ['year']
    necessary_cols.append(desired_col)

    desired_data = df[(df['country'] == desired_country) & (df['year'] <= desired_year)].loc[:, necessary_cols]

    # remove rows with null values
    desired_data = desired_data.dropna()

    return desired_data, desired_col


def filter_by_year(desired_source, desired_metric, desired_year):
    desired_col = desired_source + '_' + desired_metric

    necessary_cols = ['country']
    necessary_cols.append(desired_col)

    desired_data = df[(df['year'] == desired_year)].loc[:, necessary_cols]

    # select only countries
    desired_data = desired_data[desired_data['country'].isin(data_manager.countries)]

    # remove rows with null values
    desired_data = desired_data.dropna()

    return desired_data, desired_col
# -------------------------------------------------#



def generate_trend(desired_source, desired_metric, desired_country, desired_year):
    desired_data, desired_col = filter_by_country(desired_source, desired_metric, desired_country, desired_year)
    if desired_data.empty:
        return empty_trend()
    
    # create line chart
    fig = px.line(
        desired_data, 
        x='year', 
        y=desired_col, 
        labels={desired_col: dm.metric_label_map[desired_metric]}
    )
    return fig


def generate_choropleth(desired_source, desired_metric, desired_year):
    desired_data, desired_col = filter_by_year(desired_source, desired_metric, desired_year)
    if desired_data.empty:
        return empty_choropleth()

    # split into n equal frequency bins
    n_bins = 6
    if len(desired_data) < n_bins:
        n_bins = len(desired_data)

    desired_data['bin'] = pd.qcut(desired_data[desired_col], n_bins, labels=False, duplicates='drop')

    bin_labels = []
    for bin_num in range(n_bins):
        min_val, max_val = desired_data[desired_data['bin'] == bin_num].describe().loc[['min', 'max'], desired_col].values
        label = f'{min_val} - {max_val}'
        bin_labels.append(label)

    # given label to each data point
    desired_data['bin'] = desired_data['bin'].apply(lambda x: bin_labels[x])

    # make discrete color scale from sequential color scale and n_bins
    color_scale = px.colors.sequential.Reds

    # make discrete color scale
    discrete_color_scale = []
    for i in range(n_bins):
        discrete_color_scale.append(color_scale[int(i * len(color_scale) / n_bins)])


    # Create a dictionary mapping the bin labels to the corresponding color
    color_map = dict(zip(bin_labels, discrete_color_scale))

    # Create the choropleth map using Plotly Express
    fig = px.choropleth(
        desired_data, 
        locations='country', 
        locationmode='country names', 
        color='bin',
        color_discrete_sequence=discrete_color_scale, 
        labels={desired_col: desired_col},
        category_orders={'bin': bin_labels}, 
        hover_name='country',
        hover_data={'country':False, desired_col:True, 'bin':True}
    )


    fig.update_layout(
        legend_title_text=f'{dm.metric_label_map[desired_metric]} by {dm.source_label_map[desired_source]}'
    )

    return fig

main_style = {'font-family': 'Arial', 'max-width':'1200px', 'align-content':'center', 'margin':'auto', 'padding':'20px'}

# -------------------------------------------------#
main_layout = html.Div([
    html.H1("Energy Data Visualization", style={'text-align':'center', 'font-family': 'Arial', 'size':'50px'}),
    html.Div(children=[
        html.Div(children = [
            html.Label("Source"),
            dcc.Dropdown(
                id='source-dropdown',
                options=[
                    {'label': dm.source_label_map[source], 'value': source} for source in dm.source_label_map.keys()
                ],
                value=None
            )
        ], style={'padding':'10px', 'width': '300px', 'display': 'inline-block', 'background-color':'#f8f9fa', 'margin':'10px'}),

        html.Div(children = [
            html.Label("Metric"),
            dcc.Dropdown(
                id='metric-dropdown',
                options=[],
                value=None
            ),
        ], style={'padding':'10px', 'width': '500px', 'display': 'inline-block', 'background-color':'#f8f9fa'}),
            
    ], style = { 'vertical-align': 'top','align-content':'center'}),
    
    dcc.Graph(id='chart', style={'height': '800px', 'width': '1200px'}),
    html.Div(children = [
        html.H4("Year", style={'text-align':'center', 'font-family': 'Arial', 'size':'50px'}),

        dcc.Slider(
            id='year-slider',
            min=df['year'].min(),
            max=df['year'].max(),
            value=None,
            step=1,
            marks=None,
            tooltip={'placement': 'bottom', 'always_visible': True}
        ),
    ], style = {'padding':'10px', 'width': '1000px', 'align-content':'center', 'margin':'auto', 'background-color':'#f8f9fa'}),
        
    html.Div(children = [
        html.H3(id = 'country-title', style={'text-align':'center', 'font-family': 'Arial', 'size':'50px'}),
        dcc.Graph(id='trend-chart')
    ], style={'padding':'10px', 'width': '1200px', 'align-content':'center', 'margin':'auto'}),
    
], style = main_style)


# update metric dropdown based on source dropdown
@app.callback(
    dash.dependencies.Output('metric-dropdown', 'options'),
    [dash.dependencies.Input('source-dropdown', 'value')])
def update_metric_dropdown(source):
    if source is None:
        return []
    else:
        metrics = data_manager.source_metric_map[source]
        return [{'label': dm.metric_label_map[metric], 'value': metric} for metric in metrics]


# update choropleth chart based on source, metric, and year
@app.callback(
    dash.dependencies.Output('chart', 'figure'),
    [dash.dependencies.Input('source-dropdown', 'value'),
    dash.dependencies.Input('metric-dropdown', 'value'),    
    dash.dependencies.Input('year-slider', 'value')])
def update_chart(source, metric, year):
    if source is None or metric is None:
        return empty_choropleth()
    else:
        fig = generate_choropleth(source, metric, year)
        return fig


# update trend chart based on source, metric, year, and country
@app.callback(
    dash.dependencies.Output('trend-chart', 'figure'),
    dash.dependencies.Output('country-title', 'children'),
    [dash.dependencies.Input('source-dropdown', 'value'),
     dash.dependencies.Input('metric-dropdown', 'value'),
     dash.dependencies.Input('chart', 'clickData'), 
     dash.dependencies.Input('year-slider', 'value')])
def update_trend_chart(source, metric, clickData, year):
    country = 'country'
    country_title = html.Div(f'Trend for {country}')
    
    if source is None or metric is None:
        return empty_trend(), country_title

    if clickData:
        country = clickData['points'][0]['location']
        country_title = html.Div(f'Trend for {country} upto {year}')
    else:
        return empty_trend(), country_title

    fig = generate_trend(source, metric, country, year)

    
    return fig, country_title

home_layout = html.Div([
    dbc.Alert([
        html.H1("Welcome to my Dash app!", className="display-3"),
        html.P("This is the opening page of my app. Click the button below to go to the next page."),
        html.Hr(),
        dbc.Button("Go to Graphs", color="primary", href="/graphs")
    ], className="text-center")
])

app.layout = html.Div([
    dcc.Location(id='url', refresh=False),
    html.Div(id='page-content')
])

@app.callback(Output('page-content', 'children'),
              [Input('url', 'pathname')])
def display_page(pathname):
    if pathname == '/':
        return home_layout
    elif pathname == '/graphs':
        return main_layout
    else:
        return '404 Page Not Found'

if __name__ == '__main__':
    app.run_server(debug=False)