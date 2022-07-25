from django.shortcuts import render, redirect
from django.contrib import messages
from .forms import UserRegistrerForm, ProfileUpdateForm
from django.contrib.auth.decorators import login_required


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

    if request.method == 'POST':
        print("request here", request.POST)
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
        'p_form': p_form,
    }

    return render(request, 'users/profile.html', context)
