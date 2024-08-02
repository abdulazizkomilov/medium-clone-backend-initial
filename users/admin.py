from django.contrib import admin
from django.contrib.auth.admin import UserAdmin
from .models import CustomUser

@admin.register(CustomUser)   # administrator panelida ro'yxatdan o'tdan o'tkazish
class CustomUserAdmin(UserAdmin):  
    fieldsets = UserAdmin.fieldsets + (
        (None, {'fields': ('middle_name',)}),
    )
    list_display = ('id', 'username', 'email', 'first_name', 'last_name', 'middle_name')
    list_display_links = ('id', 'username', 'email')
    search_fields = ('username', 'email', 'first_name', 'last_name', 'middle_name')
    list_filter = ('last_login', 'date_joined', 'is_staff', 'is_superuser', 'is_active')

# admin.site.register(CustomUser, CustomUserAdmin)  # administrator panelida ro'yxatdan o'tishning yana bir usuli
