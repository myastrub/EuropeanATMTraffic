from copy import deepcopy
import pandas as pd
import numpy as np
import constants as c
import datetime


def rename_state_names(dataset, field):
    data = dataset.copy(deep=True)

    data[field] = data[field].str.replace(
        'Bosnia-Herzegovina',
        'Bosnia and Herzegovina',
        regex=False
    )
    data[field] = data[field].str.replace(
        'Serbia & Montenegro',
        'Serbia',
        regex=False
    )
    data[field] =data[field].str.replace(
        'North Macedonia',
        'Republic of North Macedonia',
        regex=False
    )
    return data


def get_combined_datasets(dataset_name, cutoff_date):
    datasets = []
    years = ['2020', '2021', '2022']
    for year in years:
        dataset = pd.read_csv(
            'datasets/{}-{}.csv'.format(year, dataset_name),
            delimiter=';',
            decimal=',',
            dtype={
                c.MA: np.float32
            }
        )
        dataset[c.DAY] = pd.to_datetime(dataset[c.DAY], format='%Y-%m-%d')
        dataset[c.DATE_2019] = pd.to_datetime(dataset[c.DATE_2019], format='%Y-%m-%d')
        if year == '2022':
            dataset = dataset[
                dataset[c.DAY].gt(
                    pd.to_datetime(cutoff_date)
                )
            ]
        datasets.append(dataset)
    return pd.concat(datasets)


def upload_states_data():
    states = get_combined_datasets('States', datetime.datetime(2021, 12, 24))

    states = states.rename(
        columns={
            c.DAY: c.DATE
        }
    )
    states = rename_state_names(states, c.ENTITY)

    states = states.set_index(c.ENTITY).join(
        iso_codes.set_index(c.STATE_NAME),
        on=c.ENTITY,
        how='left'
    )
    states = states.reset_index()
    return states


def upload_area_centers_data():
    area_centers = get_combined_datasets('ACCs', datetime.datetime(2021, 12, 24))

    area_centers = area_centers.rename(
        columns={
            c.DAY: c.DATE,
            c.ENTITY: c.ACC,
            'State': c.STATE_NAME
        }
    )
    area_centers = rename_state_names(area_centers, c.STATE_NAME)
    return area_centers


def upload_airports_data():
    airports = pd.read_csv(
        'datasets/Airport_Traffic.csv',
        delimiter=';',
        usecols=[
            c.YEAR, c.MONTH_NUM, c.MONTH_MON,
            c.DATE, c.AIRPORT_CODE, c.AIRPORT_NAME,
            c.STATE_NAME, c.NM_DEP_FLIGHTS, c.NM_ARR_FLIGHTS,
            c.NM_TOTAL_FLIGHTS, c.AIRPORT_DEP_FLIGHTS,
            c.AIRPORT_ARR_FLIGHTS, c.AIRPORT_TOTAL_FLIGHTS
        ],
        dtype={
            c.YEAR: np.int32,
            c.MONTH_NUM: np.int32,
            c.NM_DEP_FLIGHTS: np.float32,
            c.NM_ARR_FLIGHTS: np.float32,
            c.NM_TOTAL_FLIGHTS: np.float32,
            c.AIRPORT_TOTAL_FLIGHTS: np.float32,
            c.AIRPORT_ARR_FLIGHTS: np.float32,
            c.AIRPORT_DEP_FLIGHTS: np.float32,
        }
    )

    airports[c.DATE] = pd.to_datetime(airports[c.DATE], format='%d/%m/%Y')

    airports = airports.set_index(c.STATE_NAME).join(
        iso_codes.set_index(c.STATE_NAME),
        on=c.STATE_NAME,
        how='left'
    )
    airports = airports.reset_index()
    return airports


def upload_aircraft_operators_data():

    aircraft_operators = get_combined_datasets(
        'Aircraft_Operators',
        datetime.datetime(2021, 12, 31)
    )

    aircraft_operators = aircraft_operators.rename(
        columns={
            c.DAY: c.DATE
        }
    )
    names_to_update = [
        'Ryanair', 'easyJet', 'KLM', 'Wizz Air',
        'SAS', 'SWISS', 'TAP', 'Aer Lingus',
        'Air France', 'Eurowings', 'Iberia',
        'British Airways'
        ]
    for name in names_to_update:
        aircraft_operators[c.ENTITY] = aircraft_operators[c.ENTITY].str.replace(
            '{}$'.format(name), '{} Group'.format(name), regex=True
        )    
    aircraft_operators[c.ENTITY] = aircraft_operators[c.ENTITY].str.replace(
        'Lufthansa$', 'Lufthansa Airlines', regex=True
    )
    aircraft_operators[c.ENTITY] = aircraft_operators[c.ENTITY].str.replace(
        'DHL Express', 'DHL Group', regex=True
    )
    aircraft_operators[c.ENTITY] = aircraft_operators[c.ENTITY].str.replace(
        'Aegean Airlines', 'AEGEAN Group', regex=True
    )

    
    return aircraft_operators


def get_aircraft_operators_2019_data(aircraft_operators):
    aircraft_operators_2021 = aircraft_operators[
        aircraft_operators[c.DATE].dt.year.eq(2021)
    ]
    aircraft_operators_2019 = aircraft_operators_2021[[c.ENTITY, c.DATE_2019, c.FLIGHTS_2019]]
    aircraft_operators_2019 = aircraft_operators_2019[
        aircraft_operators_2019[c.DATE_2019].dt.year.eq(2019)
    ]
    aircraft_operators_2019 = aircraft_operators_2019.rename(
        columns={
            c.DATE_2019: c.DATE,
            c.FLIGHTS_2019: c.FLIGHTS
        }
    )
    return aircraft_operators_2019


iso_codes = pd.read_csv('datasets/iso_codes.csv', delimiter=';')

states = upload_states_data()
area_centers = upload_area_centers_data()
airports = upload_airports_data()
aircraft_operators = upload_aircraft_operators_data()
aircraft_operators_2019 = get_aircraft_operators_2019_data(aircraft_operators)