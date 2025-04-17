from django.contrib import admin
from .models import CustomUser, Patient, Medecin
from django.contrib.auth.admin import UserAdmin

admin.site.register(CustomUser, UserAdmin)
admin.site.register(Patient)
admin.site.register(Medecin)
