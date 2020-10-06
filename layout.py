import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from datetime import datetime, timedelta
import math


now = datetime.now()
year = now.year
now_minus_90 = now - timedelta(90)
previous_quarter = f'{now.year}-Q{math.ceil(now_minus_90.month/3)}'
this_quarter = f'{now.year}-Q{math.ceil(now.month/3)}'


time_periods = [
    f'{year - 1}-Annual',
    f'{year}-Q1',
    f'{year}-Q2',
    f'{year}-Half-Yearly',
    f'{year}-Q3',
    f'{year}-Q4',
    f'{year}-Annual'
]

period_dict = {
    f'{year - 1}-Annual': (f'01-01-{year-1}', f'12-31-{year-1}'),
    f'{year}-Q1': (f'01-01-{year}', f'03-31-{year}'),
    f'{year}-Q2': (f'04-01-{year}', f'06-30-{year}'),
    f'{year}-Q3': (f'07-01-{year}', f'09-30-{year}'),
    f'{year}-Q4': (f'10-01-{year}', f'12-31-{year}'),
    f'{year}-Half-Yearly': (f'01-01-{year}', f'06-30-{year}'),
    f'{year}-Annual': (f'01-01-{year}', f'12-31-{year}')
}


def create_danger_alert(message, dismissable=False):
    return dbc.Alert(message, color="danger", dismissable=dismissable)


alert = dbc.Alert("No metrics data XLSX. Please contact EQA Support",
                  color="danger",
                  dismissable=False)


select_quarter = dbc.FormGroup(
    [
        dbc.Label("Select Timeperiod"),
        dcc.Dropdown(
            id="quarter-selector",
            options=[
                {"label": t, "value": t}
                for t in time_periods
            ],
            value=this_quarter,
        ),
    ]
)


select_dropdown_card = dbc.Card(
    [
        dbc.CardBody(
            [
                html.Div(id="the_alert", children=[],
                         style={
                            'margin-bottom': '10px'
                }),
                select_quarter,
                html.Hr(),
            ]
        ),
    ],
    color="light",
)

layout = dbc.Container(
    [
        html.H1("EQA Automation-Team Dashboard",
                style={
                    'textAlign': 'center',
                    'color': '#ad5555'
                }),
        html.Hr(),

        dbc.Row(
            [
                dbc.Col(select_dropdown_card, md=6,
                        width={"size": 6, "offset": 3})
            ],
        ),
        dbc.Row(
            [
                dbc.Col(dcc.Graph(id="list_of_projects"), md=12),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(dcc.Graph(id="all_proj_hours"), md=12),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(dcc.Graph(id="type_pie"), md=6),
                dbc.Col(dcc.Graph(id="num_proj_bar"), md=6),
            ]
        ),
        html.Hr(),
        html.H2("Number Of Scripts Developed",
                style={
                    'textAlign': 'center',
                    'color': '#ad5555'
                }),
        dbc.Row(
            [
                dbc.Col(dcc.Graph(id="num_of_scripts"), md=12),
            ]
        ),
        dbc.Row(
            [
                dbc.Col(dcc.Graph(id="script_count_table"), md=6)
            ],
            justify="center",
        ),
    ],
    fluid=True,
)
