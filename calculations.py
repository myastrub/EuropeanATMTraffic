import pandas as pd
import numpy as np
import constants as c
import pycountry

# ----- Filtering functions ------- #


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


def filter_aircraft_operators(data, start_date=None, end_date=None, operators=None):

    filtered_data = filter_dataset_by_date(
        data=data, start_date=start_date, end_date=end_date
    )

    if operators:
        filtered_data = filtered_data[
            filtered_data[c.ENTITY].isin(operators)
        ]
    
    return filtered_data



def filter_states_traffic_variability(data, start_date=None, end_date=None, states=None):
    """
    Filters states data for traffic variability graph
    If states is None or [] then it takes Total Netwok Area
    instead of all states
    """
    filtered_data = filter_dataset_by_date(
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
    filtered_data = filter_dataset_by_date(
        data=data, start_date=start_date, end_date=end_date
    )

    if states:
        filtered_data = filtered_data[
            filtered_data[c.ENTITY].isin(states)
        ]
    return filtered_data


def filter_area_center_data(data, states=None, area_centers=None, start_date=None, end_date=None):
    """
    Filters acc centers data based on a set of parameters
    """
    filtered_data = filter_dataset_by_date(
        data=data, start_date=start_date, end_date=end_date
    )

    if states and area_centers:
        filtered_data = filtered_data[
            filtered_data[c.ACC].isin(area_centers) &
            filtered_data[c.STATE_NAME].isin(states)
        ]
    elif states and not area_centers:
        filtered_data = filtered_data[
            filtered_data[c.STATE_NAME].isin(states)
        ]
    elif not states and area_centers:
        filtered_data = filtered_data[
            filtered_data[c.ACC].isin(area_centers)
        ]
    return filtered_data


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


def filter_airport_dataset(data, airports=None, states=None, start_date=None, end_date=None):
    """
    Filters dataset based on the specified filters.
    """
    filtered_dataset = filter_dataset_by_date(
        data, start_date, end_date
    )

    if airports and states:
        filtered_dataset = filtered_dataset[
            filtered_dataset[c.AIRPORT_NAME].isin(airports) &
            filtered_dataset[c.STATE_NAME].isin(states)
        ]
    elif (airports is None or airports == []) and states:
        filtered_dataset = filtered_dataset[
            filtered_dataset[c.STATE_NAME].isin(states)
        ]
    elif (states is None or states == []) and airports:
        filtered_dataset = filtered_dataset[
            filtered_dataset[c.AIRPORT_NAME].isin(airports)
        ]
    return filtered_dataset


# ----- Functions for calculations ----- #


def get_states_flight_data(data, index):
    """
    Returns a dataframe suitable to use for map choropleth chart or bar chart
    Groups data by country and calculates daily average number of flights
    """
    pivot = pd.pivot_table(
        data,
        values=[c.FLIGHTS, c.FLIGHTS_2019],
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


def get_top_ten_aircraft_operators(data):
    """
    Return a dataframe with a list of top ten aircraft operators with higher
    levels of traffic
    """
    ao_flight_data = pd.pivot_table(
        data,
        values=c.FLIGHTS,
        index=c.ENTITY,
        aggfunc=np.mean
    )
    ao_flight_data = ao_flight_data.reset_index()
    
    ao_flight_data = ao_flight_data.sort_values(by=c.FLIGHTS, ascending=False)
    return ao_flight_data.head(10)



def get_area_centers_data(data, fields):
    """
    Return a dataframe with a list of area centers corresponding
    flight levels
    """
    area_center_flight_data = pd.pivot_table(
        data,
        values=fields,
        index=[c.STATE_NAME, c.ACC],
        aggfunc=np.mean
    )
    area_center_flight_data = area_center_flight_data.reset_index()
    area_center_flight_data = area_center_flight_data.sort_values(by=c.FLIGHTS, ascending=False)
    return area_center_flight_data


def get_flight_column(ifr_movements):
    """
    Based on the selected IFR movement returns a string with
    column where the values are stored.
    """
    if len(ifr_movements) == 2 or len(ifr_movements) == 0:
        return c.NM_TOTAL_FLIGHTS
    elif ifr_movements[0] == 'Arrival':
        return c.NM_ARR_FLIGHTS
    elif ifr_movements[0] == 'Departure':
        return c.NM_DEP_FLIGHTS
    else:
        return c.NM_TOTAL_FLIGHTS

def get_flight_columns(ifr_movements):
    """
    Based on the selected IFR movement returns a string with
    column where the values are stored.
    """
    if len(ifr_movements) == 2 or len(ifr_movements) == 0:
        return [c.NM_TOTAL_FLIGHTS, c.AIRPORT_TOTAL_FLIGHTS]
    elif ifr_movements[0] == 'Arrival':
        return [c.NM_ARR_FLIGHTS, c.AIRPORT_ARR_FLIGHTS]
    elif ifr_movements[0] == 'Departure':
        return [c.NM_DEP_FLIGHTS, c.AIRPORT_DEP_FLIGHTS]
    else:
        return [c.NM_TOTAL_FLIGHTS, c.AIRPORT_TOTAL_FLIGHTS]


def has_airport_data(data):
    """
    Checks if a dataset has values reported by Airport
    """
    if (c.AIRPORT_DEP_FLIGHTS in data.columns or
        c.AIRPORT_ARR_FLIGHTS in data.columns or
        c.AIRPORT_TOTAL_FLIGHTS in data.columns):
        return True
    else:
        return False



def get_number_of_flights(data, flight_columns):
    """
    Takes a dataset and flight column (arrival, departure or total)
    and returns dataframe with dates of flights and a number of flights
    according to NM
    """

    pivot = pd.pivot_table(
        data, values=flight_columns, index=c.DATE,
        aggfunc=np.sum
    )
    pivot = pivot.reset_index()
    pivot[c.NM_MA] = pivot[flight_columns[0]].rolling(7, min_periods=1).mean()
    pivot[c.APT_MA] = pivot[flight_columns[1]].rolling(7, min_periods=1).mean()
    return pivot


def get_top_flight_airports(data, flight_column):
    """
    Returns top 10 airports with daily average flights
    """
    
    pivot = pd.pivot_table(
        data, values=flight_column, index=c.AIRPORT_NAME,
        aggfunc=np.mean
    )
    if not pivot.empty:
        pivot = pivot.reset_index()
        pivot = pivot.sort_values(by=flight_column, ascending=False)
        return pivot.head(10)
    else:
        return pd.DataFrame(columns=[c.AIRPORT_NAME, flight_column])


def get_daily_average_per_state(data, flight_columns):
    """
    Takes a dataset and flight columns (arrival, departure or total)
    and returns dataframe with states and a number of daily flights
    according to NM and airport
    """
    if has_airport_data(data):
        pivot = pd.pivot_table(
            data, values=flight_columns, index=c.STATE_NAME,
            aggfunc=np.sum
        )
    else:
        pivot = pd.pivot_table(
            data, values=flight_columns[0], index=c.STATE_NAME,
            aggfunc=np.sum
        )
    pivot = pivot.reset_index()
    pivot = pivot.sort_values(by=c.STATE_NAME)
    return pivot


def get_daily_average_per_airport(data, flight_column):
    """
    Takes a dataset and returns a dataframe with airports
    and a number of daily flights according to NM
    Resulting dataframe is merged with geojson to get
    coordinates of airports
    """
    pivot = pd.pivot_table(
        data, values=flight_column, index=[c.AIRPORT_CODE, c.AIRPORT_NAME, c.ISO],
        aggfunc=np.mean
    )
    
    pivot = pivot.join(
      airport_coordinates.set_index(c.AIRPORT_CODE),
      on=c.AIRPORT_CODE,
      how='left'
    )
    pivot = pivot.reset_index()
    return pivot


def get_average_per_year(data, flight_columns):
    """
    Takes a dataset and flight columns (arrival, departure or total)
    and returns dataframe with years and a number of daily flights
    according to NM and airport
    """
    pivot = pd.pivot_table(
        data, values=flight_columns, index=[c.YEAR],
        aggfunc=np.mean
    )
    pivot = pivot.sort_values(by=c.YEAR)
    pivot=pivot.reset_index()
    return pivot


def get_average_per_month(data, flight_columns):
    """
    Takes a dataset and flight columns (arrival, departure or total)
    and returns dataframe with months and a number of daily flights
    according to NM and airport
    """
    pivot = pd.pivot_table(
        data, values=flight_columns, index=[c.MONTH_MON, c.MONTH_NUM],
        aggfunc=np.mean
    )
    pivot = pivot.sort_values(by=c.MONTH_NUM)
    pivot = pivot.reset_index()
    return pivot


def get_list_of_states(data):
    """
    Returns a list of states from the dataset
    """
    return data[c.STATE_NAME].unique()


def get_list_of_airports(data):
    """
    Returns a list of states from the dataset
    """
    return data[c.AIRPORT_NAME].unique()


def get_iso_code(row, field):
    if pycountry.countries.get(name=row[field]):
        return pycountry.countries.get(name=row[field]).alpha_3
    elif row[field] == 'Bosnia-Herzegovina':
        return 'BIH'
    elif row[field] == 'Czech Republic':
        return 'CZE'
    elif row[field] == 'Moldova':
        return 'MDA'
    elif row[field] == 'Serbia & Montenegro':
        return 'SRB'
    elif row[field] == 'Republic of North Macedonia':
        return 'MKD'
    else:
        return 'N/A'

def get_unique_values(data, field):
    """
    Returns a list of unique values of a field from the dataset
    """
    return sorted(list(data[field].unique()))


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



# ---- Upload of additional dataset to get airport coordinates ----- #

airport_coordinates = pd.read_csv(
    'datasets/airport_coordinates.csv',
    delimiter=';',
    decimal=','
)
airport_coordinates = airport_coordinates.drop(labels=c.AIRPORT_NAME, axis=1)