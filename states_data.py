import pandas as pd
import numpy as np
import constants as c
import utility as u
import pycountry
import datetime

def get_iso_code(row):
    if pycountry.countries.get(name=row[c.ENTITY]):
        return pycountry.countries.get(name=row[c.ENTITY]).alpha_3
    elif row[c.ENTITY] == 'Bosnia-Herzegovina':
        return 'BIH'
    elif row[c.ENTITY] == 'Czech Republic':
        return 'CZE'
    elif row[c.ENTITY] == 'Moldova':
        return 'MDA'
    elif row[c.ENTITY] == 'Serbia & Montenegro':
        return 'SRB'
    else:
        return 'N/A'

def get_season(row):
    if row[c.WEEK] in range(10, 22):
        return 'Spring'
    elif row[c.WEEK] in range(22, 36):
        return 'Summer'
    elif row[c.WEEK] in range(36, 48):
        return 'Autumn'
    else:
        return 'Winter'


states = pd.read_excel('datasets/States.xlsx', sheet_name='Data')
states_2020 = pd.read_excel('datasets/2020-States.xlsx', sheet_name='Data')
states_2022 = pd.read_excel('datasets/2022-States.xlsx', sheet_name='Data')

states_2022 = states_2022[
    states_2022[c.DAY].gt(pd.to_datetime(datetime.datetime(2021, 12, 24)))
]

states = pd.concat([states_2022, states, states_2020])
states = states.rename(
    columns={
        c.DAY: c.DATE
    }
)

states[c.ISO] = states.apply(lambda x: get_iso_code(x), axis=1)


def filter_states_traffic_variability(data, start_date=None, end_date=None, states=None):
    """
    Filters states data for traffic variability graph
    If states is None or [] then it takes Total Netwok Area
    instead of all states
    """
    filtered_data = u.filter_dataset_by_date(
        data=data, start_date=start_date, end_date=end_date
    )

    if states is None or states == []:
        filtered_data = filtered_data[
            filtered_data[c.ENTITY].eq(c.TOT_NETWORK_AREA)
        ]
    else:
        filtered_data = filtered_data[
            filtered_data[c.ENTITY].isin(states)
        ]
    
    return filtered_data


def filter_states_data(data, start_date=None, end_date=None, states=None):
    """
    Filters states data based on a set of parameters
    """
    filtered_data = u.filter_dataset_by_date(
        data=data, start_date=start_date, end_date=end_date
    )

    if states:
        filtered_data = filtered_data[
            filtered_data[c.ENTITY].isin(states)
        ]
    return filtered_data



def get_states_flight_data(data, index):
    """
    Returns a dataframe suitable to use for map choropleth chart or bar chart
    Groups data by country and calculates daily average number of flights
    """
    pivot = pd.pivot_table(
        data,
        values=c.FLIGHTS,
        index=index,
        aggfunc=np.mean
    )
    pivot = pivot.reset_index()
    return pivot


def get_top_ten_states(data):
    """
    Return a dataframe with a list of top ten countries with higher
    levels of traffic
    """
    states_flight_data = pd.pivot_table(
        data,
        values=c.FLIGHTS,
        index=c.ENTITY,
        aggfunc=np.mean
    )
    states_flight_data = states_flight_data.reset_index()
    states_flight_data = states_flight_data[
        states_flight_data[c.ENTITY].ne(c.TOT_NETWORK_AREA)
    ]
    states_flight_data = states_flight_data.sort_values(by=c.FLIGHTS, ascending=False)
    return states_flight_data.head(10)


def get_traffic_variations(data):
    
    # if year == 2021:
    #    columns = [c.DATE, c.FLIGHTS]
    # elif year == 2020:
    #    columns = [c.DATE_2020, c.FLIGHT_2020]
    # else:
    #     columns = [c.DATE_2019, c.FLIGHTS_2019]

    traffic_variations = pd.pivot_table(
        data,
        values=[c.MA, c.FLIGHTS, c.FLIGHTS_2019, c.FLIGHTS_2020],
        index=c.DATE,
        aggfunc=np.sum
    )
    traffic_variations = traffic_variations.reset_index()
    traffic_variations[c.MA_2019] = traffic_variations[c.FLIGHTS_2019].rolling(7, min_periods=1).mean()
    return traffic_variations


def get_weekly_variations(data):
    
    weekly_variations = data.copy(deep=True)
    weekly_variations[c.YEAR] = weekly_variations[c.DATE].dt.year
    weekly_variations[c.SEASON] = weekly_variations.apply(lambda x: get_season(x), axis=1)
    
    pivot_variations = pd.pivot_table(
        weekly_variations,
        values=[c.MA, c.FLIGHTS, c.VARIATION_2019],
        index=[c.WEEK, c.SEASON],
        aggfunc=np.mean
    )
    pivot_variations = pivot_variations.reset_index()
    return pivot_variations
    
    