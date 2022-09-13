from django.conf import settings
from django.shortcuts import render, redirect
from django.http import HttpResponse
from .models import Flavor, League, Match, Deck, MtgFormat, Archetype, Tag
from .forms import LeagueForm, MatchForm, DeckForm, FlavorForm, TagForm
from django.forms import inlineformset_factory
import datetime
from django.db.models import Count, F, Q, Case, When, Exists, OuterRef
from django.utils import timezone
from django.utils.timezone import timedelta, make_aware
from django.db.models.functions import Lower
from django.shortcuts import get_object_or_404
from django.contrib.auth.decorators import login_required
from datetime import datetime


def challenge(request):
    decks = Deck.objects.all().order_by('-name')
    user = request.user
    filterdeck = user.profile.recentDeck
    filterformat = user.profile.recentFormat
    formatdecks = Match.objects.filter(mtgFormat=filterformat)
    num_matches = Match.objects.filter(mtgFormat=filterformat).count()
    mytopdeckslegacy = formatdecks.filter(mtgFormat=filterformat).values("theirDeck__name").annotate(
        popularity=Count("theirDeck"),
        percentpopularity=100 * F("popularity") / num_matches, mynumgames=Count("theirDeck",
                                                                                filter=Q(user=user, myDeck=filterdeck)),
        mywingames=Count("theirDeck", filter=Q(user=user,
                                               myDeck=filterdeck, didjawin=1)),
        mwp=Case(When(mynumgames=0, then=0), default=100 *
                 F("mywingames") / F("mynumgames")),
    ).order_by("-popularity")[:40]

    context = {
        'decks': decks,
        'mytopdeckslegacy': mytopdeckslegacy,
        'filterdeck': filterdeck,

    }

    return render(request, 'challenge.html', context)


def test(request):
    decks = Deck.objects.all().order_by('-name')
    user = request.user
    filterdeck = user.profile.recentDeck
    filterformat = user.profile.recentFormat
    formatdecks = Match.objects.filter(mtgFormat=filterformat)
    num_matches = Match.objects.filter(mtgFormat=filterformat).count()
    mytopdeckslegacy = formatdecks.filter(mtgFormat=filterformat).values("theirDeck__name").annotate(
        popularity=Count("theirDeck"),
        percentpopularity=100 * F("popularity") / num_matches, mynumgames=Count("theirDeck",
                                                                                filter=Q(user=user, myDeck=filterdeck)),
        mywingames=Count("theirDeck", filter=Q(user=user,
                                               myDeck=filterdeck, didjawin=1)),
        mwp=Case(When(mynumgames=0, then=0), default=100 *
                 F("mywingames") / F("mynumgames")),
    ).order_by("-popularity")[:40]

    context = {
        'decks': decks,
        'mytopdeckslegacy': mytopdeckslegacy,
        'filterdeck': filterdeck,

    }

    return render(request, 'test.html', context)


def leaguedelete(request, pk):
    user = request.user
    league = get_object_or_404(League, pk=pk, user=request.user)
    matchcount = league.matches.count()
    wincount = league.matches.filter(didjawin=1).count()

    if request.method == "POST":
        league.delete()
        print("deleted")
        return redirect('home')

    context = {
        "league": league,
        "wincount": wincount,
    }

    return render(request, "deleted.html", context)


def leaguedetail(request, pk):
    user = request.user
    league = get_object_or_404(League, pk=pk, user=request.user)
    lformat = league.mtgFormat

    matchcount = league.matches.count()
    wincount = league.matches.filter(didjawin=1).count()
    print("matchcount", matchcount, wincount)

    Leagueinlineformset = inlineformset_factory(
        League, Match, form=MatchForm, extra=5, can_delete=False, max_num=5)

    formset = Leagueinlineformset(instance=league)

    addtag_form = TagForm()

    if request.method == "POST":
        print("post:", request.POST)
        if 'matchformset' in request.POST:
            formset = Leagueinlineformset(
                request.POST, instance=league)
            if formset.is_valid():
                new_instances = formset.save(commit=False)
                for new_instance in new_instances:
                    new_instance.user = request.user
                    new_instance.mtgFormat = league.mtgFormat
                    new_instance.myDeck = league.myDeck
                    new_instance.theirArchetype = new_instance.theirDeck.archetype

                    if new_instance.game1 + new_instance.game2 + new_instance.game3 >= 2:
                        new_instance.didjawin = 1
                    else:
                        new_instance.didjawin = 0

                    if new_instance.game1 == new_instance.game2:
                        new_instance.game3 = None

                    new_instance.save()
                    league.save()

                return redirect(league.get_absolute_url())
            else:
                print("errors be here")

    if request.method == "GET":
        print("GET REQUEST", request.GET)

        if 'drop' in request.GET:
            print("DROOOOOOOOOOOOOOOOOOOOP")
            league.isFinished = 1
            league.save()
            print("league.matches.count",
                  league.matches.count())

            if league.matches.count() == 0:
                print("ZER0000000000000000000000000000000 mataches")
                league.delete()

            return redirect('home')

    context = {
        'league': league,
        'wincount': wincount,
        'matchformset': formset,
        'addtag_form': addtag_form
    }

    return render(request, "leaguedetail.html", context)


def mymatches(request):

    context = {

    }
    return render(request, 'mymatches.html', context)


def mystats(request):
    user = request.user
    flavors = Flavor.objects.all()
    currentleague = League.objects.filter(user=user).latest('dateCreated')
    uservarients = flavors.filter(deck=user.profile.recentDeck)
    filterdeck = user.profile.recentDeck
    checkfilter = False

    mydecks = Deck.objects.filter(
        Exists(League.objects.filter(user=user, myDeck=OuterRef('pk')))).order_by('-dateCreated')

    context = {
        'filterdeck': filterdeck,
        'mydecks': mydecks,
        'checkfilter': checkfilter,
        'currentleague': currentleague,
        'uservarients': uservarients,
    }

    return render(request, 'mystats.html', context)


def matchtablebody(request):
    user = request.user
    usermatches = Match.objects.filter(user=user).order_by('dateCreated')

    context = {
        'usermatches': usermatches,

    }

    return render(request, "partials/matchtablebody.html", context)


def statstable(request):
    timeframe = 90
    user = request.user
    deckvalue = user.profile.recentDeck
    deckflavor = user.profile.recentFlavor
    currentleague = user.profile

    try:
        deckvalue = int(request.GET.get('deckname'))
    except:
        deckvalue = user.profile.recentDeck

    try:
        timeframe = int(request.GET.get('timeframe'))
    except:
        timeframe = 90

    try:
        varientselect = int(request.GET.get('varientselect'))
    except:
        varientselect = 0

    if "checkbox" in request.GET:
        checkfilter = True
    else:
        checkfilter = False

    # print("deckvalue:", deckvalue, "timeframe:", timeframe,
    #       "varientselect:", varientselect, "checkfilter:", checkfilter)

    filterdeck = deckvalue
    filterformat = user.profile.recentFormat

    formatdecks = Match.objects.filter(mtgFormat=filterformat)
    num_matches = Match.objects.filter(mtgFormat=filterformat).count()
    startdate = timezone.now()
    enddate = startdate - timedelta(days=timeframe)
    num_decks = formatdecks.filter(dateCreated__gte=enddate).count()

    targetdecks = Match.objects.filter(
        mtgFormat=filterformat, dateCreated__gte=enddate)

    mydecks = League.objects.filter(mtgFormat=filterformat).values(
        "myDeck__name").distinct()

    if varientselect > 0:
        filterprofile = {
            "user": user,
            "myDeck": filterdeck,
            "myFlavor": varientselect,

        }
    else:
        filterprofile = {
            "user": user,
            "myDeck": filterdeck,

        }

    mytopdeckslegacy = targetdecks.values("theirDeck__name").annotate(
        popularity=Count("theirDeck"),
        percentpopularity=100 * F("popularity") / num_matches, mynumgames=Count("theirDeck",
                                                                                filter=Q(**filterprofile)),
        mywingames=Count("theirDeck", filter=Q(**filterprofile, didjawin=1)),
        mylossgames=Count("theirDeck", filter=Q(**filterprofile, didjawin=0)),
        mwp=Case(When(mynumgames=0, then=0), default=100 *
                 F("mywingames") / F("mynumgames")),
    ).order_by("-popularity")[:50]

    currentleague = League.objects.filter(
        user=user).latest('dateCreated')

    context = {
        'mytopdeckslegacy': mytopdeckslegacy,
        'num_decks': num_decks,
        'filterdeck': filterdeck,
        'mydecks': mydecks,
        'checkfilter': checkfilter,
        'num_decks': num_decks,
        'currentleague': currentleague

    }

    return render(request, 'partials/statspagebackend.html', context)


def landingpage(request):

    leagues = League.objects.all()
    mtgformats = MtgFormat.objects.all()

    context = {
        'mtgformats': mtgformats,

    }

    return render(request, "landingpage.html", context)


@login_required(login_url='landingpage')
def home(request):
    user = request.user

    if user.profile.recentDeck == None:
        return redirect('profile')
    else:
        flavors = Flavor.objects.all()
        recentformat = user.profile.recentFormat
        mtgformats = MtgFormat.objects.all()
        userleagues = League.objects.filter(user=user)
        usermatches = Match.objects.filter(user=user)
        usernamelist = Match.objects.all().values(
            "theirname").distinct().order_by(Lower("theirname"))

        try:
            currentleague = League.objects.filter(
                user=user).latest('dateCreated')
        except:
            currentleague = League.objects.none()

        uservarients = flavors.filter(deck=user.profile.recentDeck)

        # forms
        initial_data = {
            'mtgFormat': user.profile.recentFormat,
            'myDeck': user.profile.recentDeck,
            'myFlavor': user.profile.recentFlavor,
            'tag': user.profile.recentTag,
        }
        league_form = LeagueForm(initial=initial_data)

        Leagueinlineformset = inlineformset_factory(
            League, Match, form=MatchForm, extra=5, can_delete=False, max_num=5)
        try:
            currentleague = League.objects.filter(
                user=user).latest('dateCreated')
            formset = Leagueinlineformset(instance=currentleague)
        except League.DoesNotExist:
            currentleague = 0
            formset = Leagueinlineformset()

        if request.method == "POST":
            if 'league_form' in request.POST:
                league_form = LeagueForm(request.POST)

                if league_form.is_valid():

                    league = league_form.save(commit=False)
                    league.user = request.user
                    league.mtgoUserName = user.profile.mtgoUserName
                    user.profile.recentFormat = league.mtgFormat
                    user.profile.recentDeck = league.myDeck
                    user.profile.recentFlavor = league.myFlavor
                    user.profile.save()
                    league.save()
                    league_form.save_m2m()

                    return redirect('home')

            if 'matchformset' in request.POST:

                formset = Leagueinlineformset(
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

                    return redirect('home')
                else:
                    print("errors be here")
                    print(formset.errors)

        context = {
            'league_form': league_form,
            'currentleague': currentleague,
            'matchformset': formset,
            'mtgformats': mtgformats,
            'uservarients': uservarients,
            'usernamelist': usernamelist
        }

        return render(request, 'home.html', context)


def decks(request):
    decks = Deck.objects.all().order_by('-name')
    user = request.user

    initial_data = {
        'mtgFormat': user.profile.recentFormat,
        'myDeck': user.profile.recentDeck
    }

    deck_form = DeckForm(initial=initial_data)
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

                return redirect('home')
        else:
            flavor_form = FlavorForm(request.POST)
            oldflavor = Flavor.objects.filter(isdefault=True)
            oldflavor.isdefault = False
            flavor_form.save()
            return redirect('home')

    context = {
        'decks': decks,
        'deck_form': deck_form,
        'flavor_form': flavor_form,
    }

    return render(request, 'decks.html', context)


def listofdecksArche(request):
    for key in request.GET:
        larche = request.GET[key]
    listofdecks = Deck.objects.filter(archetype=larche).order_by('name')
    context = {
        'listofdecks': listofdecks,
    }

    return render(request, 'partials/listofdecks.html', context)


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

    has_format = 'mtgFormat' in request.GET or 'recentFormat' in request.GET
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

    return render(request, 'partials/listofdecks.html', context)


def listofflavors(request):
    user = request.user
    listofflavors = None
    specialflavor = None
    allvarients = False

    if "mtgFormat" in request.GET:
        mtgformat = int(request.GET.get('mtgFormat'))

        if user.profile.recentFormat and mtgformat == user.profile.recentFormat.id:
            ldeck = user.profile.recentDeck.id
            specialflavor = user.profile.recentFlavor
            listofflavors = Flavor.objects.filter(
                deck=ldeck).order_by('-isdefault')

        else:
            pass

    else:
        for key in request.GET:
            try:
                ldeck = int(request.GET[key])
                listofflavors = Flavor.objects.filter(
                    deck=ldeck).order_by('-isdefault')
                if user.profile.recentDeck and ldeck == user.profile.recentDeck.id and "myDeck" in request.GET:
                    specialflavor = user.profile.recentFlavor
                    listofflavors = Flavor.objects.filter(
                        deck=ldeck).order_by('-isdefault')

                elif "deckname" in request.GET:
                    allvarients = True

            except:
                listofflavors = None
                specialflavor = None
                allvarients = False

    context = {
        'listofflavors': listofflavors,
        'specialflavor': specialflavor,
        'allvarients': allvarients,
    }

    return render(request, 'partials/listofflavors.html', context)


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
                    deck=deckvalue).order_by('-isdefault')

            except:
                deckvalue = 0
                listofflavors = None

    context = {
        'specialflavor': specialflavor,
        'listofflavors': listofflavors,
    }

    return render(request, 'partials/listofflavorsformatch.html', context)


def listofarchetypes(request):
    for key in request.GET:
        var = request.GET[key]
    listofarchetypes = Archetype.objects.filter(mtgFormat=var).order_by('name')
    print(type(listofarchetypes))
    context = {
        'listofarchetypes': listofarchetypes,
    }

    return render(request, 'partials/listofarchetypes.html', context)


def stats50s(request):
    user = request.user

    if "deckname" in request.GET:
        deckname = int(request.GET.get('deckname'))

    if "varientselect" in request.GET:
        varientselected = int(request.GET.get('varientselect'))

        if varientselected > 0:
            targetflavor = Flavor.objects.get(pk=varientselected)
        else:
            targetflavor = 0
    else:
        varientselected = user.profile.recentFlavor.pk
        targetflavor = user.profile.recentFlavor

    if "timeframe" in request.GET:
        timeframe = int(request.GET.get('timeframe'))
        startdate = timezone.now()
        enddate = startdate - timedelta(days=timeframe)

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

    leagues = League.objects.all()

    myactivedeck = user.profile.recentDeck

    userleagues = League.objects.filter(user=user, isFinished=1)

    try:
        myactivedeck = Deck.objects.get(pk=deckname)
    except:
        myactivedeck = user.profile.recentDeck

    if varientselected > 0:
        try:
            targetleagues = userleagues.filter(
                myDeck=myactivedeck, myFlavor=targetflavor, dateCreated__gte=enddate)
            targetmatches = Match.objects.filter(
                user=user, myDeck=myactivedeck, myFlavor=targetflavor, dateCreated__gte=enddate)
        except:
            targetleagues = userleagues.filter(
                myDeck=myactivedeck, myFlavor=targetflavor)
            targetmatches = Match.objects.filter(
                user=user, myDeck=myactivedeck, myFlavor=targetflavor)
    else:
        try:
            targetleagues = userleagues.filter(
                myDeck=myactivedeck, dateCreated__gte=enddate)
            targetmatches = Match.objects.filter(
                user=user, myDeck=myactivedeck, dateCreated__gte=enddate)
        except:
            targetleagues = userleagues.filter(myDeck=myactivedeck)
            targetmatches = Match.objects.filter(
                user=user, myDeck=myactivedeck)

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

    matchwinpercentage = 0
    matchcount = 0
    matcheswon = 0
    matcheslost = 0
    gamewinpercentage = 0
    gamesplayed = 0
    gameswon = 0
    gameslost = 0

    game1wins = targetmatches.filter(game1=1, myDeck=myactivedeck).count()
    game1losses = targetmatches.filter(game1=0, myDeck=myactivedeck).count()
    game2wins = targetmatches.filter(game2=1, myDeck=myactivedeck).count()
    game2losses = targetmatches.filter(game2=0, myDeck=myactivedeck).count()
    game3wins = targetmatches.filter(game3=1, myDeck=myactivedeck).count()
    game3losses = targetmatches.filter(game3=0, myDeck=myactivedeck).count()

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

    context = {
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

        'targetleagues': targetleagues,

        'matchcount': targetmatches.count(),
        'matchwinpercentage': matchwinpercentage,
        'matcheswon': targetmatches.filter(didjawin=1).count(),
        'matcheslost': targetmatches.filter(didjawin=0).count(),
        'gamesplayed': game1wins + game1losses + game2wins + game2losses + game3wins + game3losses,
        'gameswon': game1wins + game2wins + game3wins,
        'gameslost': game1losses + game2losses + game3losses,
        'gamewinpercentage': gamewinpercentage,

        'myactivedeck': myactivedeck,
        'targetflavor': targetflavor,
    }

    return render(request, 'partials/stats50s.html', context)


def leaguescore(request):
    lformat = request.GET['formatselect']
    user = request.user
    leaguescore = League.objects.filter(user=user, mtgFormat=lformat, isFinished=True).annotate(wins=Count(
        "matches", filter=Q(matches__didjawin=1))).order_by("-dateCreated")

    context = {
        'leaguescore': leaguescore,
    }
    return render(request, 'partials/leagues.html', context)


def leaguescoreAll(request):
    lformat = request.GET['formatselect']
    leaguescore = League.objects.filter(mtgFormat=lformat, isFinished=True).annotate(wins=Count(
        "matches", filter=Q(matches__didjawin=1))).order_by("-dateCreated")

    context = {
        'leaguescore': leaguescore,
    }
    return render(request, 'partials/leagues.html', context)


def checkopponent(request):
    print(request.GET)
    for key in request.GET:
        username = request.GET[key]
        keyvalue = key

    theirdeckfield = keyvalue.replace("theirname", "theirDeck")
    theirflavorfield = keyvalue.replace("theirname", "theirFlavor")
    recentFormat = request.user.profile.recentFormat

    fromformat = Match.objects.filter(mtgFormat=recentFormat)

    try:
        getdeck = fromformat.filter(theirname=username).latest('dateCreated')
        print("deck", getdeck.theirDeck.id)
        print("flavor", getdeck.theirFlavor.id)
    except:
        getdeck = None
        print("oops", getdeck)

    context = {
        'getdeck': getdeck,
        'theirdeckfield': theirdeckfield,
        'theirflavorfield': theirflavorfield,
    }

    return render(request, 'partials/checkopponent.html', context)

    user = request.user
    if user.profile.recentDeck == None:
        return redirect('profile')
    else:
        leagues = League.objects.all()
        user = request.user
        openLeagues = League.objects.filter(user=user, isFinished=False)
        closedLeagues = League.objects.filter(user=user, isFinished=True)
        recentformat = user.profile.recentFormat
        mtgformats = MtgFormat.objects.all()
        decks = Deck.objects.all()
        myactiveformat = MtgFormat(1)
        myactivedeck = user.profile.recentDeck
        myclosedleagues = closedLeagues.filter(myDeck=myactivedeck)
        userleagues = League.objects.filter(user=user)
        usermatches = Match.objects.filter(user=user)
        usernamelist = Match.objects.all().values(
            "theirname").distinct().order_by(Lower("theirname"))

        try:
            currentleague = League.objects.filter(
                user=user).latest('dateCreated')
        except:
            currentleague = League.objects.none()

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

        for league in userleagues.filter(myDeck=myactivedeck):
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

        closedLeaguesNum = closedLeagues.filter(myDeck=myactivedeck).count()

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

        matchwinpercentage = 0
        matchcount = 0
        matcheswon = 0
        matcheslost = 0
        gamewinpercentage = 0
        gamesplayed = 0
        gameswon = 0
        gameslost = 0

        num_matches = Match.objects.filter(mtgFormat=myactiveformat).count()
        game1wins = usermatches.filter(game1=1, myDeck=myactivedeck).count()
        game1losses = usermatches.filter(game1=0, myDeck=myactivedeck).count()
        game2wins = usermatches.filter(game2=1, myDeck=myactivedeck).count()
        game2losses = usermatches.filter(game2=0, myDeck=myactivedeck).count()
        game3wins = usermatches.filter(game3=1, myDeck=myactivedeck).count()
        game3losses = usermatches.filter(game3=0, myDeck=myactivedeck).count()

        if usermatches.filter(myDeck=myactivedeck).count() > 0:
            matchwinpercentage = ((usermatches.filter(didjawin=1, myDeck=myactivedeck).count(
            )/usermatches.filter(myDeck=myactivedeck).count()))*100
        else:
            matchwinpercentage = 0

        if usermatches.filter(myDeck=myactivedeck).count() > 0:
            gamewinpercentage = ((usermatches.filter(game1=1, myDeck=myactivedeck).count() + usermatches.filter(game2=1, myDeck=myactivedeck).count() +
                                  usermatches.filter(game3=1, myDeck=myactivedeck).count())/(game1wins + game1losses + game2wins + game2losses + game3wins + game3losses))*100
        else:
            gamewinpercentage = 0

        # forms
        initial_data = {
            'mtgFormat': user.profile.recentFormat,
            'myDeck': user.profile.recentDeck,
            'myFlavor': user.profile.recentFlavor,
        }
        league_form = LeagueForm(initial=initial_data)

        Leagueinlineformset = inlineformset_factory(
            League, Match, form=MatchForm, extra=5, can_delete=False, max_num=5)
        try:
            currentleague = League.objects.filter(
                user=user).latest('dateCreated')
            formset = Leagueinlineformset(instance=currentleague)
        except League.DoesNotExist:
            currentleague = 0
            formset = Leagueinlineformset()

        if request.method == "POST":
            if 'drop' in request.POST:
                currentleague.isFinished = 1
                currentleague.save()
                return redirect('home')

            if 'league_form' in request.POST:
                league_form = LeagueForm(request.POST)
                if league_form.is_valid():
                    league = league_form.save(commit=False)
                    league.user = request.user
                    league.mtgoUserName = user.profile.mtgoUserName
                    user.profile.recentFormat = league.mtgFormat
                    user.profile.recentDeck = league.myDeck
                    user.profile.recentFlavor = league.myFlavor
                    user.profile.save()

                    league.save()

                    return redirect("home")

            if 'matchformset' in request.POST:

                formset = Leagueinlineformset(
                    request.POST, instance=currentleague)

                print("herehhhhh")
                if formset.is_valid():
                    new_instances = formset.save(commit=False)
                    for new_instance in new_instances:
                        new_instance.user = request.user
                        new_instance.mtgFormat = currentleague.mtgFormat
                        new_instance.myDeck = currentleague.myDeck
                        new_instance.theirArchetype = new_instance.theirDeck.archetype

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

                    return redirect('home')
                else:
                    print("errors be here")
                    print(formset.errors)

        formatdecks = Match.objects.filter(mtgFormat=myactiveformat)
        num_matches = Match.objects.filter(mtgFormat=myactiveformat).count()

        context = {
            'openLeagues': openLeagues,
            'league_form': league_form,
            'currentleague': currentleague,
            'matchformset': formset,
            'mtgformats': mtgformats,

            'myactivedeck': myactivedeck,
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

            'myclosedleagues': myclosedleagues,

            'matchcount': usermatches.filter(myDeck=myactivedeck).count(),
            'matchwinpercentage': matchwinpercentage,
            'matcheswon': usermatches.filter(didjawin=1, myDeck=myactivedeck).count(),
            'matcheslost': usermatches.filter(didjawin=0, myDeck=myactivedeck).count(),
            'gamesplayed': game1wins + game1losses + game2wins + game2losses + game3wins + game3losses,
            'gameswon': game1wins + game2wins + game3wins,
            'gameslost': game1losses + game2losses + game3losses,
            'gamewinpercentage': gamewinpercentage,
            'usernamelist': usernamelist,
        }

        return render(request, 'home.html', context)
