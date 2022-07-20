from django import forms
from .models import League, Match, Flavor, Deck, Archetype, MtgFormat
from django.contrib.auth.models import User
from datetime import datetime, date
from django.forms import inlineformset_factory


class MatchForm(forms.ModelForm):

    game1 = forms.BooleanField(label='one', required=False, widget=forms.CheckboxInput(
        attrs={'class': 'largerCheckbox'}))
    game2 = forms.BooleanField(label='two', required=False, widget=forms.CheckboxInput(
        attrs={'class': 'largerCheckbox'}))
    game3 = forms.BooleanField(label='three', required=False, widget=forms.CheckboxInput(
        attrs={'class': 'largerCheckbox'}))
    theirname = forms.CharField(
        label="their user name", widget=forms.TextInput(attrs={'list': 'usernamelist', 'hx-get': '/checkopponent', 'hx-target': '#namereceptor'}))
    theirArchetype = forms.ModelChoiceField(
        queryset=Archetype.objects.all(), label='Archetype', required=False, widget=forms.Select(attrs={'class': 'hidden', 'hx-get': '/listofdecksArche', 'hx-target': 'next select', 'hx-swap': 'innerHTML'}))
    theirDeck = forms.ModelChoiceField(
        queryset=Deck.objects.filter(mtgFormat=1).order_by('name'), label='deck', widget=forms.Select(attrs={'hx-trigger': 'change', 'hx-get': '/listofflavors', 'hx-target': 'next select', 'hx-swap': 'innerHTML'}))
    theirFlavor = forms.ModelChoiceField(
        required=False, queryset=Flavor.objects.all(), label='variant', widget=forms.Select(attrs={'hx-trigger': 'load', 'hx-get': '/listofflavorsformatch', 'hx-target': 'this', 'hx-include': 'previous select'}))
    date = forms.DateField(initial=date.today(), widget=forms.DateInput(
        attrs={'class': 'hidden', 'type': 'date', 'max': datetime.now().date()}))

    class Meta:
        model = Match

        fields = (
            'date',
            'theirname',
            'theirArchetype',
            'theirDeck',
            'theirFlavor',
            'game1',
            'game2',
            'game3',
        )


class LeagueForm(forms.ModelForm):
    mtgFormat = forms.ModelChoiceField(
        queryset=MtgFormat.objects.all(), label='Format', widget=forms.Select(attrs={}))
    myDeck = forms.ModelChoiceField(
        queryset=Deck.objects.all(), label='My Deck', widget=forms.Select(attrs={}))
    myFlavor = forms.ModelChoiceField(
        queryset=Flavor.objects.all(), label='Varient', widget=forms.Select(attrs={}))

    class Meta:
        model = League
        fields = ('mtgFormat', 'myDeck', 'myFlavor')


class DeckForm(forms.ModelForm):
    mtgFormat = forms.ModelChoiceField(
        queryset=MtgFormat.objects.all(), label='Format', widget=forms.Select(attrs={'hx-trigger': 'load, change', 'hx-get': '/listofarchetypes', 'hx-target': '#id_archetype'}))
    archetype = forms.ModelChoiceField(
        queryset=Archetype.objects.all(), label='Archetype', widget=forms.Select(attrs={'hx-get': '/listofflavors', 'hx-target': 'next td'}))

    class Meta:
        model = Deck
        fields = (
            'mtgFormat',
            'archetype',
            'name',
            'image',
        )


class FlavorForm(forms.ModelForm):
    name = forms.CharField(
        label="varient name", widget=forms.TextInput(attrs={'class': 'redtest2'}))
    isdefault = forms.BooleanField(label='Make Default Varient', required=False, widget=forms.CheckboxInput(
        attrs={'class': 'largerCheckbox'}))

    class Meta:
        model = Flavor
        fields = (
            'deck',
            'name',
            'isdefault',
        )
