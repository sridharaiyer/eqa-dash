import pandas as pd
from pathlib import Path
from functools import reduce

# The individual xlsx files are placed in the path >>
# current_directory/data/metrics
# Change the path of the files as needed
metrics_dir = Path.joinpath(Path().absolute(), 'data/metrics/')

# Reading all the xlsx files
# omitting any opened files, which will have the '~$' suffix
files_xlsx = [f for f in metrics_dir.iterdir()
              if (f.suffix == '.xlsx') & (f.stem[:2] != '~$')]

# Creating a list of dataframes of individual team members
# This is being done, just in case if we want to do an individual's progress,
# trends or throughput analysis
df_persons = {}


def get_df_total_hours(start_date, end_date):
    for f in files_xlsx:
        person_name = f.stem[:f.stem.index('_')]
        df_person = pd.read_excel(f, index_col='Date', sheet_name='Hours')
        df_person = df_person.loc[start_date:end_date]
        df_person.drop(['Day'], axis=1, inplace=True)
        df_person.drop(['Hours'], axis=1, inplace=True)
        float_cols = df_person.select_dtypes(include=['float64']).columns
        str_cols = df_person.select_dtypes(include=['object']).columns
        df_person.loc[:,
                      float_cols] = df_person.loc[:, float_cols].fillna(0)
        df_person.loc[:,
                      str_cols] = df_person.loc[:, str_cols].fillna('')

        df_persons[person_name] = df_person

    # Combinaing all XLSX df into 1 and summing the project hours
    df_hours_series = reduce(lambda x, y: x.add(y, fill_value=0),
                             [df for df in df_persons.values()])

    df_total = pd.DataFrame(
        {
            'Projects': pd.Series(df_hours_series.sum().index),
            'Hours': pd.Series(df_hours_series.sum().values)
        }
    )

    df_total = df_total[df_total['Hours'] > 0]

    return df_total
