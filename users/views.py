from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import UserRegistrerForm, ProfileUpdateForm
from django.contrib.auth.decorators import login_required
from leagues.models import Tag
from leagues.forms import TagForm


def register(request):
    if request.method == 'POST':
        form = UserRegistrerForm(request.POST)
        if form.is_valid():
            form.save()
            username = form.cleaned_data.get('username')
            messages.success(
                request, f'Account created for {username}, you can now login')
            return redirect('login')
    else:
        form = UserRegistrerForm()

    return render(request, 'users/register.html', {'form': form})


@login_required
def profile(request):
    fff = request.user.profile.recentFormat
    ffd = request.user.profile.recentDeck
    ffl = request.user.profile.recentFlavor
    ffu = request.user.profile.mtgoUserName
    tagbutton = False

    user = request.user
    usertags = Tag.objects.filter(user=user)
    if usertags:
        tagbutton = True

    print("request", request.GET)
    for key in request.GET:
        var = request.GET[key]
        if var == "tags":
            tagbutton = True

    t_form = TagForm()

    if request.method == 'POST':
        print("request here", request.POST)

        if "t_form" in request.POST:
            t_form = TagForm(request.POST)
            if t_form.is_valid():
                tag = t_form.save(commit=False)
                tag.user = request.user
                tag.save()
                return redirect('profile')

        p_form = ProfileUpdateForm(
            request.POST, instance=request.user.profile)

        if p_form.is_valid():
            p_form.save()
            return redirect('profile')
    else:
        p_form = ProfileUpdateForm(
            instance=request.user, initial={'recentFormat': fff, 'recentDeck': ffd, 'recentFlavor': ffl, 'mtgoUserName': ffu})
        p_form.fields['recentFormat'].widget.attrs.update(
            {'name': 'recentFormat', 'hx-trigger': 'change, load', 'hx-get': "/listofdecks", 'hx-swap': 'innerHTML', 'hx-target': '#id_recentDeck'})
        p_form.fields['recentDeck'].widget.attrs.update(
            {'hx-trigger': 'change, load', 'hx-get': "/listofflavors", 'hx-swap': 'innerHTML', 'hx-target': '#id_recentFlavor'})

    context = {
        't_form': t_form,
        'p_form': p_form,
        'usertags': usertags,
        'tagbutton': tagbutton,
    }

    return render(request, 'users/profile.html', context)
