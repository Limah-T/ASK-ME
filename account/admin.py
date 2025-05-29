from django.contrib import admin
from .models import CustomUser

@admin.register(CustomUser)
class ChatAdminInterface(admin.ModelAdmin):
    list_display = ["username", "email", "country", "role", "email_verified"]
    list_filter = ["username", "country", "email_verified"]
    search_fields = ["email_verfied", "username", "email", "country"]