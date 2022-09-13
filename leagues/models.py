from django.db import models
from django.utils import timezone
from PIL import Image
from django.contrib.auth.models import User
from leagues.utils import image_resize
from django.urls import reverse


class MtgFormat(models.Model):
    name = models.CharField(max_length=200)

    def __str__(self):
        return self.name


class Archetype(models.Model):
    name = models.CharField(verbose_name="Archetype", max_length=40)
    mtgFormat = models.ForeignKey(
        MtgFormat, null=True, on_delete=models.CASCADE)

    def __str__(self):
        return str(self.name)


class Deck(models.Model):
    name = models.CharField(verbose_name="deck name", max_length=25)
    mtgFormat = models.ForeignKey(
        MtgFormat, null=True, on_delete=models.CASCADE)
    archetype = models.ForeignKey(
        Archetype, null=True, on_delete=models.CASCADE)
    dateCreated = models.DateTimeField(default=timezone.now)
    image = models.ImageField(default='defaultdeck.jpg', upload_to='deckpics')

    def __str__(self):
        return str(self.name)

    def save(self, *args, **kwargs):
        image_resize(self.image, 452, 616)
        super().save(*args, **kwargs)


class Flavor(models.Model):

    name = models.CharField(max_length=30, default='none')
    deck = models.ForeignKey(
        Deck, null=True, on_delete=models.CASCADE)
    isdefault = models.BooleanField('default', default=False)

    def __str__(self):
        return self.name


class Tag(models.Model):
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    name = models.CharField(max_length=30, default='none')
    explaination = models.TextField(default='none')

    def __str__(self):
        return self.name


class League(models.Model):
    mtgFormat = models.ForeignKey(
        MtgFormat, null=True, on_delete=models.CASCADE, related_name="mformat")
    mtgoUserName = models.CharField(max_length=40, null=True)
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    dateCreated = models.DateTimeField(default=timezone.now)
    myDeck = models.ForeignKey(
        Deck, null=True, on_delete=models.CASCADE, related_name="mydeckname")
    myFlavor = models.ForeignKey(
        Flavor, null=True, on_delete=models.CASCADE, related_name="myleagueflavor")
    isFinished = models.BooleanField('finished', default=False)
    tags = models.ManyToManyField(Tag, related_name="leagues")

    def __str__(self):
        return f'{self.mtgFormat} League with {self.myDeck} by {self.mtgoUserName} on {self.dateCreated}'

    def get_absolute_url(self):
        return reverse('leaguedetail', kwargs={'pk': self.pk})


class Tourneytype(models.Model):
    name = models.CharField(max_length=120)

    def __str__(self):
        return self.name


class Tournament(models.Model):
    tourneyType = models.ForeignKey(
        Tourneytype, null=True, on_delete=models.CASCADE, related_name="type")
    mtgFormat = models.ForeignKey(
        MtgFormat, null=True, on_delete=models.CASCADE, related_name="mformat2")
    mtgoUserName = models.CharField(max_length=40, null=True)
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    dateCreated = models.DateTimeField(default=timezone.now)
    myDeck = models.ForeignKey(
        Deck, null=True, on_delete=models.CASCADE, related_name="mydeckname2")
    myFlavor = models.ForeignKey(
        Flavor, null=True, on_delete=models.CASCADE, related_name="myleagueflavor2")
    isFinished = models.BooleanField('finished', default=False)

    def __str__(self):
        return str(self.mtgFormat)


class Match(models.Model):

    dateCreated = models.DateTimeField(default=timezone.now, null=True)
    theirname = models.CharField(null=True, max_length=100)
    theirArchetype = models.ForeignKey(
        Archetype(), verbose_name="Their Archetype", null=True, on_delete=models.CASCADE, related_name="theirarchetype")
    theirDeck = models.ForeignKey(
        Deck, verbose_name="Their Deck", null=True, on_delete=models.CASCADE, related_name="theirdeck")
    theirFlavor = models.ForeignKey(
        Flavor, verbose_name="Their Deck Details", null=True, on_delete=models.CASCADE, related_name="theirdetails")
    myDeck = models.ForeignKey(
        Deck, null=True, on_delete=models.CASCADE, related_name="mydeck")
    myFlavor = models.ForeignKey(
        Flavor, null=True, on_delete=models.CASCADE, related_name="mydeckdetails")
    game1 = models.BooleanField(
        verbose_name='Win', default=False, help_text="win")
    game2 = models.BooleanField(verbose_name='Win', default=False)
    game3 = models.BooleanField(verbose_name='Win', null=True, default=None)
    didjawin = models.BooleanField('Match Win', default=False)
    user = models.ForeignKey(User, null=True, on_delete=models.CASCADE)
    mtgFormat = models.ForeignKey(
        MtgFormat, null=True, on_delete=models.CASCADE, related_name="mtgFormat")
    league = models.ForeignKey(
        League, null=True, on_delete=models.CASCADE, related_name="matches")
    tourney = models.ForeignKey(
        Tournament, null=True, on_delete=models.CASCADE, related_name="matches")

    def __str__(self):
        return f'Match vs: {self.theirname} by {self.user} on {self.dateCreated} (league id {self.league.pk})'
