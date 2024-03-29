from django.urls import path, re_path

from . import views

app_name = 'form'

urlpatterns = [
    # ex: /
    path('', views.home, name='home'),
    # ex: /signup
    path('signup', views.signup, name='signup'),
    # ex: /search
    path('search', views.search, name='search'),
    # ex: /chart
    path('chart', views.chart, name='chart'),
    # ex: /map
    path('map', views.map, name='map'),
    # ex: /geo_data.json
    path('chart_data.json', views.chart_data, name='chart_data'),
]