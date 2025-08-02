from django.db import models
from django.contrib.auth.models import User

class MaterialType(models.Model):
    nom = models.CharField(max_length=100)
    description = models.TextField(blank=True)

    def __str__(self):
        return self.nom

class Equipment(models.Model):
    ETAT_CHOICES = [
        ('Disponible', 'Disponible'),
        ('Affecté', 'Affecté'),
        ('Hors service', 'Hors service'),
    ]
    nom = models.CharField(max_length=100)
    numero_serie = models.CharField(max_length=50, unique=True)
    type_materiel = models.ForeignKey(MaterialType, on_delete=models.CASCADE)
    etat = models.CharField(max_length=20, choices=ETAT_CHOICES, default='Disponible')

    def __str__(self):
        return f"{self.nom} ({self.numero_serie})"

class MaterialRequest(models.Model):
    ETAT_CHOICES = [
        ('En attente', 'En attente'),
        ('Validée', 'Validée'),
        ('Refusée', 'Refusée'),
    ]
    demandeur = models.ForeignKey(User, on_delete=models.CASCADE)
    types_materiel = models.ManyToManyField(MaterialType)
    equipements = models.ManyToManyField(Equipment, blank=True)  # New field
    etat = models.CharField(max_length=20, choices=ETAT_CHOICES, default='En attente')
    commentaires = models.TextField(blank=True)
    date_creation = models.DateTimeField(auto_now_add=True)
    history = models.BooleanField(default=False)

    def __str__(self):
        return f"Demande {self.id} par {self.demandeur.username}"

class AssignmentHistory(models.Model):
    equipement = models.ForeignKey(Equipment, on_delete=models.CASCADE)
    utilisateur = models.ForeignKey(User, on_delete=models.CASCADE)
    demande = models.ForeignKey(MaterialRequest, on_delete=models.CASCADE, null=True)  # Link to request
    affecte_le = models.DateTimeField(auto_now_add=True)
    retourne_le = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"{self.equipement} affecté à {self.utilisateur.username}"
