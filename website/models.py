from django.db import models
from django.contrib.auth.models import User
from django.utils import timezone

class Equipment(models.Model):
    cab_number = models.CharField(max_length=50, unique=True)
    designation = models.CharField(max_length=200)
    type = models.CharField(max_length=100)
    sous_type = models.CharField(max_length=100)
    year = models.IntegerField()
    emplacement = models.CharField(max_length=200)
    affecte = models.BooleanField(default=False)
    quantity = models.PositiveIntegerField(default=1)

    def __str__(self):
        return f"{self.designation} ({self.cab_number})"

class Affectation(models.Model):
    date_affectation = models.DateTimeField(default=timezone.now)
    equipement = models.ForeignKey(Equipment, on_delete=models.CASCADE)
    fonctionnaire = models.ForeignKey(User, on_delete=models.CASCADE)
    service = models.CharField(max_length=100)
    quantity = models.PositiveIntegerField(default=1)  # New field for quantity
    date_retour = models.DateTimeField(null=True, blank=True)

    def __str__(self):
        return f"Affectation {self.equipement} à {self.fonctionnaire}"

class DemandeEquipement(models.Model):
    ETAT_CHOICES = [
        ('En attente', 'En attente'),
        ('Validée', 'Validée'),
        ('Refusée', 'Refusée'),
    ]
    objet = models.CharField(max_length=200)
    equipements = models.ManyToManyField(Equipment)
    quantity = models.PositiveIntegerField()
    motif = models.TextField()
    service = models.CharField(max_length=100)
    etat = models.CharField(max_length=20, choices=ETAT_CHOICES, default='En attente')
    demandeur = models.ForeignKey(User, on_delete=models.CASCADE)
    date_creation = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Demande {self.id} par {self.demandeur}"

class DemandeIntervention(models.Model):
    date = models.DateTimeField(default=timezone.now)
    service = models.CharField(max_length=100)
    poste = models.CharField(max_length=100)
    description = models.TextField()
    demandeur = models.ForeignKey(User, on_delete=models.CASCADE)

    def __str__(self):
        return f"Intervention {self.id} par {self.demandeur}"

class Notification(models.Model):
    message = models.TextField()
    personne = models.ForeignKey(User, on_delete=models.CASCADE)
    read = models.BooleanField(default=False)
    date = models.DateTimeField(auto_now_add=True)

    def __str__(self):
        return f"Notification: {self.message}"
