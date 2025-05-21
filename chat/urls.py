from django.urls import path
from . import views

app_name = "chat"

urlpatterns = [
    path('bot/', views.ChatBotView.as_view(), name='chat'),
]