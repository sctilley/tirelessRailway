from django.urls import path
from . import views
from .views import DeckDeleteView
from django.contrib.staticfiles.storage import staticfiles_storage
from django.views.generic.base import RedirectView
from django.conf import settings

urlpatterns = [
    path('', views.home, name="home"),
    path('about/', views.about, name="about"),
    path('league/', views.league, name="league"),
    path('data/', views.data, name="data"),
    path('decks/', views.decks, name="decks"),
    path('leaguedata/', views.leaguedata, name="leaguedata"),
    path('decks/<int:id>/update', views.deckdoctor, name="deckdoctor"),
    path('test/', views.test, name="test"),
    path('deckupdate/', views.deckupdate, name="deckupdate"),

]

htmx_urlpatters = [
    path('listofdecks/', views.listofdecks, name='listofdecks'),
    path('listofflavors/', views.listofflavors, name='listofflavors'),
    path('listofflavorsformatch/', views.listofflavorsformatch, name='listofflavorsformatch'),
    path('checkopponent/', views.checkopponent, name='checkopponent'),
    path('leagueroll/', views.leagueroll, name='leagueroll'),
    path('leagueedit/', views.leagueedit, name='leagueedit'),
    path('decktable/', views.decktable, name='decktable'),
    path('listofarchetypes/', views.listofarchetypes, name='listofarchetypes'),
    path('leaguetable/', views.leaguetable, name='leaguetable'),
    path('metatable/', views.metatable, name='metatable'),
]

urlpatterns += htmx_urlpatters
