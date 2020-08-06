import dash
import dash_bootstrap_components as dbc
import dash_core_components as dcc
import dash_html_components as html
import pandas as pd
from dash.dependencies import Input, Output
import plotly.express as px
from dataframe import get_df_total_hours

app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP])

time_periods = [
# '2020-Q1',
# '2020-Q2',
# '2020-Half-Yearly'
# '2020-Q3',
# '2020-Q4',
# '2020-Annual'
'2020-Q2'
]

period_dict = {
    '2020-Q1': ('01-01-2020','03-31-2020'),
    '2020-Q2': ('04-01-2020','06-30-2020'),
    '2020-Q3': ('07-01-2020','09-30-2020'),
    '2020-Q4': ('10-01-2020','12-31-2020'),
    '2020-Half-Yearly': ('01-01-2020','06-30-2020'),
    '2020-Annual': ('01-01-2020','12-31-2020')
}

controls = dbc.FormGroup(
    [
        dbc.Label("Select Timeperiod"),
        dcc.Dropdown(
            id="quarter-selector",
            options=[
                {"label": t, "value": t}
                for t in time_periods
            ],
            value="2020-Q2",
        ),
    ]
)


app.layout = dbc.Container(
    [
        html.H1("EQA Automation-Team Dashboard",
            style = {
                'textAlign':'center',
                'color': '#ad5555'
            }),
        html.Hr(),
        dbc.Row(
            [
                dbc.Col(controls, md=6, width={"size": 6, "offset": 3}),
            ],
            align="center",
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
################################################################################
###
### Graph CALLBACKS
###
################################################################################
@app.callback(
    [Output("all_proj_hours", "figure"),
     Output("type_pie", "figure"),
     Output("num_proj_bar", "figure")],
    [Input("quarter-selector", "value")]
)
def update_graphs(quarter):
    global df_total_hours
    df_total_hours = get_df_total_hours(period_dict[quarter][0], period_dict[quarter][1])

    fig1 = px.bar(df_total_hours, y="Hours")
    fig1.update_layout(
        height=700,
        xaxis=dict(
            title_text=""
        ),
        xaxis_type='category',
    )
    fig1.update_xaxes(automargin=True)
################################################################################
    global df_projtype
    # --------------------------------------------------------------------------------
    # Adding 'Type' to the df_total_hours
    # --------------------------------------------------------------------------------
    df_total_hours.reset_index(inplace=True)
    df_total_hours['Type'] = df_total_hours['Projects'].str.split(" ",n=1, expand=True)[0]
    df_total_hours.set_index('Projects', inplace=True)

    # --------------------------------------------------------------------------------
    # Get hours and count for each type of project
    # --------------------------------------------------------------------------------
    df_projtype = df_total_hours.groupby('Type').agg([('Hours','sum'), ('Count','count')])
    df_projtype.columns = df_projtype.columns.droplevel(0)

    # --------------------------------------------------------------------------------
    # Project type hours pie
    # --------------------------------------------------------------------------------
    fig2 = px.pie(df_projtype, values='Hours', names=df_projtype.index, title='Hours spent by Project Type')
    fig2.update_traces(textposition='inside', textinfo='percent+label', automargin=True)
################################################################################

    fig3 = px.bar(df_projtype, y="Count", text='Count')
    fig3.update_layout(
        title="Number of Project Types in Q2-2020",
        autosize=True,
    )
    fig3.update_traces(textposition='inside')
    fig3.update_xaxes(automargin=True)

    return fig1, fig2, fig3


if __name__ == "__main__":
    app.run_server(debug=True)
