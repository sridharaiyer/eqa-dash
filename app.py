import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
from dash.dependencies import Input, Output
import plotly.express as px
from dataframe import get_df_total_hours, METRICS_FILES_COUNT
from datetime import datetime, timedelta
from flask import Flask
import math

# csvpath = Path(__file__).parent.absolute()/'data'/'palmer-penguins.csv'

server = Flask(__name__)
app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP], server=server)
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

app.layout = dbc.Container(
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
    ],
    fluid=True,
)


@ app.callback(
    [Output("the_alert", "children"),
     Output("list_of_projects", "figure"),
     Output("all_proj_hours", "figure"),
     Output("type_pie", "figure"),
     Output("num_proj_bar", "figure")],
    [Input("quarter-selector", "value")]
)
def update_graphs(quarter):
    if METRICS_FILES_COUNT < 1:
        alert_msg = "No metrics data XLSX. Please contact EQA Support"
        return (create_danger_alert(alert_msg),
                dash.no_update,
                dash.no_update,
                dash.no_update,
                dash.no_update)
    else:
        start_date = period_dict[quarter][0]
        end_date = period_dict[quarter][1]
        df_total_hours = get_df_total_hours(start_date, end_date)

        if len(df_total_hours) == 0:
            alert_msg = f'No data found for period {start_date} to {end_date}'
            return (create_danger_alert(alert_msg, dismissable=True),
                    dash.no_update,
                    dash.no_update,
                    dash.no_update,
                    dash.no_update)

        # -----------------------------------------------------------
        # fig1 - Total hours for each Project
        # -----------------------------------------------------------

        fig1 = px.bar(df_total_hours, x='Projects', y='Hours')
        fig1.update_layout(
            title=f"Total Hours Per Project from {start_date} to {end_date}",
            height=800,
            xaxis={'title_text': '',
                   'tickangle': 90
                   }
        )
        fig1.update_xaxes(automargin=True)

        # --------------------------------------------------------------------------------
        # Adding 'Type' to the df_total_hours
        # --------------------------------------------------------------------------------
        df_total_hours['Type'] = df_total_hours['Projects'].str.replace(
            '-', ' ').str.split(n=1, expand=True)[0]
        df_total_hours['Projects'] = df_total_hours['Projects'].str.split(
            '-', n=1).str[1].str.strip()

        # ----------------------------------------------------------
        # Get hours and count for each type of project
        # ----------------------------------------------------------
        df_projtype = (df_total_hours.groupby('Type')['Hours']
                       .agg(Hours='sum', Count='count')
                       .reset_index()
                       ).set_index('Type')

        # ---------------------------------------------------------
        # Project type hours pie
        # ---------------------------------------------------------
        fig2 = px.pie(df_projtype,
                      values='Hours',
                      names=df_projtype.index,
                      title=f'Hours spent by Project Type from {start_date} to {end_date}')
        fig2.update_traces(textposition='inside',
                           textinfo='value+label', automargin=True)

        # ---------------------------------------------------------
        # Project type hours count bar
        # ---------------------------------------------------------

        fig3 = px.bar(df_projtype, y="Count", text=df_projtype.index)
        fig3.update_layout(
            title=f"Number of Project Types from {start_date} to {end_date}",
            autosize=True,
            xaxis={
                'showticklabels': False
            },
            margin={
                #         'l':50,
                #         'r':50,
                #         'b':100,
                't': 100,
                #         'pad':4
            }
        )

        fig3.update_traces(textposition='inside')
        fig3.update_xaxes(automargin=True)

        # ---------------------------------------------------------
        # List of Projects
        # ---------------------------------------------------------
        import plotly.graph_objects as go

        core_df = df_total_hours[(df_total_hours['Type'] == 'Core')]['Projects']
        mobile_df = df_total_hours[(df_total_hours['Type'] == 'Mobile')]['Projects']
        poc_df = df_total_hours[(df_total_hours['Type'] == 'POC')]['Projects']

        fig4 = go.Figure(data=[go.Table(
            header=dict(values=list(['Core Projects', 'Mobile Projects', 'POCs']),
                        fill_color='paleturquoise',
                        align='left',
                        font_size=18,
                        height=38
                        ),
            cells=dict(values=[core_df, mobile_df, poc_df],
                       fill_color='lavender',
                       align='left',
                       font_size=14,
                       height=35
                       )
        )
        ])

        fig4.update_layout(
            autosize=True,
            height=(max([len(core_df), len(mobile_df), len(poc_df), 8])/2)*100,
        )

        return dash.no_update, fig4, fig1, fig2, fig3


if __name__ == "__main__":
    app.run_server()
