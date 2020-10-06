import dash
import dash_bootstrap_components as dbc
from flask import Flask
from layout import layout
from callbacks import register_callbacks


server = Flask(__name__)
app = dash.Dash(external_stylesheets=[dbc.themes.BOOTSTRAP], server=server)

app.layout = layout
register_callbacks(app)

if __name__ == "__main__":
    app.run_server()
