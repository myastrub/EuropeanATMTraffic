import pandas as pd
import numpy as np
import constants as c
import datetime
import utility as u

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

def filter_area_center_data(data, states=None, area_centers=None, start_date=None, end_date=None):
    """
    Filters acc centers data based on a set of parameters
    """
    filtered_data = u.filter_dataset_by_date(
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


def get_area_centers_data(data):
    """
    Return a dataframe with a list of area centers corresponding
    flight levels
    """
    area_center_flight_data = pd.pivot_table(
        data,
        values=c.FLIGHTS,
        index=[c.STATE_NAME, c.ACC],
        aggfunc=np.mean
    )
    area_center_flight_data = area_center_flight_data.reset_index()
    area_center_flight_data = area_center_flight_data.sort_values(by=c.FLIGHTS, ascending=False)
    return area_center_flight_data
