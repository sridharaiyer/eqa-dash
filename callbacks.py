from dash.dependencies import Output, Input
import dash
import plotly.express as px
from dataframe import get_df_total_hours, get_file_count, get_df_total_scripts
from layout import create_danger_alert, period_dict


def register_callbacks(app):
    @ app.callback(
        [
            Output("the_alert", "children"),
            Output("list_of_projects", "figure"),
            Output("all_proj_hours", "figure"),
            Output("type_pie", "figure"),
            Output("num_proj_bar", "figure"),
            Output("num_of_scripts", "figure"),
            Output("script_count_table", "figure")
        ],
        [Input("quarter-selector", "value")]
    )
    def update_graphs(quarter):
        if get_file_count() < 1:
            alert_msg = "No metrics data XLSX. Please contact EQA Support"
            return (
                create_danger_alert(alert_msg),
                dash.no_update,
                dash.no_update,
                dash.no_update,
                dash.no_update,
                dash.no_update,
                dash.no_update
            )
        else:
            start_date = period_dict[quarter][0]
            end_date = period_dict[quarter][1]
            df_total_hours = get_df_total_hours(start_date, end_date)

            if len(df_total_hours) == 0:
                alert_msg = f'No data found for period {start_date} to {end_date}'
                return (
                    create_danger_alert(alert_msg, dismissable=True),
                    dash.no_update,
                    dash.no_update,
                    dash.no_update,
                    dash.no_update,
                    dash.no_update,
                    dash.no_update
                )

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

            # ---------------------------------------------------------
            # Number of scripts
            # ---------------------------------------------------------
            df_total_scripts = get_df_total_scripts(start_date, end_date)

            fig5 = px.bar(df_total_scripts, x='Projects', y='Scripts')
            fig5.update_layout(
                title=f"Total Scripts developed Per Project from {start_date} to {end_date}",
                height=800,
                xaxis={'title_text': '',
                       'tickangle': 90
                       }
            )
            fig5.update_xaxes(automargin=True)

            # --------------------------------------------------------------------------------
            # Adding 'Type' to the df_total_scripts
            # --------------------------------------------------------------------------------
            df_total_scripts['Type'] = df_total_scripts['Projects'].str.replace(
                '-', ' ').str.split(n=1, expand=True)[0]
            df_total_scripts['Projects'] = df_total_scripts['Projects'].str.split(
                '-', n=1).str[1].str.strip()

            try:
                num_of_core_scripts = df_total_scripts.groupby('Type')['Scripts'].sum().loc['Core']
            except KeyError:
                num_of_core_scripts = 0

            try:
                num_of_mobile_scripts = df_total_scripts.groupby(
                    'Type')['Scripts'].sum().loc['Mobile']
            except KeyError:
                num_of_mobile_scripts = 0

            fig6 = go.Figure(
                data=[go.Table(
                    header=dict(values=list(['Core', 'Mobile']),
                                fill_color='paleturquoise',
                                align='center',
                                font_size=18,
                                height=38
                                ),
                    cells=dict(values=[num_of_core_scripts, num_of_mobile_scripts],
                               fill_color='lavender',
                               align='center',
                               font_size=16,
                               height=35
                               )

                )
                ])

            fig6.update_layout(
                autosize=True,
                title=f"Total Scripts developed from {start_date} to {end_date}",
            )

            return dash.no_update, fig4, fig1, fig2, fig3, fig5, fig6
