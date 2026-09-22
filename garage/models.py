from django.db import models
from django.utils import timezone  # <--- Ajouté pour la date de la facture

class Client(models.Model):
    nom = models.CharField(max_length=100)
    prenom = models.CharField(max_length=100)
    telephone = models.CharField(max_length=20)
    email = models.EmailField(blank=True, null=True)

    def __str__(self):
        return f"{self.nom} {self.prenom}"

class Vehicule(models.Model):
    immatriculation = models.CharField(max_length=20, unique=True)
    marque = models.CharField(max_length=50)
    modele = models.CharField(max_length=50)
    annee = models.IntegerField()
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='vehicules')

    def __str__(self):
        return f"{self.marque} {self.modele} ({self.immatriculation})"

class Reparation(models.Model):
    STATUT_CHOICES = [
        ('EN_ATTENTE', 'En attente'),
        ('EN_COURS', 'En cours'),
        ('TERMINE', 'Terminé'),
    ]
    vehicule = models.ForeignKey(Vehicule, on_delete=models.CASCADE)
    description = models.TextField()
    statut = models.CharField(max_length=20, choices=STATUT_CHOICES, default='EN_ATTENTE')
    cout = models.DecimalField(max_digits=10, decimal_places=2, default=0.00)
    date_entree = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Réparation #{self.id} - {self.vehicule}"

# -------------------------------------------------------------------
# NOUVEAUX MODÈLES (DEVIS & FACTURES) AJOUTÉS À LA SUITE
# -------------------------------------------------------------------

class Facture(models.Model):
    TYPE_CHOICES = [
        ('DEVIS', 'Devis'),
        ('FACTURE', 'Facture'),
    ]
    STATUT_CHOICES = [
        ('BROUILLON', 'Brouillon'),
        ('VALIDE', 'Validé / Payé'),
        ('ANNULE', 'Annulé'),
    ]

    type_document = models.CharField(max_length=10, choices=TYPE_CHOICES, default='FACTURE')
    numero = models.CharField(max_length=20, unique=True)
    client = models.ForeignKey(Client, on_delete=models.CASCADE, related_name='factures')
    reparation = models.ForeignKey(Reparation, on_delete=models.SET_NULL, null=True, blank=True)
    date_emission = models.DateField(default=timezone.now)
    statut = models.CharField(max_length=10, choices=STATUT_CHOICES, default='BROUILLON')

    def __str__(self):
        return f"{self.get_type_document_display()} {self.numero} - {self.client}"

    @property
    def total_ht(self):
        # Calcule la somme de toutes les lignes associées à cette facture
        return sum(ligne.total_ht for ligne in self.lignes.all())

    @property
    def tva(self):
        return float(self.total_ht) * 0.20  # TVA à 20%

    @property
    def total_ttc(self):
        return float(self.total_ht) + self.tva


class LigneFacture(models.Model):
    facture = models.ForeignKey(Facture, on_delete=models.CASCADE, related_name='lignes')
    description = models.CharField(max_length=255)  # Ex: Remplacement Filtre à Huile ou Main d'œuvre
    quantite = models.DecimalField(max_digits=7, decimal_places=2, default=1)
    prix_unitaire_ht = models.DecimalField(max_digits=10, decimal_places=2)

    @property
    def total_ht(self):
        return self.quantite * self.prix_unitaire_ht

    def __str__(self):
        return f"{self.description} ({self.quantite} x {self.prix_unitaire_ht}€)"