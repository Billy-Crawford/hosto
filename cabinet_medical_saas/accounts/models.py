#accounts/models
from django.contrib.auth.models import AbstractUser
from django.conf import settings
from django.db import models
from django.utils import timezone


# USERNAME_FIELD = 'email'
# REQUIRED_FIELDS = ['username']


class CustomUser(AbstractUser):
    ROLE_CHOICES = (
        ('PATIENT', 'Patient'),
        ('MEDECIN', 'Médecin'),
        ('ADMIN', 'Admin'),
    )
    role = models.CharField(max_length=10, choices=ROLE_CHOICES, default='PATIENT')
    email = models.EmailField(unique=True)  # Important !

    USERNAME_FIELD = 'email'
    REQUIRED_FIELDS = ['username']  # On garde username comme champ requis

    def __str__(self):
        return f"{self.username} ({self.role})"



class Patient(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    date_naissance = models.DateField(null=True, blank=True)
    genre = models.CharField(max_length=10, choices=[('Homme', 'Homme'), ('Femme', 'Femme')])
    téléphone = models.CharField(max_length=20)
    adresse = models.TextField(blank=True)

    def __str__(self):
        return f"Patient: {self.user.get_full_name()}"


class Medecin(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE)
    spécialité = models.CharField(max_length=100)
    téléphone = models.CharField(max_length=20)
    horaires = models.JSONField(default=dict)  # {"lundi": "08:00-12:00", ...}

    def __str__(self):
        return f"Dr. {self.user.get_full_name()} - {self.spécialité}"

class PatientProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='patient_profile')
    age = models.IntegerField(null=True, blank=True)
    sexe = models.CharField(max_length=10, choices=[('HOMME', 'Homme'), ('FEMME', 'Femme')])
    groupe_sanguin = models.CharField(max_length=3, choices=[
        ('A+', 'A+'), ('A-', 'A-'), ('B+', 'B+'), ('B-', 'B-'),
        ('AB+', 'AB+'), ('AB-', 'AB-'), ('O+', 'O+'), ('O-', 'O-')
    ])
    adresse = models.CharField(max_length=255)

    def __str__(self):
        return f"Profil patient de {self.user.username}"

class MedecinProfile(models.Model):
    user = models.OneToOneField(settings.AUTH_USER_MODEL, on_delete=models.CASCADE, related_name='medecin_profile')
    age = models.IntegerField(null=True, blank=True)
    spécialité = models.CharField(max_length=100)
    expérience = models.TextField(blank=True)  # Description de l'expérience du médecin
    adresse = models.CharField(max_length=255)

    def __str__(self):
        return f"Profil médecin de {self.user.username}"

class RendezVous(models.Model):
    ETAT_CHOICES = [
        ('en_attente', 'En attente'),
        ('confirmé', 'Confirmé'),
        ('terminé', 'Terminé'),
        ('annulé', 'Annulé'),
    ]

    # Utilisation de 'Medecin' et 'Patient' comme modèles
    medecin = models.ForeignKey('Medecin', on_delete=models.CASCADE, related_name='rendezvous')
    patient = models.ForeignKey('Patient', on_delete=models.CASCADE, related_name='rendezvous', null=True, blank=True)
    date_heure = models.DateTimeField()
    etat = models.CharField(max_length=20, choices=ETAT_CHOICES, default='en_attente')
    motif = models.TextField(blank=True)

    created_at = models.DateTimeField(default=timezone.now)
    updated_at = models.DateTimeField(auto_now=True)  # Optionnel: pour suivre les mises à jour

    def __str__(self):
        return f"RDV {self.date_heure} avec {self.medecin.user.username}"

    # Optionnel: méthode pour vérifier si le rendez-vous est confirmé
    def est_confirme(self):
        return self.etat == 'confirmé'

    # Optionnel: méthode pour vérifier si le rendez-vous est annulé
    def est_annule(self):
        return self.etat == 'annulé'