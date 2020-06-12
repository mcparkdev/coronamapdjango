from django.urls import path
from . import views
from django.conf.urls import url

urlpatterns = [
    path('', views.home_kr, name="home_kr"),
    path('spa/', views.home_spa, name="home_spa"),
    path('en/', views.home_en, name="home_en"),
    path('mobile/',views.home_mobile_kr, name="home_mobile_kr"),
    path('mobile/en',views.home_mobile_en, name="home_mobile_en"),
    path('mobile/spa',views.home_mobile_spa, name="home_mobile_spa"),
]