from django.urls import path
from . import views
from django.contrib.staticfiles.storage import staticfiles_storage
from django.views.generic.base import RedirectView
from django.conf import settings

urlpatterns = [
    path('', views.home, name="home"),
    path('league/', views.league, name="league"),
    path('data/', views.data, name="data"),
]

htmx_urlpatters = [
    path('listofdecks/', views.listofdecks, name='listofdecks'),
    path('listofflavors/', views.listofflavors, name='listofflavors'),
    path('listofflavorsformatch/', views.listofflavorsformatch, name='listofflavorsformatch'),
    path('checkopponent/', views.checkopponent, name='checkopponent'),
    path('leagueroll/', views.leagueroll, name='leagueroll'),
]

urlpatterns += htmx_urlpatters
