#%%
import plotly.graph_objects as go
import re
from pathlib import Path
import os
import json
import numpy as np
import operator

localities = {
    "Antonio Nariño": [1115,1],
    "Barrios Unidos": [1112,2],
    "Bosa": [1107,4],
    "Chapinero": [1102,3],
    "Ciudad Bolívar": [1119,8],
    "Engativá": [1110,7],
    "Fontibón": [1109,3],
    "Kennedy": [1108,8],
    "La Candelaria": [1117,1],
    "Los Mártires": [1114,1],
    "Puente Aranda": [1116,3],
    "Rafael Uribe Uribe": [1118,4],
    "San Cristóbal": [1104,4],
    "Santa Fe": [1103,2],
    "Suba": [1111,10],
    "Sumapaz": [1120,4],
    "Teusaquillo": [1113,2],
    "Tunjuelito": [1106,2],
    "Usaquén": [1101,5],
    "Usme": [1105,7],
}

names = [*localities]
zip_locality_list = []
ziplist = []
zipnames = []
zip = '{0}{1}1'
for name in names:
    temp = []
    if (name == "Suba"):
        sub = [11,21,31,41,51,56,61,66,71,76]
        zip1 = '{0}{1}'
        for j in sub:
            current = zip1.format(localities[name][0],j)
            zip_locality_list.append([name,current])
            temp.append("/{}.json".format(str(current)))
    else:
        for j in range(1,localities[name][1]+1):
            current = zip.format(localities[name][0],j)
            zip_locality_list.append([name,current])
            temp.append("{}.json".format(str(current)))
    zipnames.append({name:temp})

def give_zip_list(name):
    switcher = {
        "locality": zip_locality_list,
        "names": zipnames,
    }
    return switcher.get(name, "Invalid list name")

#%%
from sqlalchemy import create_engine
from urllib.request import urlopen
import json
import pandas as pd
import plotly.express as px

DATABASES = {
    'coronamap':{
        'NAME': 'coronamap',
        'USER': 'postgres',
        'PASSWORD': '12150426aA',
        'HOST': 'localhost',
        'PORT': 5432,
    },
    'coronamap-yesterday':{
        'NAME': 'coronamap-yesterday',
        'USER': 'postgres',
        'PASSWORD': '12150426aA',
        'HOST': 'localhost',
        'PORT': 5432,
    },
}

# choose the database to use
db = DATABASES['coronamap']
db_yesterday = DATABASES['coronamap']
# construct an engine connection string
engine_string = "postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}".format(
    user = db['USER'],
    password = db['PASSWORD'],
    host = db['HOST'],
    port = db['PORT'],
    database = db['NAME'],
)

engine_string_yesterday = "postgresql+psycopg2://{user}:{password}@{host}:{port}/{database}".format(
    user = db_yesterday['USER'],
    password = db_yesterday['PASSWORD'],
    host = db_yesterday['HOST'],
    port = db_yesterday['PORT'],
    database = db_yesterday['NAME'],
)
engine = create_engine(engine_string)
engine_yesterday = create_engine(engine_string_yesterday)

'''Change directory'''
data_file_today = 'static/data/today.csv'
data_file_yesterday = 'static/data/yesterday.csv'
# data_file = '7_6.csv'
def give_raw_df(data=data_file_today,update=False,eng=engine):
    if update:
        i=pd.read_csv(data)
        i.to_sql('covid_cases', eng, if_exists='replace')
    df = pd.read_sql_query('select * from covid_cases',con=eng)
    df['state'] = df['state'].str.capitalize()
    df.loc[df['state'] == "Fallecido (no aplica, no causa directa)", 'state'] = "Fallecido"
    return df
df = give_raw_df(update=True)
df_yesterday = give_raw_df(data=data_file_yesterday,eng=engine_yesterday,update=True)
#%%
def give_bogota_total():
    return len(df)
#%%
def give_bogota_extra():
    return len(df) - len(df_yesterday)
# %%
def give_df(*name):
    group = [*name]
    return df.groupby(group).size().to_frame(name='count').reset_index()

#%%
def give_df_yesterday(*name):
    group = [*name]
    return df_yesterday.groupby(group).size().to_frame(name='count').reset_index()

#%%
def give_diff_df():
    diff = list(map(operator.sub, 
        give_df('locality')['count'].values.tolist(),
        give_df_yesterday('locality')['count'].values.tolist()))
    df_locality_diff = give_df('locality')
    df_locality_diff['count'] =diff
    return df_locality_diff

#%%
def give_data_dict(name):
    return df.set_index(name).to_dict()

#%%
def give_json_file():
    json_file = 'static/js/localities-data.json'
    # json_file = 'localities-data.json'
    with open(json_file, 'r',encoding='utf8') as response:
        js = json.load(response)
    return js
#%%
def give_df_zip():
    df_zip = pd.DataFrame(give_zip_list('locality'), columns = ["locality", "ZIP"])
    df_zip["count"] = 0
    local_count = give_df('locality').set_index('locality').to_dict()['count']
    for name in names:
        try:
            df_zip.loc[df_zip['locality'] == name, 'count'] = local_count[name]
        except:
            pass
    return df_zip

#%%
def give_list_locality_state_ratio(sortby = 'count', ascending=False):
    temp = give_df('locality').sort_values('count', ascending=ascending)
    names = list(temp['locality'])
    temp = give_df('locality','state')
    temp['state']=pd.Categorical(temp['state'], ["Recuperado","Moderado","Severo","Crítico","Fallecido","Fallecido (no aplica, no causa directa)"])
    temp['locality']=pd.Categorical(temp['locality'], names)
    df_locality_state = temp.sort_values(['locality','state'])
    diff_dict = give_diff_df().set_index('locality').to_dict()['count']
    locality_state_ratio = []
    for name in names:
        try:
            df_temp = df_locality_state[df_locality_state['locality']==name]
            df_temp['ratio'] = df_temp['count']/sum(df_temp['count'])
            df_temp['state'] = pd.Categorical(df_temp['state'], ["Recuperado","Moderado","Severo","Crítico","Fallecido","Fallecido (no aplica, no causa directa)"])
            df_temp = df_temp.sort_values("state")
            df_temp['ratio'] = pd.Series(["{0:.2f}%".format(val * 100) for val in df_temp['ratio']], index = df_temp.index)
            total_dict = give_df('locality').set_index('locality').to_dict()['count']
            df_temp['count'] = df_temp['count'].apply(lambda x : f"{x:,d}")
            graph_id = "main-bogota-graph-{}"
            dict_temp = {
                "name":name,
                "total": f"{total_dict[name]:,d}",
                "extra": diff_dict[name],
                "state": df_temp.set_index('state')['count'].to_dict(),
                "state_ratio": df_temp.set_index('state')['ratio'].to_dict(),
                "id": graph_id.format(names.index(name)+1),}
            locality_state_ratio.append(dict_temp)
        except:
            pass
    return locality_state_ratio

# %%
