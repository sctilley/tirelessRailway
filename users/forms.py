from django import forms
from django.contrib.auth.models import User
from django.contrib.auth.forms import UserCreationForm
from .models import Profile
from leagues.models import MtgFormat


class UserRegistrerForm(UserCreationForm):
    email = forms.EmailField()

    class Meta:
        model = User
        fields = ['username', 'email', 'password1', 'password2']


class ProfileUpdateForm(forms.ModelForm):

    recentFormat = forms.ModelChoiceField(
        queryset=MtgFormat.objects.all(), label='format')

    class Meta:
        model = Profile
        fields = [
            'recentFormat',
            'recentDeck',
            'recentFlavor',
            'mtgoUserName'
        ]
