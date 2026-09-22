from django.contrib import admin
from django.utils.html import format_html
from django.urls import reverse
from .models import Client, Vehicule, Reparation, Facture, LigneFacture

# Enregistrement des modèles de base
admin.site.register(Client)
admin.site.register(Vehicule)
admin.site.register(Reparation)


class LigneFactureInline(admin.TabularInline):
    model = LigneFacture
    extra = 1


@admin.register(Facture)
class FactureAdmin(admin.ModelAdmin):
    list_display = ('numero', 'type_document', 'client', 'date_emission', 'statut', 'telecharger_pdf_button')
    list_filter = ('type_document', 'statut', 'date_emission')
    search_fields = ('numero', 'client__nom', 'client__prenom')
    inlines = [LigneFactureInline]

    def telecharger_pdf_button(self, obj):
        url = reverse('facture_pdf', args=[obj.id])
        return format_html(
            '<a class="button" href="{}" target="_blank" style="background-color: #2b6cb0; color: white; padding: 3px 10px; border-radius: 3px; text-decoration: none;">📄 PDF</a>',
            url
        )
    
    telecharger_pdf_button.short_description = "Action PDF"