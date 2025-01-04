from django.contrib import admin
from api.models import CustomUser

# Register your models here.


@admin.register(CustomUser)
class CustomUserAdmin(admin.ModelAdmin):
    list_display = ['username', 'email', 'date_joined', 'is_staff', 'is_active']