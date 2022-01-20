import pandas as pd
import numpy as np
import constants as c
from datetime import timedelta
import plotly.graph_objects as go


def get_unique_values(data, field):
    """
    Returns a list of unique values of a field from the dataset
    """
    return list(data[field].unique())


def get_date(data, func):
    """
    Returns first (min) or last (max) date from a dataset
    """
    return pd.to_datetime(
        str(func(data[c.DATE].unique()))
    ).strftime('%m/%d/%Y')


def get_last_date(data):
    """
    Returns last (max) date + 1 day from a dataset
    """
    return pd.to_datetime(
        str(max(data[c.DATE].unique()) + np.timedelta64(1, 'D'))
    ).strftime('%m/%d/%Y')


def filter_dataset_by_date(data, start_date, end_date):
    """
    Filters dataset based on the start and end date
    """
    if start_date is None:
        beginning_date = pd.to_datetime(get_date(data, min))
    else:
        beginning_date = pd.to_datetime(start_date)
    if end_date is None:
        ending_date = pd.to_datetime(get_date(data, max))
    else:
        ending_date = pd.to_datetime(end_date)

    filtered_dataset = data[
        data[c.DATE].ge(beginning_date) &
        data[c.DATE].le(ending_date)
    ]
    return filtered_dataset


def get_traffic_variations(data):
    
    traffic_variations = pd.pivot_table(
        data,
        values=[c.MA, c.FLIGHTS, c.FLIGHTS_2019, c.FLIGHTS_2020],
        index=c.DATE,
        aggfunc=np.sum
    )
    traffic_variations = traffic_variations.reset_index()
    traffic_variations[c.MA_2019] = traffic_variations[c.FLIGHTS_2019].rolling(7, min_periods=1).mean()
    return traffic_variations


def get_traffic_variability_chart(data):
    """
    Return a traffic variability chart (2019 vs now) based on parsed data
    """
    fig_data = get_traffic_variations(data)
    
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
        )
    )
    return fig
