import pandas as pd
import constants as c
import datetime
import utility as u

# Upload of the ACC data
# TODO: replace Excel with CSV to speed up loading time
area_centers = pd.read_excel('datasets/ACCs.xlsx', sheet_name='Data')
area_centers_2020 = pd.read_excel('datasets/2020-ACCs.xlsx', sheet_name='Data')
area_centers_2022 = pd.read_excel('datasets/2022-ACCs.xlsx', sheet_name='Data')

area_centers_2022 = area_centers_2022[
    area_centers_2022[c.DAY].gt(pd.to_datetime(datetime.datetime(2021, 12, 24)))
]

area_centers = pd.concat([area_centers_2022, area_centers, area_centers_2020])

area_centers = area_centers.rename(
    columns={
        c.DAY: c.DATE,
        c.ENTITY: c.ACC,
        'State': c.STATE_NAME
    }
)

# Upload af States data
# TODO: replace Excel with CSV to speed up loading time
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

states[c.ISO] = states.apply(lambda x: u.get_iso_code(x, c.ENTITY), axis=1)

# Upload of airport data

airports = pd.read_csv('datasets/Airport_Traffic.csv', delimiter=';')
airports[c.DATE] = pd.to_datetime(airports[c.DATE], format='%d/%m/%Y')
airports[c.ISO] = airports.apply(lambda x: u.get_iso_code(x, c.STATE_NAME), axis=1)