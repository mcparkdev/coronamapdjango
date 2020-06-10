from django.shortcuts import render
from plotly.offline import plot
from .models import Case
from django.http import JsonResponse
import os
from django.conf import settings

from sqlalchemy import create_engine
from urllib.request import urlopen
import json
import pandas as pd
import plotly.express as px
import plotly.graph_objects as go
from . import functions as fc
import locale

def home(requests):
    df_zip = fc.give_df_zip()
    fig = px.choropleth_mapbox(df_zip, geojson=fc.give_json_file(), locations='ZIP', color='count',
                           color_continuous_scale="balance",
                           range_color=(min(df_zip['count']), max(df_zip['count'])),
                           mapbox_style="carto-positron",
                           hover_name="locality",
                           zoom=9, center = {"lat": 4.6097102, "lon": -74.081749},
                           opacity=0.5,
                           labels={'count':'Casos'},
                          )
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    plot_div = plot(fig,
               output_type='div',include_plotlyjs=False,
               show_link=False, link_text="", config={'displayModeBar': False})
    # Main Data
    bogota_total = f"{fc.give_bogota_total():,d}"
    bogota_extra = f"{fc.give_bogota_extra():,d}"
    
    # Detailed Data
    df_state = fc.give_df('state')
    df_state['ratio'] = df_state['count']/sum(df_state['count'])
    df_state['ratio'] = pd.Series(["{0:.2f}%".format(val * 100) for val in df_state['ratio']], index = df_state.index)
    states = ['Recuperado','Moderado','Severo','Crítico','Fallecido','Fallecido (no aplica, no causa directa)']
    df_state['state'] = pd.Categorical(df_state['state'], states)
    df_state = df_state.sort_values("state")
    bogota_state = list(df_state['count'])
    bogota_state_ratio = list(df_state['ratio'])

    # Data by locality
    locality_state_list = fc.give_list_locality_state_ratio()
    update = "8.6.2020, 15:20"
    context={
      'update': update,
      'covid_cases': fc.give_data_dict('locality'),
      'plot_div': plot_div,
      'bogota': [bogota_total,bogota_extra,bogota_state,bogota_state_ratio],
      'locality': locality_state_list,
    }
    return render(requests, "covidcases/index.html", context)
