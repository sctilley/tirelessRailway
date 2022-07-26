from django.urls import path
from . import views

urlpatterns = [
    path('', views.home, name="home"),
    path('decks/', views.decks, name="decks"),
    path('mystats/', views.mystats, name="mystats"),
    path('leaguedetail/<int:pk>', views.leaguedetail, name="leaguedetail"),
]

htmx_urlpatters = [
    path('leaguescore/', views.leaguescore, name='leaguescore'),
    path('listofdecks/', views.listofdecks, name='listofdecks'),
    path('listofdecksArche/', views.listofdecksArche, name='listofdecksArche'),
    path('listofflavors/', views.listofflavors, name='listofflavors'),
    path('listofarchetypes/', views.listofarchetypes, name='listofarchetypes'),
    path('listofflavorsformatch/', views.listofflavorsformatch,
         name='listofflavorsformatch'),
    path('checkopponent/', views.checkopponent, name='checkopponent'),
    path('statstable/', views.statstable, name='statstable'),
    path('leaguedelete/<int:pk>', views.leaguedelete, name='leaguedelete'),

]

urlpatterns += htmx_urlpatters
