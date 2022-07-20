mytopdeckslegacy = formatdecks.filter(mtgFormat=myactiveformat).values("theirDeck__name").annotate(
    popularity=Count("theirDeck"),
    percentpopularity=100 * F("popularity") / num_matches, mynumgames=Count("theirDeck",
                                                                            filter=Q(user=user, myDeck=myactivedeck)),
    mywingames=Count("theirDeck", filter=Q(user=user,
                                           myDeck=myactivedeck, didjawin=1)),
    mwp=Case(When(mynumgames=0, then=0), default=100 *
             F("mywingames") / F("mynumgames")),
).order_by("-popularity")[:40]


class Deck(models.Model):
    name = models.CharField(verbose_name="deck name", max_length=25)
    date = models.DateTimeField(default=timezone.now)


class League(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    date = models.DateTimeField(default=timezone.now)
    myDeck = models.ForeignKey(
        Deck, null=True, on_delete=models.CASCADE, related_name="mydeckname")
