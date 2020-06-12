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

def home_kr(requests):
    context = fc.give_context("kr")
    return render(requests, "covidcases/index_kr.html", context)

def home_spa(requests):
    context = fc.give_context()
    return render(requests, "covidcases/index_kr.html", context)

def home_en(requests):
    context = fc.give_context("en")
    return render(requests, "covidcases/index_kr.html", context)

def home_mobile_kr(requests):
    context = fc.give_context("kr")
    return render(requests, "covidcases/mobile.html", context) 

def home_mobile_en(requests):
    context = fc.give_context("en")
    return render(requests, "covidcases/mobile.html", context) 

def home_mobile_spa(requests):
    context = fc.give_context("spa")
    return render(requests, "covidcases/mobile.html", context)    