#%%
import plotly.graph_objects as go
import plotly.express as px
import re
from pathlib import Path
import os
import json
import numpy as np
import operator
import pandas as pd
from plotly.offline import plot

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
'''Change directory'''
data_file_today = 'staticfiles/data/today.csv'
data_file_yesterday = 'staticfiles/data/yesterday.csv'
# data_file_today = 'today.csv'
# data_file_yesterday = 'yesterday.csv'
#%%
def read_csv(datafile, fix=True):
    data_df = pd.read_csv(datafile, skiprows=4,sep=';', skipfooter=2, engine="python")
    if fix:
        fix_df(data_df) 
    return data_df

#%%
def fix_df(data):
    column_names = ['caseID',"date","city","locality","age","sex","type","place","state"]
    data.columns = column_names
    data['state'] = data['state'].str.strip()
    data['state'] = data['state'].str.capitalize()
    data.loc[data['state'] == "Fallecido (no aplica, no causa directa)", 'state'] = "Fallecido"
    date_list =[]
    date_raw = data['date'].tolist()
    for i in range(0, len(data)):
        date_fixed = date_raw[i].split("/")
        date_fixed.reverse()
        date_fixed = "-".join(date_fixed)
        date_list.append(date_fixed)
    data['date'] = date_list
#%%
df = read_csv(data_file_today)
df_yesterday = read_csv(data_file_yesterday)
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
def give_plot_div(lang="spa"):
    switcher = {
        "spa": 'Casos',
        "en": 'Cases',
        "kr": '확진자수'
    }
    language = switcher.get(lang, "Invalid language")
    df_zip = give_df_zip()
    fig = px.choropleth_mapbox(df_zip, geojson=give_json_file(), locations='ZIP', color='count',
                            color_continuous_scale="OrRd",
                            range_color=(min(df_zip['count']), max(df_zip['count'])),
                            mapbox_style="carto-positron",
                            hover_name="locality",
                            zoom=9, center = {"lat": 4.6097102, "lon": -74.081749},
                            opacity=0.5,
                            labels={'count':language},
                        )
    fig.update_layout(margin={"r":0,"t":0,"l":0,"b":0})
    plot_div = plot(fig,
                output_type='div',include_plotlyjs=False,
                show_link=False, link_text="", config={'displayModeBar': False})
    return plot_div

#%%

def give_bogota_state(format = "count"):
    df_state = give_df('state')
    df_state['ratio'] = df_state['count']/sum(df_state['count'])
    df_state['ratio'] = pd.Series(["{0:.2f}%".format(val * 100) for val in df_state['ratio']], index = df_state.index)
    states = ['Recuperado','Moderado','Severo','Crítico','Fallecido','Fallecido (no aplica, no causa directa)']
    df_state['state'] = pd.Categorical(df_state['state'], states)
    df_state = df_state.sort_values("state")
    bogota_state = list(df_state['count'])
    [f"{item:,d}" for item in bogota_state]
    bogota_state_ratio = list(df_state['ratio'])
    switcher = {
        "count": bogota_state,
        "ratio": bogota_state_ratio,
    }
    return switcher.get(format, "Invalid property")
#%%
update_day = "11"
update_month = "06"
update_year = "2020"

def give_update_time(lang="spa", day = update_day, month=update_month, year=update_year):
    day = day
    month = month
    year = year
    date = "{0}.{1}.{2} 0:00{3}"
    switcher = {
        "spa": date.format(day,month,year, ""),
        "en": date.format(month,day,year, ""),
        "kr": date.format(month,day,year, " 시")
    }
    update = switcher.get(lang,"Invalid language")
    return update

#%%
def add_percentage(data):
    data['percentage'] = data['count']/sum(data['count'])
    data['percentage'] = pd.Series(["{0:.2f}%".format(val * 100) for val in data['percentage']], index = data.index)

#%%
def give_age_sex_graph(lang="spa"):
    switcher_x = {
        "spa": "Edad",
        "en": "Age",
        "kr": "나이",
    }
    switcher_y = {
        "spa": "Casos",
        "en": "Cases",
        "kr": "확진자수",
    }
    df_age = give_df('age')
    df_age_sex = give_df('age','sex')
    add_percentage(df_age)
    add_percentage(df_age_sex)
    df_age_f = df_age_sex[df_age_sex['sex']=="F"]
    df_age_m = df_age_sex[df_age_sex['sex']=="M"]
    fig = go.Figure()
    fig.add_trace(
        go.Scatter(
            x=df_age['age'], y=df_age['count'], name='Total',
            text = df_age['percentage'],
            hovertemplate =
                '<br><b>%{text}</b><br>',
        ))
    fig.add_trace(
        go.Scatter(
            x=df_age_f['age'], y=df_age_f['count'], name='F',
            text = df_age_f['percentage'],
            hovertemplate =
                '<br><b>%{text}</b><br>',
        ))
    fig.add_trace(
        go.Scatter(
            x=df_age_m['age'], y=df_age_m['count'], name='M',
            text = df_age_m['percentage'],
            hovertemplate =
                '<br><b>%{text}</b><br>',
        ))
    x_title = switcher_x.get(lang, "Invalid language")
    y_title = switcher_y.get(lang, "Invalid language")
    fig.update_xaxes(nticks=11,tick0=0, dtick=10, title_text=x_title)
    fig.update_yaxes(nticks=5,tick0=0, dtick=100, title_text=y_title)

    # fig.update_layout(xaxis_showgrid=False, yaxis_showgrid=False)
    fig.update_layout(
        hovermode='x',
        legend_orientation="h",
        template = 'plotly_white',
        margin = go.layout.Margin(
            l=20, r=10, t=0, b=30,
        ),
        legend=dict(x=0.72, y=1),
    )
    plot_div = plot(fig,
                output_type='div',include_plotlyjs=False,
                show_link=False, link_text="", config={'displayModeBar': False})
    return plot_div

#%%

def give_title(lang="spa"):
    switcher = {
        "spa" : "CoronaMap Bogotá",
        "en" : "CoronaMap Bogotá",
        "kr" : "코로나맵 보고타",
    }
    return switcher.get(lang,"Invalid Language")

#%%

def give_navbar(lang="spa"):
    switcher_title = {
        "spa" : "BOGOTÁ: COVID-19",
        "en" : "BOGOTÁ: COVID-19",
        "kr" : "보고타: 코로나-19"
    }
    switcher_language = {
        "spa" : "Idioma: Español",
        "en" : "Language: English",
        "kr" : "언어: 한국어"
    }
    navbar_title = switcher_title.get(lang, "Invalid language")
    navbar_update = give_update_time(lang)
    navbar_language = switcher_language.get(lang, "Invalid language")
    
    navbar = {
        "title": navbar_title,
        "update": navbar_update,
        "language": navbar_language,
    }

    return navbar
#%%
def give_sidebar(lang="spa"):
    sidebar_spa = {
        "title": "Home",
        "header": {
            "1":"Datos Principales",
            "2":"Hospitales",
            "3":"Apoyo",
            "4":"Idioma"
        },
        "content":{
            "1": ["Datos Actuales", "Estado de pacientes", "Casos por localidad","CoronaMap"],
            "2": ["Hacinación", "Hospitales UCI"],
            "3": ["Voluntario", "Donación"],
            "4": ["Coreano", "Español", "Inglés"],
        },
    }
    sidebar_kr = {
        "title": "홈",
        "header": {
            "1":"핵심내용",
            "2":"병원",
            "3":"도움 지원",
            "4":"언어"
        },
        "content":{
            "1": ["현황", "상세현황", "지역별 현황","코로나맵"],
            "2": ["사용 가능 여부", "ICU 병원"],
            "3": ["지원", "기부"],
            "4": ["한국어", "스페인어", "영어"],
        },
    }
    sidebar_en = {
        "title": "Home",
        "header": {
            "1":"Main Data",
            "2":"Hospitals",
            "3":"Support",
            "4":"Language",
        },
        "content":{
            "1": ["Today's Data", "Patient's state", "Case by Locality","CoronaMap"],
            "2": ["Availability", "ICU Hospitals"],
            "3": ["Volunteer", "Donation"],
            "4": ["Korean","Spanish","English"],
        },
    }
    switcher = {
        "spa" : sidebar_spa,
        "en"  : sidebar_en,
        "kr"  : sidebar_kr,
    }
    return switcher.get(lang,"Invalid language")


#%%
def give_footer(lang="spa"):
    footer_spa = {
        "developer": "Developer: Min Chang Park",
        "email": "e-mail: mc.park@uniandes.edu.co",
    }
    footer_en = footer_spa
    footer_kr = {
        "developer": "개발자: 박민창",
        "email": "이메일: mc.park@uniandes.edu.co",
    }
    switcher = {
        "spa" : footer_spa,
        "en"  : footer_en,
        "kr"  : footer_kr,
    }
    return switcher.get(lang, "Invalid language")
    
#%%
def give_data_box(lang="spa"):
    # Headers are in the give_side_bar() function to reduce redundancy.
    bogota_total = f"{give_bogota_total():,d}"
    bogota_extra = f"{give_bogota_extra():,d}"
    # Detailed Data
    bogota_state = give_bogota_state()
    bogota_state_ratio = give_bogota_state('ratio')
    # national_state = ["17,333","25,096","1,433"]
    # national_state_ratio = ["39.52%","57.22%","3.27%"]
    # worldwide_state = ["3,722,536","3,303,985","418,123"]
    # worldwide_state_ratio = ["50.00%","44.38%","5.62%"]

    # Data by locality
    locality_state_list = give_list_locality_state_ratio()
    # Data by age & sex
    # national_total = "43,682"
    # national_extra = "1,359"
    # worldwide_total = "7,145,539"
    # worldwide_extra = "108,918"

    df_nw = pd.read_csv("staticfiles/data/data.csv")
    national_total = df_nw['national_state'][3]
    national_extra = df_nw['national_extra'][0]
    national_state = df_nw['national_state'][:3].values.tolist()
    national_state_ratio = df_nw['national_state_ratio'][:3].values.tolist()

    worldwide_total = df_nw['worldwide_state'][3]
    worldwide_extra = df_nw['worldwide_extra'][0]
    worldwide_state = df_nw['worldwide_state'][:3].values.tolist()
    worldwide_state_ratio = df_nw['worldwide_state_ratio'][:3].values.tolist()

    
    kr_total = "{}명"
    kr_extra = "(전일대비)+{}"

    data_box_main_kr = {
        "title": {
            "bogota": "보고타확진자",
            "national": "국내확진자",
            "worldwide": "세계확진자",
        },
        "total": {
            "bogota": kr_total.format(bogota_total),
            "national": kr_total.format(national_total),
            "worldwide": kr_total.format(worldwide_total),
        },
        "extra": {
            "bogota"   : kr_extra.format(bogota_extra),
            "national" : kr_extra.format(national_extra),
            "worldwide": kr_extra.format(worldwide_extra),
        },
    }

    data_box_main_en = {
        "title": {
            "bogota": "Bogotá",
            "national": "National",
            "worldwide": "Worldwide",
        },
        "total": {
            "bogota": bogota_total,
            "national": national_total,
            "worldwide": worldwide_total,
        },
        "extra": {
            "bogota"   : "+{}".format(bogota_extra),
            "national" : "+{}".format(national_extra),
            "worldwide": "+{}".format(worldwide_extra),
        },
    }
    data_box_main_spa = {
        "title": {
            "bogota": "Bogotá",
            "national": "Nacional",
            "worldwide": "Global",
        },
        "total": {
            "bogota": bogota_total,
            "national": national_total,
            "worldwide": worldwide_total,
        },
        "extra": {
            "bogota"   : "+{}".format(bogota_extra),
            "national" : "+{}".format(national_extra),
            "worldwide": "+{}".format(worldwide_extra),
        },
    }

    data_box_detailed_kr = {
        "title": {
            "bogota":"보고타: {}명".format(bogota_total),
            "national": "국내: {}명".format(national_total),
            "worldwide": "세계: {}명".format(worldwide_total),
        },
        "label": ['완치자', '무증상자','경증 환자','중증 환자', '사망자', '격리자'],
        "count": {
            "bogota":bogota_state,
            "national":national_state,
            "worldwide":worldwide_state,
        },
        "ratio": {
            "bogota":bogota_state_ratio,
            "national":national_state_ratio,
            "worldwide":worldwide_state_ratio,
        },
    }

    data_box_detailed_en = {
        "title": {
            "bogota":"Bogotá: {}".format(bogota_total),
            "national": "National: {}".format(national_total),
            "worldwide": "Worldwide: {}".format(worldwide_total),
        },
        "label": ['Recovered', 'Moderate','Severe','Critical', 'Dead', 'Active'],
        "count": {
            "bogota":bogota_state,
            "national":national_state,
            "worldwide":worldwide_state,
        },
        "ratio": {
            "bogota":bogota_state_ratio,
            "national":national_state_ratio,
            "worldwide":worldwide_state_ratio,
        },
    }
    data_box_detailed_spa = {
        "title": {
            "bogota":"Bogotá: {}".format(bogota_total),
            "national": "Nacional: {}".format(national_total),
            "worldwide": "Global: {}".format(worldwide_total),
        },
        "label": ['Recuperados', 'Moderados','Severos','Críticos', 'Fallecidos', 'Activos'],
        "count": {
            "bogota":bogota_state,
            "national":national_state,
            "worldwide":worldwide_state,
        },
        "ratio": {
            "bogota":bogota_state_ratio,
            "national":national_state_ratio,
            "worldwide":worldwide_state_ratio,
        },
    }

    switcher_main = {
        "spa" : data_box_main_spa,
        "en"  : data_box_main_en,
        "kr"  : data_box_main_kr,
    }

    switcher_detailed = {
        "spa" : data_box_detailed_spa,
        "en"  : data_box_detailed_en,
        "kr"  : data_box_detailed_kr,
    }

    switcher_locality = {
        "spa": {
            "filter":"Orden decreciente (casos)",
            "placeholder":"Buscar por localidad",
        },
        "en" : {
            "filter":"Decreasing order (cases)",
            "placeholder":"Search by locality",
        },
        "kr" : {
            "filter":"확진자 분포 내림차순",
            "placeholder":"지역을 입력해주세요",
        },
    }

    switcher_map = {
        "spa": {
            "header":"CoronaMap",
            "update_box":"Actualizado",
            "source":"Fuente",
            "source_content":"Subsecretaría de Salud Pública. Secretaría Distrital de Salud 2020",
        },
        "en":{
            "header":"CoronaMap",
            "update_box":"Update",
            "source":"Source",
            "source_content":"Subsecretaría de Salud Pública. Secretaría Distrital de Salud 2020",
        },
        "kr":{
            "header":"코로나맵",
            "update_box":"업데이트",
            "source":"출처",
            "source_content":"Subsecretaría de Salud Pública. Secretaría Distrital de Salud 2020",
        }
    }

    switcher_kr = {
        "spa": {
            "unit":"",
            "day_before":"",
        },
        "en": {
            "unit":"",
            "day_before":"",
        },
        "kr": {
            "unit":"명",
            "day_before":"(전일대비)",
        }
    }

    data_box = {
        "main": switcher_main.get(lang, "Invalid language"),
        "detailed": switcher_detailed.get(lang, "Invalid language"),
        "locality": switcher_locality.get(lang, "Invalid language"),
        "map": switcher_map.get(lang, "Invalid language"),
        "kr": switcher_kr.get(lang, "Invalid language")
    }

    return data_box

#%%

def give_context(lang="spa"):
    bogota_total = f"{give_bogota_total():,d}"
    bogota_extra = f"{give_bogota_extra():,d}"
    # Detailed Data
    bogota_state = give_bogota_state()
    bogota_state_ratio = give_bogota_state('ratio')
    # Data by locality
    locality_state_list = give_list_locality_state_ratio()
    # Data by age & sex

    context={
        'title' : give_title(lang),
        'navbar': give_navbar(lang),
        'sidebar': give_sidebar(lang),
        'footer': give_footer(lang),
        'data_box': give_data_box(lang),
        'covid_cases': give_data_dict('locality'),
        'plot_div': [give_plot_div(lang), give_age_sex_graph(lang)],
        'locality': locality_state_list,
    }
    return context
