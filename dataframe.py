import numpy as np
from collections import Counter
import pandas as pd
import os
from pathlib import Path
from datetime import datetime
from functools import reduce

# The individual xlsx files are placed in the path >> current_directory/data/metrics
# Change the path of the files as needed


metrics_dir = Path.joinpath(Path.cwd(),'data/metrics/')

# Reading all the xlsx files omitting any opened files, which will have the '~$' suffix
files_xlsx = [f for f in metrics_dir.iterdir() if (f.suffix == '.xlsx') & (f.stem[:2] != '~$')]

# Creating a list of dataframes of individual team members
# This is being done, just in case if we want to do an individual's progress, trends or throughput analysis
df_hours_list = []

def get_df_total_hours(start_date, end_date):
    for f in files_xlsx:
        person_name = f.stem[:f.stem.index('_')]
        df_person_hours_variable = f'df_{person_name}_hours'
        exec("{}=pd.read_excel(f, index_col='Date', sheet_name='Hours')".format(df_person_hours_variable))

        # Reading the time series just for Q2 of 2020.
        # This time series slicing will be made dynamic in the "Metrics App",
        # based on user's dropdown selection of the particular timeline.
        # exec(f"{df_person_hours_variable} = {df_person_hours_variable}['2020-04-01':'2020-06-30']")
        exec(f"{df_person_hours_variable} = {df_person_hours_variable}[\'{start_date}\':\'{end_date}']")

        # Dropping the Day and Hours column as these calculations can be done by Pandas itself.
        # The Day and Hours were included in the XLSX just to aid people to do data entry.
        exec(f"{df_person_hours_variable}.drop(['Day'], axis=1, inplace=True)")
        exec(f"{df_person_hours_variable}.drop(['Hours'], axis=1, inplace=True)")

        # Selecting the String and Numeric columns in order to fill them with blanks or zeroes
        # Ideally, there should not be any String columns in the 'Hours' sheet.
        exec(f"float_cols = {df_person_hours_variable}.select_dtypes(include=['float64']).columns")
        exec(f"str_cols = {df_person_hours_variable}.select_dtypes(include=['object']).columns")

        exec(f"{df_person_hours_variable}.loc[:, float_cols] = {df_person_hours_variable}.loc[:, float_cols].fillna(0)")
        exec(f"{df_person_hours_variable}.loc[:, str_cols] = {df_person_hours_variable}.loc[:, str_cols].fillna('')")

        exec(f"df_hours_list.append({df_person_hours_variable})")

    # Combinaing all the individual team member's dataframe into 1 and summing the project hours
    df_hours_timeseries = reduce(lambda x, y: x.add(y, fill_value=0), df_hours_list)

    return pd.DataFrame(
        {
            'Projects':pd.Series(df_hours_timeseries.sum().index),
            'Hours':pd.Series(df_hours_timeseries.sum().values)
        }
                ).set_index('Projects')
