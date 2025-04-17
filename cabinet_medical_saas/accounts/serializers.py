# accounts/serializers

from rest_framework import serializers
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.tokens import RefreshToken
from .models import CustomUser, Patient, Medecin, PatientProfile, MedecinProfile, RendezVous
from rest_framework.exceptions import ValidationError


class RegisterSerializer(serializers.ModelSerializer):
    role = serializers.ChoiceField(choices=CustomUser.ROLE_CHOICES)
    password = serializers.CharField(write_only=True, required=True, validators=[validate_password])

    class Meta:
        model = CustomUser
        fields = ('username', 'email', 'password', 'role')

    def create(self, validated_data):
        # Récupérer le rôle de l'utilisateur
        role = validated_data.pop('role').upper()

        # Création de l'utilisateur
        user = CustomUser.objects.create_user(**validated_data, role=role)

        # Création du profil en fonction du rôle
        if role == 'PATIENT':
            # Créer un Patient et un PatientProfile
            patient = Patient.objects.create(user=user)
            PatientProfile.objects.create(user=user)

        elif role == 'MEDECIN':
            # Créer un Médecin et un MedecinProfile
            medecin = Medecin.objects.create(user=user, spécialité="Généraliste", téléphone="")
            MedecinProfile.objects.create(user=user)

        return user

    def to_representation(self, instance):
        # Générez les tokens JWT pour l'utilisateur
        refresh = RefreshToken.for_user(instance)
        return {
            'refresh': str(refresh),
            'access': str(refresh.access_token),
            'user': {
                'id': instance.id,
                'username': instance.username,
                'email': instance.email,
                'role': instance.role
            }
        }


class PatientProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = PatientProfile
        fields = ['user', 'age']

    def create(self, validated_data):
        # Valider si l'âge est fourni pour un patient
        age = validated_data.get('age')
        if age is None:
            raise ValidationError({"age": "Ce champ est requis."})

        return PatientProfile.objects.create(**validated_data)


class UserSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'email', 'role']


class MedecinProfileSerializer(serializers.ModelSerializer):
    user = UserSerializer(read_only=True)

    class Meta:
        model = MedecinProfile
        fields = '__all__'
        read_only_fields = ['user', 'medecin']

class RendezVousSerializer(serializers.ModelSerializer):
    medecin_nom = serializers.SerializerMethodField()

    class Meta:
        model = RendezVous
        fields = '__all__'
        read_only_fields = ['etat', 'created_at']

    def get_medecin_nom(self, obj):
        return f"{obj.medecin.user.first_name} {obj.medecin.user.last_name}" if obj.medecin else None
