import pandas as pd
import numpy as np
import constants as c
import datetime

area_centers = pd.read_excel('datasets/ACCs.xlsx', sheet_name='Data')
area_centers_2020 = pd.read_excel('datasets/2020-ACCs.xlsx', sheet_name='Data')
area_centers_2022 = pd.read_excel('datasets/2022-ACCs.xlsx', sheet_name='Data')

area_centers_2022 = area_centers_2022[
    area_centers_2022[c.DAY].gt(pd.to_datetime(datetime.datetime(2021, 12, 24)))
]

area_centers = pd.concat([area_centers_2022, area_centers, area_centers_2020])

area_centers = area_centers.rename(
    columns={
        c.DAY: c.DATE
    }
)
