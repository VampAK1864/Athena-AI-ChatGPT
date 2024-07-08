from django.db import models
from django.contrib.auth.models import User
from django.db import models
from django.utils import timezone


# Create your models here.

class ChatRoom(models.Model):
    chat_name = models.CharField(max_length=100)
    users = models.ManyToManyField(User)  # Many-to-Many relationship with User model

    def __str__(self):
        return self.chat_name
class Chat(models.Model):
    user = models.ForeignKey(User, on_delete=models.CASCADE)
    message = models.TextField()
    response = models.TextField()
    created_at = models.DateTimeField(default=timezone.now)
    chat_room = models.ForeignKey(ChatRoom, on_delete=models.CASCADE)

    def __str__(self):
        return f'Chat {self.id} - Room: {self.chat_room.id}, User: {self.user.username}'
