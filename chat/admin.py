from django.contrib import admin
from .models import Chat

@admin.register(Chat)
class ChatAdminInterface(admin.ModelAdmin):
    list_display = ["user", "user_message", "bot_reply", "time_stamp"]
    list_filter = ["user", "user_message"]
    search_fields = ["user", "user_message"]
