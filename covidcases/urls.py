from django.urls import path
from . import views
from django.conf.urls import url

urlpatterns = [
    path('', views.home, name="home"),
    path('kr/', views.home_kr, name="home_kr"),
    path('en/', views.home_en, name="home_en"),
]