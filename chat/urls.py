from django.urls import path
from . import views

app_name = "chat"

urlpatterns = [
    path('bot/', views.ChatBotView.as_view(), name='chat'),
    # path('chat-update/<pk>', views.chat_update_view, name='chat-update'),
    path('chat-delete/<pk>', views.chat_delete_view, name="chat-delete")
]