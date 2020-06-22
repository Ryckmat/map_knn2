# Import required libraries
from random import randint
import flask
import dash
import dash_core_components as dcc
import dash_html_components as html
import os, json
import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px
import datetime
from datetime import timedelta
from sklearn.cluster import KMeans
import seaborn as sn
import plotly.graph_objects as go
import dash_table


# Setup the app
# Make sure not to change this file name or the variable names below,
# the template is configured to execute 'server' on 'app.py'
server = flask.Flask(__name__)
server.secret_key = os.environ.get('secret_key', str(randint(0, 1000000)))
app = dash.Dash(__name__, server=server)


# Put your Dash code here


# Run the Dash app
if __name__ == '__main__':
    app.server.run(debug=True, threaded=True)
