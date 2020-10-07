import pandas as pd
from pathlib import Path
from functools import reduce


def isTrueMetrics(metrics_file_path):
    MANDATORY_SHEETS = ['Hours', 'Scripts', 'Comments']
    df = pd.read_excel(metrics_file_path, None)

    if sorted(MANDATORY_SHEETS) != sorted(df.keys()):
        return False

    df_sheet = pd.read_excel(metrics_file_path, sheet_name='Hours')
    for col in ['Date', 'Day', 'Hours']:
        if not (col in df_sheet):
            return False

    df_sheet = pd.read_excel(metrics_file_path, sheet_name='Scripts')
    for col in ['Date', 'Day']:
        if not (col in df_sheet):
            return False

    return True


def get_files():

    # The individual xlsx files are placed in the path >>
    # current_directory/data/metrics
    # Change the path of the files as needed
    METRICS_DATA_DIR = Path.joinpath(Path.cwd(), 'data/metrics/')

    # Reading all the xlsx files
    # omitting any opened files, which will have the '~$' suffix
    files_xlsx = [f for f in METRICS_DATA_DIR.iterdir()
                  if ((f.is_file()) & (f.suffix == '.xlsx') & (f.stem[:2] != '~$'))
                  ]
    files_xlsx = list(filter(lambda f: isTrueMetrics(f), files_xlsx))
    return files_xlsx


def get_file_count():
    return len(get_files())


def get_df_total_hours(start_date, end_date):
    # Creating a list of dataframes of individual team members
    # This is being done, just in case if we want to do
    # an individual's progress, trends or throughput analysis
    df_persons = {}
    for f in get_files():
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
        del df_person

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
# -----------------------------------------------------------
# Block to get number of scripts DataFrame
# -----------------------------------------------------------


def get_df_total_scripts(start_date, end_date):
    df_persons_scripts = {}
    for f in get_files():
        person_name = f.stem[:f.stem.index('_')]
        df_person = pd.read_excel(f, index_col='Date', sheet_name='Scripts')
        df_person = df_person.loc[start_date:end_date]
        df_person.drop(['Day'], axis=1, inplace=True)
        float_cols = df_person.select_dtypes(include=['float64']).columns
        str_cols = df_person.select_dtypes(include=['object']).columns
        df_person.loc[:,
                      float_cols] = df_person.loc[:, float_cols].fillna(0)
        df_person.loc[:,
                      str_cols] = df_person.loc[:, str_cols].fillna('')

        df_persons_scripts[person_name] = df_person
        del df_person

    # Combinaing all XLSX df into 1 and summing the project hours
    df_scripts_series = reduce(lambda x, y: x.add(y, fill_value=0),
                               [df for df in df_persons_scripts.values()])

    df_total = pd.DataFrame(
        {
            'Projects': pd.Series(df_scripts_series.sum().index),
            'Scripts': pd.Series(df_scripts_series.sum().values)
        }
    )

    df_total = df_total[df_total['Scripts'] > 0]

    return df_total
