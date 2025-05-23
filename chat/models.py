from django.db import models
from account.models import CustomUser
import uuid

class Chat(models.Model):
    id = models.UUIDField(primary_key=True, default=uuid.uuid4, editable=False)
    user = models.ForeignKey(CustomUser, on_delete=models.CASCADE, related_name="chats")
    user_message = models.TextField()
    bot_reply = models.TextField()
    time_stamp = models.DateTimeField(auto_now_add=True)

    def save(self, *args, **kwargs):
        self.user_message = self.user_message.strip()
        self.bot_reply = self.bot_reply.strip()
        super().save(*args, **kwargs)

