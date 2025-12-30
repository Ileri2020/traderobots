from django.contrib import admin
from .models import Post, Comment, ChatGroup, Message

admin.site.register(Post)
admin.site.register(Comment)
admin.site.register(ChatGroup)
admin.site.register(Message)
