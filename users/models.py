from django.db import models
from django.contrib.auth.models import User


class Profile(models.Model):
    user = models.OneToOneField(User, on_delete=models.CASCADE)
    recentFormat = models.ForeignKey(
        'leagues.MtgFormat', null=True, on_delete=models.CASCADE)
    recentDeck = models.ForeignKey(
        'leagues.Deck', null=True, on_delete=models.CASCADE)
    recentFlavor = models.ForeignKey(
        'leagues.Flavor', null=True, on_delete=models.CASCADE)
    mtgoUserName = models.CharField(null=True, max_length=80)
    recentTag = models.ForeignKey(
        'leagues.Tag', null=True, on_delete=models.CASCADE)

    def __str__(self):
        return f'{self.user.username} Profile'
