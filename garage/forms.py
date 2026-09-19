from django import forms
from .models import Client, Vehicule, Reparation

class ClientForm(forms.ModelForm):
    class Meta:
        model = Client
        fields = ['nom', 'prenom', 'telephone', 'email']

class VehiculeForm(forms.ModelForm):
    class Meta:
        model = Vehicule
        fields = ['immatriculation', 'marque', 'modele', 'annee', 'client']

class ReparationForm(forms.ModelForm):
    class Meta:
        model = Reparation
        fields = ['vehicule', 'description', 'statut', 'cout']