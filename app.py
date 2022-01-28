import pandas as pd
import dash
import dash_bootstrap_components as dbc
import constants as c
from dash import html, dcc
from dash.dependencies import Input, Output, State
import plotly.graph_objects as go
import utility as u
from data_load import states, airports, area_centers
import calculations

import json

app = dash.Dash(
    __name__,
    external_stylesheets=[
        dbc.themes.BOOTSTRAP,
        '1_sidebar_styles.css'
    ],
    meta_tags=[
        {"name": "viewport", "content": "width=device-width, initial-scale=1"},
    ]
)

with open('assets/europe.geojson') as file:
    countries = json.load(file)


app.title = 'European Air Traffic Dashboard'
server = app.server

# we use the Row and Col components to construct the sidebar header
# it consists of a title, and a toggle, the latter is hidden on large screens
sidebar_header = dbc.Row(
    [
        dbc.Col(
            html.H2("Filters", className="display-6"),
            id='filter_header'
        ),
        dbc.Col(
            html.H2("European Air Traffic Dashboard", className="display-6"),
            id='header_small'
        ),
        dbc.Col(
            [
                html.Button(
                    # use the Bootstrap navbar-toggler classes to style
                    html.Span(className="navbar-toggler-icon"),
                    className="navbar-toggler",
                    # the navbar-toggler classes don't set color
                    style={
                        "color": "rgba(0,0,0,.5)",
                    #    "border-color": "rgba(0,0,0,.1)",
                        "border": None
                    },
                    id="navbar-toggle",
                ),
                html.Button(
                    # use the Bootstrap navbar-toggler classes to style
                    html.Span(className="navbar-toggler-icon"),
                    className="navbar-toggler",
                    # the navbar-toggler classes don't set color
                    style={
                        "color": "rgba(0,0,0,.5)",
                    #    "border-color": "rgba(0,0,0,.1)",
                        "border": None
                    },
                    id="sidebar-toggle",
                ),
            ],
            # the column containing the toggle will be only as wide as the
            # toggle, resulting in the toggle being right aligned
            width="auto",
            # vertically align the toggle in the center
            align="center",
        ),
    ]
)

sidebar = html.Div(
    [
        sidebar_header,
        # we wrap the horizontal rule and short blurb in a div that can be
        # hidden on a small screen
        html.Div(
            [html.Hr()],
            id="blurb",
        ),
        # use the Collapse component to animate hiding / revealing links
        dbc.Collapse(
            dbc.Container([
                dbc.Row(
                    dbc.Col(
                        dcc.Dropdown(
                            id='states_list',
                            options=[
                                {'label': x, 'value': x} for x in calculations.get_unique_values(states, c.ENTITY)
                            ],
                            multi=True,
                            clearable=True,
                            placeholder='Select States',
                            style=c.DROPDOWN_STYLE
                        )
                    ),
                    style=c.FILTER_ITEM_ROW),
                dbc.Row(
                    dbc.Col(
                        dcc.Dropdown(
                            id='acc_list',
                            multi=True,
                            clearable=True,
                            placeholder='Select ACCs',
                            style=c.DROPDOWN_STYLE
                        )
                    ),
                    style=c.FILTER_ITEM_ROW),
                dbc.Row(
                    dbc.Col(
                        dcc.Dropdown(
                            id='airport_list',
                            multi=True,
                            clearable=True,
                            placeholder='Select Airports',
                            style=c.DROPDOWN_STYLE
                        )
                    ),
                    style=c.FILTER_ITEM_ROW),
                dbc.Row(
                    dbc.Col(
                        dcc.Dropdown(
                            id='aircraft_operator_list',
                            options=[
                                {'label': x, 'value': x} for x in ['Ryanair Group', 'Wizz Air Group']
                            ],
                            multi=True,
                            clearable=True,
                            placeholder='Select Aircraft Operators',
                            style=c.DROPDOWN_STYLE
                        )
                    ),
                    style=c.FILTER_ITEM_ROW),
                dbc.Row([
                    dbc.Col(
                        html.H6("From: ", style={'marginBottom': '0'}),
                        xs=12, md=12, lg=3, xl=3
                    ),
                    dbc.Col(
                        dcc.DatePickerSingle(id='start_date_picker'),
                        xs=12, md=12, lg=9, xl=9
                    )
                    ],
                    style=c.FILTER_ITEM_ROW,
                    align='center'
                ),
                dbc.Row([
                    dbc.Col(
                        html.H6("To: ", style={'marginBottom': '0'}),
                        xs=12, md=12, lg=3, xl=3
                    ),
                    dbc.Col(
                        dcc.DatePickerSingle(id='end_date_picker'),
                        xs=12, md=12, lg=9, xl=9
                    )
                    ],
                    style=c.FILTER_ITEM_ROW,
                    align='center'
                ),
                dbc.Row(
                    dbc.Col(
                        html.H6("Airport traffic type"),
                    ),
                    style=c.FILTER_ITEM_ROW,
                    align='left'
                ),
                dbc.Row([
                    dbc.Col(
                        dbc.Checklist(
                            options=[{'label': x, 'value': x} for x in ['Arrival', 'Departure']],
                            id='ifr_movements',
                            value=[x for x in ['Arrival', 'Departure']],
                            switch=True,
                            inline=True
                        )
                    )],
                    style=c.FILTER_ITEM_ROW,
                    align='center'
                )
            ]),
            id="collapse"
        ),
    ],
    id="sidebar",
    className="collapsed"
)

state_traffic_tab = dcc.Tab(
    label='State Traffic',
    id='state_traffic_tab',
    value='state_traffic_tab',
    children=[
        dbc.Container([
            dbc.Row([
                dbc.Col(
                  html.Div([
                    html.H5(
                      "Overview of average daily traffic per state",
                      className='section_title'
                    ),
                    dcc.Graph(id='states_map')
                  ]),xs=12, md=12, lg=8, xl=8
                ),
                dbc.Col(
                  html.Div([
                    html.H5(
                      "Top 10 States by average daily traffic",
                      className='section_title'
                    ),
                    dcc.Graph(id='top_10_states')
                  ]),xs=12, md=12, lg=4, xl=4
                )
            ]),
            dbc.Row(
                dbc.Col(
                    html.Div([
                        html.H5(
                            "State Daily Traffic Variation",
                            className='section_title'
                        ),
                        dcc.Graph(id='states_traffic_variation')
                    ]),xs=12, md=12, lg=12, xl=12
                )
            ),
            dbc.Row(
                dbc.Col(
                    html.Div([
                        html.H5(
                            "Average Daily Number of Flights per ACC",
                            className='section_title'
                        ),
                        dcc.Graph(id='acc_state_traffic')
                    ]),xs=12, md=12, lg=12, xl=12
                )
            ),
            dbc.Row(
                dbc.Col(
                    html.Div([
                        html.H5(
                            "Average Daily Number of Flights per State",
                            className='section_title'
                        ),
                        dcc.Graph(id='state_traffic_bar_chart')
                    ]),xs=12, md=12, lg=12, xl=12
                )
            )
        ])
    ]
)

airport_traffic_tab = dcc.Tab(
    label='Airport Traffic',
    id='airport_traffic_tab',
    value='airport_traffic_tab',
    children=[
        dbc.Container([
            dbc.Row([
                dbc.Col(
                    html.Div([
                        html.H5(
                            "Overview of daily flights per airport",
                            className='section_title'
                            ),
                        dcc.Graph(id='airport_map')
                    ]),
                    xs=12, md=12, lg=8, xl=8
                ),
                dbc.Col(
                    html.Div([
                        html.H5(
                            "Top 10 airports by average daily traffic",
                            className='section_title'
                        ),
                        dcc.Graph(id='top_10_airports')
                    ]),
                    xs=12, md=12, lg=4, xl=4
                )
            ]),
            dbc.Row(
                dbc.Col(
                    html.Div([
                        html.H5(
                            "Airport Daily Traffic Variation",
                            className='section_title'
                        ),
                        dcc.Graph(id='airport_traffic_variation')
                    ]),
                    xs=12, md=12, lg=12, xl=12
                )
            )
        ])
    ]
)

aircraft_operator_traffic_tab = dcc.Tab(
    label='Aircraft Operator Traffic',
    id='aircraft_operator_traffic_tab',
    value='aircraft_operator_traffic_tab',
    children=[
        dbc.Container(

        )
    ]
)

tabs = html.Div([
  dcc.Tabs(
      children=[
        state_traffic_tab,
        airport_traffic_tab,
        aircraft_operator_traffic_tab
      ],
    id='content_tabs',
    value='state_traffic_tab'
  )  
])

header = dbc.Container(
    dbc.Row(
        dbc.Col(
            html.H2(
                "European Air Traffic Dashboard",
                style={'textAlign': 'center'},
            ),
            xs=12, md=12, lg=12, xl=12
        )
    ),
    style={
        'marginBottom': '2%'
    },
    id="header_big"
)

content = html.Div(children=[
        header,
        tabs
    ],
    className='page-content',
    id="page-content"
)


app.layout = html.Div([sidebar, content])

# ---- Callbacks for controls ----- #
@app.callback(
    Output("sidebar", "className"),
    [Input("sidebar-toggle", "n_clicks")],
    [State("sidebar", "className")],
)
def toggle_classname(n, classname):
    if n and classname == "collapsed":
        return ""
    return "collapsed"


@app.callback(
    Output("collapse", "is_open"),
    [Input("navbar-toggle", "n_clicks")],
    [State("collapse", "is_open")],
)
def toggle_collapse(n, is_open):
    if n:
        return not is_open
    return is_open


# TODO: callback on list of states when the data for airport is ready
@app.callback(
    Output('airport_list', 'options'),
    Input('states_list', 'value'),
)
def update_airport_list(list_of_states):
    if list_of_states:
        filtered_data = calculations.filter_airport_dataset(
            data=airports,
            states=list_of_states
        )
        return [{'label': x, 'value': x} for x in calculations.get_unique_values(filtered_data, c.AIRPORT_NAME)]
    else:
        return [{'label': x, 'value': x} for x in calculations.get_unique_values(airports, c.AIRPORT_NAME)]



@app.callback(
    Output('acc_list', 'options'),
    Input('states_list', 'value')
)
def update_acc_list(list_of_states):
    if list_of_states:
        filtered_data = calculations.filter_area_center_data(
            data=area_centers,
            states=list_of_states
        )
        return [{'label': x, 'value': x} for x in calculations.get_unique_values(filtered_data, c.ACC)]
    else:
        return [{'label': x, 'value': x} for x in calculations.get_unique_values(area_centers, c.ACC)]



@app.callback(
    Output('ifr_movements', 'options'),
    Output('ifr_movements', 'value'),
    Input('content_tabs', 'value')
)
def update_airport_traffic_checklist(tab):
    
    if tab == 'airport_traffic_tab':
        disabled = False
    else:
        disabled = True
    
    options = [
        {
            'label': 'Arrival',
            'value': 'Arrival',
            'disabled': disabled
        },
        {
            'label': 'Departure',
            'value': 'Departure',
            'disabled': disabled
        },
    ]

    values = [x for x in ['Arrival', 'Departure']]

    return options, values


@app.callback(
    Output("states_list", "disabled"),
    Output("acc_list", "disabled"),
    Output("airport_list", "disabled"),
    Output("aircraft_operator_list", "disabled"),
    Input("content_tabs", "value")
)
def select_relevant_controls(tab):
    if tab == 'state_traffic_tab':
        return False, False, True, True
    elif tab == 'airport_traffic_tab':
        return False, True, False, True
    elif tab == 'aircraft_operator_tab':
        return True, True, True, False
    else:
        return True, True, True, True


@app.callback(
    Output('start_date_picker', 'min_date_allowed'),
    Output('start_date_picker', 'max_date_allowed'),
    Output('start_date_picker', 'date'),
    Input('content_tabs', 'value')
)
def select_start_date(tab):
    if tab == 'state_traffic_tab':
        start_date = calculations.get_date(states, min)
        max_date = calculations.get_last_date(states)
    elif tab == 'airport_traffic_tab':
        start_date = calculations.get_date(airports, min)
        max_date = calculations.get_last_date(airports)
    else:
        start_date = None
        max_date = None
    return start_date, max_date, start_date


@app.callback(
    Output('end_date_picker', 'min_date_allowed'),
    Output('end_date_picker', 'max_date_allowed'),
    Output('end_date_picker', 'date'),
    Input('content_tabs', 'value')
)
def select_end_date(tab):
    if tab == 'state_traffic_tab':
        start_date = calculations.get_date(states, min)
        end_date = calculations.get_date(states, max)
        max_date = calculations.get_last_date(states)
    elif tab == 'airport_traffic_tab':
        start_date = calculations.get_date(airports, min)
        end_date = calculations.get_date(airports, max)
        max_date = calculations.get_last_date(airports)
    else:
        start_date = None
        end_date = None
        max_date = None
    return start_date, max_date, end_date


# ----- Callback for graphs ------ #


@app.callback(
    Output('airport_traffic_variation', 'figure'),
    Input('states_list', 'value'),
    Input('airport_list', 'value'),
    Input('start_date_picker', 'date'),
    Input('end_date_picker', 'date'),
    Input('ifr_movements', 'value')
)
def update_aiport_traffic_variability(list_of_states, list_of_airports, start_date, end_date, ifr):

    filtered_data = calculations.filter_airport_dataset(
        data=airports,
        states=list_of_states,
        airports=list_of_airports,
        start_date=start_date,
        end_date=end_date
    )

    flight_columns = calculations.get_flight_columns(ifr)
    fig_data = calculations.get_number_of_flights(filtered_data, flight_columns)

    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=fig_data[c.DATE],
            y=fig_data[c.NM_MA],
            mode='lines',
            name='Number of flights (recorded by NM)'
        )
    )

    fig.add_trace(
        go.Scatter(
            x=fig_data[c.DATE],
            y=fig_data[c.APT_MA],
            mode='lines',
            name='Number of flights (recorded by NM)'
        )
    )

    fig.update_layout(
        legend=dict(
            orientation="h",
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1,
        ),
        margin={"r": 10, "t": 20, "l": 10, "b": 10}
    )

    return fig


@app.callback(
    Output('top_10_airports', 'figure'),
    Input('start_date_picker', 'date'),
    Input('end_date_picker', 'date'),
    Input('ifr_movements', 'value')
)
def update_top_10_airports_figure(start_date, end_date, ifr):

    filtered_data = calculations.filter_airport_dataset(
        data=airports,
        start_date=start_date,
        end_date=end_date
    )

    flight_column = calculations.get_flight_column(ifr)

    figure_data = calculations.get_top_flight_airports(filtered_data, flight_column)
    figure_data = figure_data.sort_values(by=flight_column, ascending=True)
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=figure_data[flight_column],
            y=figure_data[c.AIRPORT_NAME],
            orientation='h',
            textposition = "inside",
            # texttemplate = "%{y} - %{x:.1f}"
            texttemplate = "%{y}"
        )
    )

    fig.update_yaxes(
      visible=False,
      showticklabels=False
    )

    fig.update_layout(
      margin={"r": 10, "t": 20, "l": 10, "b": 10}
    )
    
    return fig


@app.callback(
    Output('top_10_states', 'figure'),
    Input('start_date_picker', 'date'),
    Input('end_date_picker', 'date')
)
def update_top_10_states_figure(start_date, end_date):

    filtered_data = calculations.filter_states_data(
        data=states,
        start_date=start_date,
        end_date=end_date
    )

    figure_data = calculations.get_top_ten_states(filtered_data)
    figure_data = figure_data.sort_values(by=c.FLIGHTS, ascending=True)
    fig = go.Figure()
    fig.add_trace(
        go.Bar(
            x=figure_data[c.FLIGHTS],
            y=figure_data[c.ENTITY],
            orientation='h',
            textposition = "inside",
            # texttemplate = "%{y} - %{x:.1f}"
            texttemplate = "%{y}"
        )
    )

    fig.update_yaxes(
      visible=False,
      showticklabels=False
    )

    fig.update_layout(
      margin={"r": 10, "t": 20, "l": 10, "b": 10}
    )
    
    return fig

@app.callback(
    Output('states_map', 'figure'),
    Input('start_date_picker', 'date'),
    Input('end_date_picker', 'date')
)
def update_states_map(start_date, end_date):
    filtered_data = calculations.filter_states_data(
        data=states,
        start_date=start_date,
        end_date=end_date,
    )
    filtered_data = filtered_data[
        filtered_data[c.ENTITY].ne(c.TOT_NETWORK_AREA)
    ]

    figure_data = calculations.get_states_flight_data(filtered_data, c.ISO)

    fig = go.Figure()
    fig.add_trace(
        go.Choropleth(
            geojson=countries,
            locations=figure_data[c.ISO],
            z=figure_data[c.FLIGHTS],
            featureidkey="properties.ISO3",
            zmin = 0,
            zmax=max(figure_data[c.FLIGHTS])
        )
    )

    fig.update_geos(
        fitbounds="locations", 
        visible=False
    )
    fig.update_layout(
        margin={"r": 10, "t": 20, "l": 10, "b": 10}
    )
    
    return fig


@app.callback(
    Output('states_traffic_variation', 'figure'),
    Input('states_list', 'value'),
    Input('start_date_picker', 'date'),
    Input('end_date_picker', 'date')
)
def update_states_variation_graph(list_of_states, start_date, end_date):
    
    filtered_data = calculations.filter_states_traffic_variability(
        data=states,
        start_date=start_date,
        end_date=end_date,
        states=list_of_states
    )
    
    fig_data = calculations.get_traffic_variations(filtered_data)
    
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=fig_data[c.DATE],
            y=fig_data[c.MA],
            mode='lines+markers',
            name='Flights (Moving Average)'
        )
    )

    fig.add_trace(
        go.Scatter(
            x=fig_data[c.DATE],
            y=fig_data[c.MA_2019],
            mode='lines+markers',
            name='Flights 2019 (Moving Average)'
        )
    )

    fig.update_layout(
        legend=dict(
            orientation='h',
            yanchor="bottom",
            y=1.02,
            xanchor="right",
            x=1
        ),
        margin={"r": 10, "t": 20, "l": 10, "b": 10}
    )

    return fig


@app.callback(
    Output('acc_state_traffic', 'figure'),
    Input('states_list', 'value'),
    Input('acc_list', 'value'),
    Input('start_date_picker', 'date'),
    Input('end_date_picker', 'date')
)
def update_acc_per_state_figure(list_of_states, acc_centers, start_date, end_date):
    
    filtered_data = calculations.filter_area_center_data(
        data=area_centers,
        states=list_of_states,
        area_centers=acc_centers,
        start_date=start_date,
        end_date=end_date
    )

    figure_data = calculations.get_area_centers_data(filtered_data)

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            y=figure_data[c.FLIGHTS],
            x=figure_data[c.ACC]
        )
    )
    fig.update_layout(
        margin={"r": 10, "t": 20, "l": 10, "b": 10}
    )
    return fig


@app.callback(
    Output('state_traffic_bar_chart', 'figure'),
    Input('states_list', 'value'),
    Input('start_date_picker', 'date'),
    Input('end_date_picker', 'date')
)
def update_state_traffic_bar_figure(list_of_states, start_date, end_date):
    
    filtered_data = calculations.filter_states_data(
        data=states,
        states=list_of_states,
        start_date=start_date,
        end_date=end_date
    )
    filtered_data = filtered_data[
        filtered_data[c.ENTITY].ne(c.TOT_NETWORK_AREA)
    ]

    figure_data = calculations.get_states_flight_data(filtered_data, c.ENTITY)
    figure_data = figure_data.sort_values(by=c.FLIGHTS, ascending=False)

    fig = go.Figure()

    fig.add_trace(
        go.Bar(
            y=figure_data[c.FLIGHTS],
            x=figure_data[c.ENTITY]
        )
    )
    fig.update_layout(
        margin={"r": 10, "t": 20, "l": 10, "b": 10}
    )
    return fig

@app.callback(
    Output('airport_map', 'figure'),
    Input('states_list', 'value'),
    Input('airport_list', 'value'),
    Input('start_date_picker', 'date'),
    Input('end_date_picker', 'date'),
    Input('ifr_movements', 'value')
)
def update_airport_map(list_of_states, list_of_airports, start_date, end_date, ifr):

    filtered_data = calculations.filter_airport_dataset(
        data=airports,
        airports=list_of_airports,
        states=list_of_states,
        start_date=start_date,
        end_date=end_date
    )
    
    flight_column = calculations.get_flight_column(ifr)

    fig_data = calculations.get_daily_average_per_airport(filtered_data, flight_column)
    unfiltered_data = calculations.get_daily_average_per_airport(airports, flight_column)
    
    traces = [
        go.Choropleth(
            geojson=countries,
            locations=unfiltered_data[c.ISO],
            featureidkey="properties.ISO3",
            z=[0]*len(unfiltered_data[flight_column]),
            hoverinfo='skip',
            showscale=False
            # hovertemplate='<extra></extra>'
        ),
        go.Scattergeo(
            lon=fig_data['LONG'],
            lat=fig_data['LAT'],
            text=fig_data[c.AIRPORT_NAME],
            customdata=fig_data[flight_column],
            marker=dict(
              color='orange',
              size=fig_data[flight_column] / 30
            ),
            hovertemplate='%{text} - %{customdata:.1f} flights<extra></extra>'
        )
    ]
    fig = go.Figure(data=traces)

    fig.update_geos(
        fitbounds="locations", 
        visible=False
    )


    fig.update_layout(
        margin={"r": 10, "t": 20, "l": 10, "b": 10},
    )
    """
    fig.add_trace(
        go.Scattergeo(
            lon=fig_data['LONG'],
            lat=fig_data['LAT'],
            text=fig_data[c.AIRPORT_CODE],
            marker=dict(
              color='orange',
              size=fig_data[c.NM_TOTAL_FLIGHTS] / 50
            )
        )
    )
    

    
    """
    return fig


if __name__ == '__main__':
    # app.run_server(debug=True)
    app.run_server(debug=True, host='0.0.0.0')
