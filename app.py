import dash
import dash_core_components as dcc
import dash_html_components as html
import plotly.graph_objs as go

import dash
import os, json
import geopandas as gpd
import matplotlib.pyplot as plt
import pandas as pd
import plotly.express as px
import datetime
from datetime import timedelta
from sklearn.cluster import KMeans
import seaborn as sn
import dash_table

from dash.dependencies import Input, Output

##########################################################################
##########################################################################

path_to_json = 'departements-france'
json_files = [pos_json for pos_json in os.listdir(path_to_json) if pos_json.endswith('.json')]

x = datetime.datetime(2020, 3, 1)
df = pd.DataFrame()
for i in sorted(json_files):
    df_temp = gpd.read_file('departements-france/'+i)
    df_temp["date"] = x
    x+= timedelta(days=1)
    frames = [df_temp, df]
    df = pd.concat(frames)

##########################################################################
##########################################################################
df1 = pd.DataFrame(df)
df1["lon"] = df.geometry.x
df1["lat"] = df.geometry.y

DeserializableColumns = ['Population', 'Beds']

for DeserializableColumn in DeserializableColumns:

  #Normalize Json Format
  jsonDf = pd.json_normalize(df1[DeserializableColumn])

  #Adding normalised json data into Df
  df1 = df1.join(jsonDf, rsuffix='' + DeserializableColumn)

#Drop Json Data
df1 = df1.drop(DeserializableColumns, axis=1)

df1= df1.drop(['geometry', 'Emergencies', 'MedicalTests','MedicalActs'], axis=1)
df1["Confirmed"].fillna(0.0, inplace = True)
df1["Deaths"].fillna(0.0, inplace = True)
df1["Recovered"].fillna(0.0, inplace = True)
df1["Severe"].fillna(0.0, inplace = True)
df1["Critical"].fillna(0.0, inplace = True)
##########################################################################
##########################################################################


X2 = pd.DataFrame()
X2["lon"]=df1["lon"]
X2["lat"]=df1["lat"]
X2["Deaths"]=df1["Deaths"]
# X2["Recovered"]=df1["Recovered"]
# X2["Severe"]=df1["Severe"]
# X2["Critical"]=df1["Critical"]
# X2["Confirmed"]=df1["Confirmed"]
# X2["Total"]=df1["Total"]
# X2["Under19"]=df1["Under19"]
# X2["Under39"]=df1["Under39"]
# X2["Under59"]=df1["Under59"]
# X2["Under74"]=df1["Under74"]
# X2["Over75"]=df1["Over75"]
# X2["Resuscitation"]=df1["Resuscitation"]
# X2["IntensiveCare"]=df1["IntensiveCare"]
# X2["TotalBeds"]=df1["TotalBeds"]
X2["date"]=df1["date"]
X2["Province/State"]=df1["Province/State"]
X2["date"]= X2["date"].apply(lambda x: x.strftime('%Y-%m-%d'))
X3 = X2.sort_values(by='date')

##########################################################################
##########################################################################
kmeans = KMeans(n_clusters = 3, init ='k-means++')
kmeans.fit(X3[X2.columns[0:3]]) # Compute k-means clustering.
X3['cluster_label'] = kmeans.fit_predict(X3[X2.columns[0:3]])
centers = kmeans.cluster_centers_ # Coordinates of cluster centers.
labels = kmeans.predict(X3[X2.columns[0:3]]) # Labels of each point



##########################################################################
##########################################################################
fig = go.Figure()
fig = px.scatter_mapbox(X3, lat="lat", lon="lon",
                        color="cluster_label", zoom=5, size="Deaths",
                        animation_frame="date",  height=750,
                        hover_name="Province/State", center={"lat": 46.4317, "lon": 2.3037})
fig.update_layout(mapbox_style="stamen-terrain")
fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})

########### Initiate the app
external_stylesheets = ['https://codepen.io/chriddyp/pen/bWLwgP.css']
app = dash.Dash(__name__, external_stylesheets=external_stylesheets)
server = app.server

# app.layout = html.Div([
#
# ], style={'display' : 'flex', 'flex-direction' : 'column', 'align-items':'center'})


app.layout = html.Div([
    html.Div([html.Img(src="assets/crayon2.jpg", width=300)],  style={'textAlign': 'center'}),
    dcc.Tabs(id="tabs-styled-with-props", value='tab-2', children=[
        dcc.Tab(label='Pré-diagnostic', value='tab-1'),
        dcc.Tab(label='Visualisation', value='tab-2'),
        dcc.Tab(label='Analyses', value='tab-3'),
    ], colors={
        "border": "white",
        "primary": "gold",
        "background": "whitesmoke"
    }),
    html.Div(id='tabs-content-props')
])

@app.callback(Output('tabs-content-props', 'children'),
              [Input('tabs-styled-with-props', 'value')])
def render_content(tab):
    if tab == 'tab-1':
        return html.Div([
        html.Div([html.Iframe(src="https://chat-bot-covid19.herokuapp.com/#/", height=450, width="100%", style={'border':'none'})])])
    elif tab == 'tab-2':
        return html.Div([
            html.H4(children='Carte des clusters en fonction du nombre de mort'),
            dcc.Graph(figure=fig),
            html.H4(children='Tableau des données des analyses'),
            dash_table.DataTable(
            id='datatable-interactivity',
            columns=[
                {"name": i, "id": i, "selectable": True} for i in X3.columns
            ],
            data=X3.to_dict('rows'),
            sort_action="native",
            sort_mode="multi",
            page_action="native",
            filter_action='native',
            page_current= 0,
            page_size= 10,
            export_format='xlsx')
        ])
    elif tab == 'tab-3':
        return html.Div([
               html.Div([
               html.H6(children='Ce collab renvoie à une étude sur la charge virale des patients. En résumé, la charge virale représente le potentiel de contamination et à être contaminé. On y retrouve des graphiques comme des nuages de points. Cette étude pourra permettre de développer l\'outil de pré-diagnostic et offre un nouvel axe d\'évaluation des risques. En résumé, la charge virale représente le potentiel de contamination et de développer des complications graves par rapport à la maladie'),
               html.A(html.Button('Charge virale', className='three columns'),href='https://colab.research.google.com/drive/1eHbrFwOYndR-l031-TYZ0N54pfUE_rOw?usp=sharing')],style={'width': '100%', 'display': 'inline-block'}),
               html.Div([html.H4(children=' ')]),
               html.Div([
               html.H6(children='Ce collab renvoie à une étude sur le taux de fréquentation des organismes de santé. On y retrouve une courbe d\'évolution qui pourrait servir en tant que référence pour planifier une éventuelle seconde vague et en optimiser la gestion.'),
               html.A(html.Button('Taux d\'occupation des organismes de santé', className='three columns'),href='https://colab.research.google.com/drive/1wYT9LdJhQAtN74gmvpLI762Vum6QyuYZ?usp=sharing')], style={'width': '100%', 'display': 'inline-block'}),
               ])


if __name__ == '__main__':
    app.run_server()
