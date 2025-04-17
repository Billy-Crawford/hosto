# accounts/views
from rest_framework import generics, status
from rest_framework.decorators import api_view, permission_classes
from rest_framework.exceptions import NotFound, PermissionDenied
from rest_framework.response import Response
from rest_framework.views import APIView
from rest_framework.permissions import AllowAny, IsAuthenticated
from .models import PatientProfile, MedecinProfile, Patient, RendezVous, Medecin
from .serializers import (
    RegisterSerializer,
    PatientProfileSerializer,
    MedecinProfileSerializer, RendezVousSerializer,
)


class RegisterView(generics.CreateAPIView):
    serializer_class = RegisterSerializer
    permission_classes = [AllowAny]


class MeView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request):
        user = request.user
        return Response({
            "id": user.id,
            "username": user.username,
            "email": user.email,
            "role": user.role
        })


@api_view(['GET'])
@permission_classes([IsAuthenticated])
def user_profile(request):
    user = request.user
    if user.role == 'PATIENT':
        try:
            profile = PatientProfile.objects.get(user=user)
            serializer = PatientProfileSerializer(profile)
        except PatientProfile.DoesNotExist:
            return Response({"detail": "Profile not found."}, status=404)
    elif user.role == 'MEDECIN':
        try:
            profile = MedecinProfile.objects.get(user=user)
            serializer = MedecinProfileSerializer(profile)
        except MedecinProfile.DoesNotExist:
            return Response({"detail": "Profile not found."}, status=404)
    else:
        return Response({"detail": "Profile not found."}, status=404)

    return Response(serializer.data)



class PatientProfileView(APIView):
    permission_classes = [IsAuthenticated]

    def get(self, request, *args, **kwargs):
        """Récupérer le profil patient."""
        try:
            profile = PatientProfile.objects.get(user=request.user)
            serializer = PatientProfileSerializer(profile)
            return Response(serializer.data, status=status.HTTP_200_OK)
        except PatientProfile.DoesNotExist:
            raise NotFound("Le profil patient n'existe pas.")

    def patch(self, request, *args, **kwargs):
        """Mettre à jour partiellement le profil patient."""
        try:
            profile = PatientProfile.objects.get(user=request.user)
        except PatientProfile.DoesNotExist:
            raise NotFound("Le profil patient n'existe pas.")

        # Serializer avec les données reçues et autorisation d'une mise à jour partielle
        serializer = PatientProfileSerializer(profile, data=request.data, partial=True)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_200_OK)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
class MedecinProfileView(generics.RetrieveUpdateAPIView):
    serializer_class = MedecinProfileSerializer
    permission_classes = [IsAuthenticated]

    def get_object(self):
        try:
            return MedecinProfile.objects.get(user=self.request.user)
        except MedecinProfile.DoesNotExist:
            raise NotFound("Le profil médecin n'existe pas.")

class RendezVousCreateView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request):
        user = request.user

        # Vérifie que l'utilisateur est bien un médecin enregistré
        try:
            medecin = Medecin.objects.get(user=user)
        except Medecin.DoesNotExist:
            return Response({"error": "Seul un médecin peut créer un rendez-vous."}, status=status.HTTP_403_FORBIDDEN)

        data = request.data.copy()
        data['medecin'] = medecin.id

        serializer = RendezVousSerializer(data=data)
        if serializer.is_valid():
            serializer.save()
            return Response(serializer.data, status=status.HTTP_201_CREATED)

        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

class RendezVousListView(generics.ListAPIView):
    serializer_class = RendezVousSerializer
    permission_classes = [IsAuthenticated]

    def get_queryset(self):
        user = self.request.user
        if user.role == 'PATIENT':
            return RendezVous.objects.filter(patient__user=user)
        elif user.role == 'MEDECIN':
            return RendezVous.objects.filter(medecin__user=user)
        else:
            return RendezVous.objects.none()


class RendezVousReservationView(APIView):
    permission_classes = [IsAuthenticated]

    def post(self, request, pk):
        # Patient prend rendez-vous sur un créneau
        if request.user.role != 'PATIENT':
            raise PermissionDenied("Seuls les patients peuvent réserver un rendez-vous.")

        try:
            rdv = RendezVous.objects.get(pk=pk, patient__isnull=True)
        except RendezVous.DoesNotExist:
            raise NotFound("Créneau non disponible.")

        patient = Patient.objects.get(user=request.user)
        rdv.patient = patient
        rdv.etat = 'en_attente'
        rdv.save()

        return Response(RendezVousSerializer(rdv).data, status=status.HTTP_200_OK)


class RendezVousDisponiblesView(generics.ListAPIView):
    serializer_class = RendezVousSerializer
    permission_classes = [IsAuthenticated]
    pagination_class = None  # Optionnel : ajoute une pagination si tu en veux

    def get_queryset(self):
        user = self.request.user

        if user.role != 'PATIENT':
            raise PermissionDenied("Seuls les patients peuvent voir les créneaux disponibles.")

        return RendezVous.objects.filter(
            patient__isnull=True
        ).order_by('date', 'heure')
