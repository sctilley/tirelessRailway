from django import forms
from .models import League, Match, Flavor, Deck, Archetype, MtgFormat, Tag
from django.contrib.auth.models import User
from datetime import datetime, date
from django.forms import inlineformset_factory
from crispy_forms.helper import FormHelper


class ChangeDeckName(forms.ModelForm):
    class Meta:
        model = Deck

        fields = (

        )


class TagForm(forms.ModelForm):
    class Meta:
        model = Tag

        fields = (
            'name',
            'explaination'
        )


class SplitDateTimeWidget(forms.SplitDateTimeWidget):
    """
    A widget that splits datetime input into two <input type="text"> boxes,
    and uses HTML5 'date' and 'time' inputs.
    """

    def __init__(self, date_format=None, time_format=None, date_attrs=None, time_attrs=None):
        date_attrs = date_attrs or {'class': 'hidden'}
        time_attrs = time_attrs or {'class': 'hidden'}
        if "type" not in date_attrs:
            date_attrs["type"] = "date"
        if "type" not in time_attrs:
            time_attrs["type"] = "time"

        attrs = {'class': 'hidden'}

        return super().__init__(
            attrs=attrs, date_format=date_format, time_format=time_format, date_attrs=date_attrs, time_attrs=time_attrs
        )


class SplitDateTimeField(forms.SplitDateTimeField):
    widget = SplitDateTimeWidget()


class MatchForm(forms.ModelForm):

    game1 = forms.BooleanField(label='one', required=False, widget=forms.CheckboxInput(
        attrs={'class': 'largerCheckbox', 'title': 'This is game 1. Tick the box if you won.'}))
    game2 = forms.BooleanField(label='two', required=False, widget=forms.CheckboxInput(
        attrs={'class': 'largerCheckbox', 'title': 'This is game 2. Tick the box if you won.'}))
    game3 = forms.BooleanField(label='three', required=False, widget=forms.CheckboxInput(
        attrs={'class': 'largerCheckbox', 'title': 'This is game 3. Tick the box if you won.'}))
    theirname = forms.CharField(
        label="Their Username", widget=forms.TextInput(attrs={'list': 'usernamelist', 'autocomplete': 'off', 'hx-trigger': 'change', 'hx-get': '/checkopponent', 'hx-target': '#reporthere'}))
    theirArchetype = forms.ModelChoiceField(
        queryset=Archetype.objects.filter(mtgFormat=1).order_by('name'), label='Archetype', required=False, widget=forms.Select(attrs={'class': 'hidden', 'hx-get': '/listofdecks?arch=1', 'hx-target': 'next select', 'hx-swap': 'innerHTML', 'title': "This is option, if you don't select it it will be automatically assinged to match the deck"}))
    theirDeck = forms.ModelChoiceField(
        queryset=Deck.objects.filter(mtgFormat=1).order_by('name'), label='Their Deck', widget=forms.Select(attrs={'hx-trigger': 'change', 'hx-get': '/listofflavors', 'hx-target': 'next select', 'hx-swap': 'innerHTML'}))
    theirFlavor = forms.ModelChoiceField(
        required=False, queryset=Flavor.objects.all(), label='Variant', widget=forms.Select(attrs={'hx-trigger': 'load', 'hx-get': '/listofflavorsformatch', 'hx-target': 'this', 'hx-include': 'previous select'}))
    dateCreated = SplitDateTimeField(
        required=False, label='Date Played')

    class Meta:
        model = Match

        fields = (
            'dateCreated',
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
    mtgoUserName = forms.CharField(label='Your MTGO user name', widget=forms.TextInput())

    class Meta:
        model = League
        fields = ('mtgFormat', 'myDeck', 'myFlavor', 'mtgoUserName')


class DeckForm(forms.ModelForm):
    mtgFormat = forms.ModelChoiceField(
        queryset=MtgFormat.objects.all(), label='Format', widget=forms.Select(attrs={'hx-trigger': 'load, change', 'hx-get': '/listofarchetypes', 'hx-include': '#id_name', 'hx-target': '#id_archetype'}))
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
