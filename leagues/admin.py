from django.contrib import admin
from .models import MtgFormat, Archetype, Deck, Flavor, League, Match, Tag


admin.site.register(MtgFormat)
admin.site.register(Archetype)
admin.site.register(Deck)
admin.site.register(Flavor)
admin.site.register(League)
admin.site.register(Match)
admin.site.register(Tag)
