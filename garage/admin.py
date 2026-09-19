from django.contrib import admin
from .models import Client, Vehicule, Reparation

admin.site.register(Client)
admin.site.register(Vehicule)
admin.site.register(Reparation)