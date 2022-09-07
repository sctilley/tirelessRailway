from django.urls import path
from . import views
from django.contrib.staticfiles.storage import staticfiles_storage
from django.views.generic.base import RedirectView
from django.conf import settings

urlpatterns = [
    path('', views.home, name="home"),
    path('decks/', views.decks, name="decks"),
    path('mystats/', views.mystats, name="mystats"),
    path('mymatches/', views.mymatches, name="mymatches"),
    path('leaguedetail/<int:pk>', views.leaguedetail, name="leaguedetail"),
    path('landingpage/', views.landingpage, name="landingpage"),
    path('test/', views.test, name="test"),
    path('challenge/', views.challenge, name="challenge"),
]

htmx_urlpatters = [
    path('leaguescore/', views.leaguescore, name='leaguescore'),
    path('stats50s/', views.stats50s, name='stats50s'),
    path('leaguescoreAll/', views.leaguescoreAll, name='leaguescoreAll'),
    path('listofdecks/', views.listofdecks, name='listofdecks'),
    path('listofdecksArche/', views.listofdecksArche, name='listofdecksArche'),
    path('listofflavors/', views.listofflavors, name='listofflavors'),
    path('listofarchetypes/', views.listofarchetypes, name='listofarchetypes'),
    path('listofflavorsformatch/', views.listofflavorsformatch,
         name='listofflavorsformatch'),
    path('checkopponent/', views.checkopponent, name='checkopponent'),
    path('statstable/', views.statstable, name='statstable'),
    path('leaguedelete/<int:pk>', views.leaguedelete, name='leaguedelete'),
    path('matchtablebody/', views.matchtablebody, name='matchtablebody'),

]

urlpatterns += htmx_urlpatters
