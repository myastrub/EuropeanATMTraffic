import pandas as pd
import constants as c
import datetime
import calculations

def get_combined_datasets(dataset_name, cutoff_date):
    datasets = []
    years = ['2020', '2021', '2022']
    for year in years:
        dataset = pd.read_csv('datasets/{}-{}.csv'.format(year, dataset_name), delimiter=';')
        dataset[c.DAY] = pd.to_datetime(dataset[c.DAY], format='%Y-%m-%d')
        dataset[c.MA] = dataset[c.MA].str.replace(',', '.')
        dataset[c.MA] = dataset[c.MA].astype(float)
        if year == '2022':
            dataset = dataset[
                dataset[c.DAY].gt(
                    pd.to_datetime(cutoff_date)
                )
            ]
        datasets.append(dataset)
    
    return pd.concat(datasets)

# Upload of the ACC data
area_centers = get_combined_datasets('ACCs', datetime.datetime(2021, 12, 24))

area_centers = area_centers.rename(
    columns={
        c.DAY: c.DATE,
        c.ENTITY: c.ACC,
        'State': c.STATE_NAME
    }
)

# Upload af States data
states = get_combined_datasets('States', datetime.datetime(2021, 12, 24))

states = states.rename(
    columns={
        c.DAY: c.DATE
    }
)

states[c.ISO] = states.apply(lambda x: calculations.get_iso_code(x, c.ENTITY), axis=1)

# Upload of airport data

airports = pd.read_csv('datasets/Airport_Traffic.csv', delimiter=';')
airports[c.DATE] = pd.to_datetime(airports[c.DATE], format='%d/%m/%Y')
airports[c.ISO] = airports.apply(lambda x: calculations.get_iso_code(x, c.STATE_NAME), axis=1)

# upload of airport_operator data

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