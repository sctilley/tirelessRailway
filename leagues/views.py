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

from django.views.generic.edit import UpdateView, DeleteView

from .forms import DeckForm, FlavorForm, LeagueForm, MatchForm, TagForm
from .models import Archetype, Deck, Flavor, League, Match, MtgFormat, Tag


def home(request):

    context = {

    }

    return render(request, 'home.html', context)


@login_required(login_url='login')
def league(request):
    user = request.user
    try:
        currentleague = League.objects.filter(user=user).latest('dateCreated')
    except:
        currentleague = League.objects.none()

    usernamelist = Match.objects.all().values("theirname").distinct().order_by(Lower("theirname"))


    userdeckslist = League.objects.filter(user=user).values_list('myDeck_id').distinct()
    usersdecks = Deck.objects.filter(id__in=userdeckslist)


    initial_data = {
        'mtgFormat': user.profile.recentFormat,
        'myDeck': user.profile.recentDeck,
        'myFlavor': user.profile.recentFlavor,
        'mtgoUserName': user.profile.mtgoUserName,
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
                user.profile.mtgoUserName = league.mtgoUserName
                user.profile.recentFormat = league.mtgFormat
                user.profile.recentDeck = league.myDeck
                user.profile.recentFlavor = league.myFlavor
                user.profile.save()
                league.save()
                l_form.save_m2m()

                return redirect('league')

        if "matchformset" in request.POST:
            print("matchformset trigger~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~~", request.POST)

            leagueid = request.POST.get('matchformset', False)
            print("leagueid ~~~ is type", type(leagueid))
            if leagueid:
                leaguehere = League.objects.get(pk=int(leagueid))
                formset = Matchesinlineformset(request.POST, instance=leaguehere)

            else:
                formset = Matchesinlineformset(request.POST, instance=currentleague)

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

        if "drop" in request.POST:
            print("Dropform ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
            currentleague.isFinished = 1
            currentleague.save()

            return redirect('league')

        if "delete" in request.POST:
            print("Delete form!!!! ~~~~~~~~~~~~~~~~~~~~~~~~~~~~~")
            currentleague.delete()
            return redirect('league')



    context = {
        'usersdecks': usersdecks,
        'l_form': l_form,
        'currentleague': currentleague,
        'matchformset': m_formset,
        'usernamelist': usernamelist,

    }

    return render(request, 'league.html', context)

def leagueroll(request):
    lformat = request.GET['formatselect']

    if 'formatselect' in request.GET:
        fselect = int(request.GET['formatselect'])

    if 'deckselect' in request.GET:
        dselect = int(request.GET['deckselect'])

    if 'varientselect' in request.GET:
        try:
            vselect = int(request.GET['varientselect'])
        except:
            vselect = 0
    

    user = request.user

    fiveohs = 0
    fourones = 0
    threetwos = 0
    twothrees = 0
    onefours = 0
    ohfives = 0
    fiveohsper = 0
    fouronesper = 0
    threetwosper = 0
    twothreesper = 0
    onefoursper = 0
    ohfivesper = 0

    if dselect == 0:
        targetleagues = League.objects.filter(
            user=user, 
            isFinished=True, 
            mtgFormat=fselect, 
        )

    elif vselect == 0:
        targetleagues = League.objects.filter(
            user=user, 
            isFinished=True, 
            mtgFormat=fselect, 
            myDeck=dselect, 
        )
    else:
        targetleagues = League.objects.filter(
            user=user, 
            isFinished=True, 
            mtgFormat=fselect, 
            myDeck=dselect, 
            myFlavor=vselect
        )


    for league in targetleagues:
        if league.isFinished == True:
            wins = league.matches.filter(didjawin=1).count()
            if wins == 5:
                fiveohs += 1
            elif wins == 4:
                fourones += 1
            elif wins == 3:
                threetwos += 1
            elif wins == 2:
                twothrees += 1
            elif wins == 1:
                onefours += 1
            else:
                ohfives += 1

    closedLeaguesNum = targetleagues.count()
    if closedLeaguesNum > 0:
        fiveohsper = (fiveohs / closedLeaguesNum)*100
        fouronesper = (fourones / closedLeaguesNum)*100
        threetwosper = (threetwos / closedLeaguesNum)*100
        twothreesper = (twothrees / closedLeaguesNum)*100
        onefoursper = (onefours / closedLeaguesNum)*100
        ohfivesper = (ohfives / closedLeaguesNum)*100
    else:
        fiveohsper = 0
        fouronesper = 0
        threetwosper = 0
        twothreesper = 0
        onefoursper = 0
        ohfivesper = 0

    if dselect == 0:
        targetmatches = Match.objects.filter(user=user, mtgFormat=fselect)
    elif vselect == 0:
        targetmatches = Match.objects.filter(user=user, mtgFormat=fselect, myDeck=dselect)
    else:
        targetmatches = Match.objects.filter(user=user, mtgFormat=fselect, myDeck=dselect, myFlavor=vselect)

    matchwinpercentage = 0
    matchcount = 0
    matcheswon = 0
    matcheslost = 0
    gamewinpercentage = 0
    gamesplayed = 0
    gameswon = 0
    gameslost = 0

    game1wins = targetmatches.filter(game1=1).count()
    game1losses = targetmatches.filter(game1=0).count()
    game2wins = targetmatches.filter(game2=1).count()
    game2losses = targetmatches.filter(game2=0).count()
    game3wins = targetmatches.filter(game3=1).count()
    game3losses = targetmatches.filter(game3=0).count()

    if targetmatches.count() > 0:
        matchwinpercentage = ((targetmatches.filter(didjawin=1).count(
        )/targetmatches.count()))*100
    else:
        matchwinpercentage = 0

    if targetmatches.count() > 0:
        gamewinpercentage = ((targetmatches.filter(game1=1).count() + targetmatches.filter(game2=1).count() +
                              targetmatches.filter(game3=1).count())/(game1wins + game1losses + game2wins + game2losses + game3wins + game3losses))*100
    else:
        gamewinpercentage = 0


    leagueroll = targetleagues.annotate(wins=Count("matches", filter=Q(matches__didjawin=1))).order_by("-dateCreated")     

    if dselect == 0:
        filterdeck = None
    else:
        filterdeck = Deck.objects.get(pk=dselect)

    if vselect == 0:
        filterflavor = None
    else:
        filterflavor = Flavor.objects.get(pk=vselect)

    context = {
        'filterdeck': filterdeck,
        'filterflavor': filterflavor,
        'matchcount': targetmatches.count(),
        'matchwinpercentage': matchwinpercentage,
        'matcheswon': targetmatches.filter(didjawin=1).count(),
        'matcheslost': targetmatches.filter(didjawin=0).count(),
        'gamesplayed': game1wins + game1losses + game2wins + game2losses + game3wins + game3losses,
        'gameswon': game1wins + game2wins + game3wins,
        'gameslost': game1losses + game2losses + game3losses,
        'gamewinpercentage': gamewinpercentage,

        'leagueroll': leagueroll,
        'targetleagues': targetleagues,
        "fiveohs": fiveohs,
        "fourones": fourones,
        "threetwos": threetwos,
        "twothrees": twothrees,
        "onefours": onefours,
        "ohfives": ohfives,
        'fiveohsper': fiveohsper,
        'fouronesper': fouronesper,
        'threetwosper': threetwosper,
        'twothreesper': twothreesper,
        'onefoursper': onefoursper,
        'ohfivesper': ohfivesper,
    }
    return render(request, 'partials/leagueroll.html', context)

def data(request):

    return render(request, 'data.html')

def decks(request):
    Decks = Deck.objects.all().order_by("-dateCreated")

    deck_form = DeckForm()
    flavor_form = FlavorForm()

    if request.method == "POST":
        if 'deckForm' in request.POST:
            deck_form = DeckForm(request.POST, request.FILES)

            if deck_form.is_valid():
                deck = deck_form.save(commit=False)
                deck.dateCreated = datetime.now()
                deck.save()
                vt = request.POST['varienttext']

                if vt:
                    if "makedefault" in request.POST:
                        Flavor.objects.create(
                            name=vt, deck=deck, isdefault=True)
                    else:
                        Flavor.objects.create(
                            name=vt, deck=deck, isdefault=False)

                else:
                    Flavor.objects.create(
                        name="none/stock", deck=deck, isdefault=True)

                return redirect('decks')
        else:
            flavor_form = FlavorForm(request.POST)
            oldflavor = Flavor.objects.filter(isdefault=True)
            oldflavor.isdefault = False
            flavor_form.save()
            return redirect('decks')

    context = {
        'Decks': Decks,
        'deck_form': deck_form,
        'flavor_form': flavor_form,
    }

    return render(request, 'decks.html', context)


# HTMX STUFF:

def listofdecks(request):
    print(request.GET)
    user = request.user
    currentdeck = None

    if "arch" in request.GET:
        for key in request.GET:
            archtype = request.GET[key]
    
        print("archtype ", archtype)
        listofdecks = Deck.objects.filter(archetype=archtype).order_by('name')


    else:
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
    # print("List of Flavors request.GET ~~~ ", request.GET)
    user = request.user
    ldeck = 0
    allvarients = False

    if "mtgFormat" in request.GET:
        mtgformat = int(request.GET.get('mtgFormat'))

        if user.profile.recentFormat.id == mtgformat:
            ldeck = user.profile.recentDeck.id
            currentflavor = user.profile.recentFlavor

    elif "deckselect" in request.GET:
        allvarients = True

    for key in request.GET:
        if request.GET[key]:
            ldeck = request.GET[key]
        else:
            ldeck = 0

    listofflavors = Flavor.objects.filter(deck=ldeck).order_by('-isdefault', 'name')

    try:
        currentdeck = user.profile.recentDeck
        deck_match = currentdeck.id == int(ldeck)
    except:
        deck_match = False

    if deck_match:
        currentflavor = user.profile.recentFlavor
    else:
        currentflavor = None


    context = {
        'allvarients': allvarients,
        'currentflavor': currentflavor,
        'listofflavors': listofflavors,
    }

    return render(request, 'partials/htmx/listofflavors.html', context)

def listofflavorsformatch(request):
    user = request.user
    currentleague = League.objects.filter(user=user).latest('dateCreated')

    for key, value in request.GET.items():

        if "flavor" in key.lower():
            try:
                flavorvalue = int(request.GET[key])
                specialflavor = Flavor.objects.get(id=flavorvalue)
            except:
                flavorvalue = 0
                specialflavor = None

        if "deck" in key.lower():
            try:
                deckvalue = int(request.GET[key])
                listofflavors = Flavor.objects.filter(
                    deck=deckvalue).exclude(id=specialflavor.id).order_by('-isdefault')

            except:
                deckvalue = 0
                listofflavors = None

    context = {
        'specialflavor': specialflavor,
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

def leagueedit(request):
    print("reqeuest.GET for leagueedit is---------", request.GET)
    for key in request.GET:
        leagueid = request.GET[key]
        editleague = League.objects.get(pk=request.GET[key])

    Matchesinlineformset = inlineformset_factory(
        League, Match, form=MatchForm, extra=5, can_delete=False, max_num=5)
    
    e_formset = Matchesinlineformset(instance=editleague)

    

    context = {
        'editleague': editleague,
        'matchformset': e_formset,
    }

    return render(request, 'partials/htmx/leagueedit.html', context)



class DeckUpdateView(UpdateView):
    model = Deck
    fields = [
        'name',
        'mtgFormat',
        'archetype',
        'dateCreated',
        'image',
        ]
    success_url ="/"

class DeckDeleteView(DeleteView):
    model = Deck
    success_url ="/"