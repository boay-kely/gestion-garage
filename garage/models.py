from django.db import models

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