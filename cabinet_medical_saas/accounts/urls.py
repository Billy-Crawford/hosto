# accounts/urls
from django.urls import path
from . import views
from .views import RegisterView, MeView, PatientProfileView, MedecinProfileView, user_profile, RendezVousDisponiblesView
from rest_framework_simplejwt.views import TokenObtainPairView, TokenRefreshView
from .views import RendezVousCreateView, RendezVousListView, RendezVousReservationView

urlpatterns = [
    path('login/', TokenObtainPairView.as_view(), name='token_obtain_pair'),
    path('refresh/', TokenRefreshView.as_view(), name='token_refresh'),
    path('register/', RegisterView.as_view(), name='register'),
    path('me/', MeView.as_view(), name='me'),

    # ✅ Point d'accès principal pour profil (dynamique selon le rôle)
    path('profile/', user_profile, name='user-profile'),

    # ✅ Endpoints spécifiques si besoin de les séparer
    path('patient-profile/', PatientProfileView.as_view(), name='patient-profile'),
    path('medecin-profile/', MedecinProfileView.as_view(), name='medecin-profile'),

    # ✅ Routes des rendez-vous
    path('rdv/create/', RendezVousCreateView.as_view(), name='create-rdv'),  # Assure-toi que la vue existe
    path('rdv/', RendezVousListView.as_view(), name='list-rdv'),
    path('rdv/reserver/<int:pk>/', RendezVousReservationView.as_view(), name='reserver-rdv'),

    path('rendezvous/disponibles/', RendezVousDisponiblesView.as_view(), name='rendezvous-disponibles'),


]
