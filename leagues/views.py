import datetime
from datetime import datetime

from django.conf import settings
from django.contrib.auth.decorators import login_required
from django.db.models import Case, Count, Exists, F, OuterRef, Q, When
from django.db.models.functions import Lower
from django.forms import inlineformset_factory
from django.http import HttpResponse
from django.shortcuts import get_object_or_404, redirect, render
from django.utils import timezone
from django.utils.timezone import make_aware, timedelta

from .forms import DeckForm, FlavorForm, LeagueForm, MatchForm, TagForm
from .models import Archetype, Deck, Flavor, League, Match, MtgFormat, Tag


def home(request):

    context = {

    }

    return render(request, 'home.html', context)


def league(request):

    user = request.user

    try:
        currentleague = League.objects.filter(user=user).latest('dateCreated')
    except:
        currentleague = League.objects.none()

    usernamelist = Match.objects.all().values("theirname").distinct().order_by(Lower("theirname"))

    initial_data = {
        'mtgFormat': user.profile.recentFormat,
        'myDeck': user.profile.recentDeck,
        'myFlavor': user.profile.recentFlavor,
        'tag': user.profile.recentTag,
    }

    l_form = LeagueForm(initial=initial_data)

    Matchesinlineformset = inlineformset_factory(
        League, Match, form=MatchForm, extra=5, can_delete=False, max_num=5)
    try:
        currentleague = League.objects.filter(user=user).latest('dateCreated')
        m_formset = Matchesinlineformset(instance=currentleague)
    except League.DoesNotExist:
        currentleague = 0
        m_formset = Matchesinlineformset()

    if request.method == "POST":
        print(request.POST)

        if "leagueform" in request.POST:
            l_form = LeagueForm(request.POST)
            if l_form.is_valid():
                league = l_form.save(commit=False)
                league.user = request.user
                league.mtgoUserName = user.profile.mtgoUserName
                user.profile.recentFormat = league.mtgFormat
                user.profile.recentDeck = league.myDeck
                user.profile.recentFlavor = league.myFlavor
                user.profile.save()
                league.save()
                l_form.save_m2m()

                return redirect('league')

        if "matchformset" in request.POST:
            formset = Matchesinlineformset(
                request.POST, instance=currentleague)
            if formset.is_valid():
                new_instances = formset.save(commit=False)
                for new_instance in new_instances:
                    new_instance.user = request.user
                    new_instance.mtgFormat = currentleague.mtgFormat
                    new_instance.myDeck = currentleague.myDeck
                    new_instance.myFlavor = currentleague.myFlavor
                    new_instance.theirArchetype = new_instance.theirDeck.archetype

                    if not new_instance.dateCreated:
                        new_instance.dateCreated = datetime.now()

                    if new_instance.game1 + new_instance.game2 + new_instance.game3 >= 2:
                        new_instance.didjawin = 1
                    else:
                        new_instance.didjawin = 0

                    if new_instance.game1 == new_instance.game2:
                        new_instance.game3 = None

                    new_instance.save()

                    if currentleague.matches.count() >= 5:
                        currentleague.isFinished = 1
                        currentleague.save()

                return redirect('league')
            else:
                print("errors be here")
                print(formset.errors)

    context = {

        'l_form': l_form,
        'currentleague': currentleague,
        'matchformset': m_formset,
        'usernamelist': usernamelist,

    }

    return render(request, 'league.html', context)


def data(request):

    return render(request, 'data.html')


# HTMX STUFF:

def listofdecks(request):
    user = request.user
    for key in request.GET:
        lformat = request.GET[key]
    try:
        listofdecks = Deck.objects.filter(mtgFormat=lformat).order_by('name')
    except:
        listofdecks = None
    try:
        currentformat = user.profile.recentFormat.id
    except:
        currentformat = 999

    if lformat:
        formatvaluechecker = int(lformat)
    else:
        formatvaluechecker = 0

    has_format = 'mtgFormat' in request.GET
    format_matches = currentformat == formatvaluechecker

    if has_format and format_matches:
        currentdeck = user.profile.recentDeck
        listofdecks = Deck.objects.filter(mtgFormat=lformat).order_by('name')
    else:
        currentdeck = None

    context = {
        'listofdecks': listofdecks,
        'currentdeck': currentdeck,
    }

    return render(request, 'partials/htmx/listofdecks.html', context)


def listofflavors(request):
    user = request.user
    ldeck = 0

    if "mtgFormat" in request.GET:
        mtgformat = int(request.GET.get('mtgFormat'))

        if user.profile.recentFormat.id == mtgformat:
            ldeck = user.profile.recentDeck.id
            currentflavor = user.profile.recentFlavor

    else:
        for key in request.GET:
            if request.GET[key]:
                ldeck = request.GET[key]
            else:
                ldeck = 0

    listofflavors = Flavor.objects.filter(deck=ldeck).order_by('-isdefault', 'name')

    currentdeck = user.profile.recentDeck
    deck_match = currentdeck.id == int(ldeck)

    if deck_match:
        currentflavor = user.profile.recentFlavor
    else:
        currentflavor = None

    context = {
        'currentflavor': currentflavor,
        'listofflavors': listofflavors,
    }

    return render(request, 'partials/htmx/listofflavors.html', context)

def checkopponent(request):
    print("check opponent")
    print(request.GET)
    for key in request.GET:
        theirusername = request.GET[key]
        keyvalue = key

    print("theirusername: ", theirusername)

    theirdeckfield = keyvalue.replace("theirname", "theirDeck")
    theirflavorfield = keyvalue.replace("theirname", "theirFlavor")
    recentFormat = request.user.profile.recentFormat

    fromformat = Match.objects.filter(mtgFormat=recentFormat)

    try:
        getmatches = Match.objects.filter(mtgFormat=recentFormat, theirname=theirusername).order_by('-dateCreated')[:5]
        # getdeck = fromformat.filter(theirname=username).latest('dateCreated')

    except:
        getmatches = None
        print("oops", getmatches)

    print("getmatches!!!", getmatches)

    context = {
        'theirusername': theirusername,
        'getmatches': getmatches,
        'theirdeckfield': theirdeckfield,
        'theirflavorfield': theirflavorfield,
    }
    return render(request, 'partials/htmx/checkopponent.html', context)
