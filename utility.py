import pandas as pd
import numpy as np
import constants as c
from datetime import timedelta

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