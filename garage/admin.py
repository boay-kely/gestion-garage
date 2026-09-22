from django.contrib import admin
from .models import Client, Vehicule, Reparation, Facture, LigneFacture

# Enregistrement des anciens modèles
admin.site.register(Client)
admin.site.register(Vehicule)
admin.site.register(Reparation)

# Configuration pour ajouter les lignes de facture directement dans la facture
class LigneFactureInline(admin.TabularInline):
    model = LigneFacture
    extra = 1

@admin.register(Facture)
class FactureAdmin(admin.ModelAdmin):
    list_display = ('numero', 'type_document', 'client', 'date_emission', 'statut')
    inlines = [LigneFactureInline]