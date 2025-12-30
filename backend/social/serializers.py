from rest_framework import serializers
from .models import Post, Comment, ChatGroup, Message
from django.contrib.auth.models import User

class CommentSerializer(serializers.ModelSerializer):
    user_name = serializers.ReadOnlyField(source='user.username')
    
    class Meta:
        model = Comment
        fields = ['id', 'user', 'user_name', 'content', 'created_at']

class PostSerializer(serializers.ModelSerializer):
    user_name = serializers.ReadOnlyField(source='user.username')
    likes_count = serializers.SerializerMethodField()
    comments = CommentSerializer(many=True, read_only=True)
    
    class Meta:
        model = Post
        fields = ['id', 'user', 'user_name', 'content', 'media_urls', 'likes_count', 'comments', 'created_at']

    def get_likes_count(self, obj):
        return obj.likes.count()

class ChatGroupSerializer(serializers.ModelSerializer):
    class Meta:
        model = ChatGroup
        fields = '__all__'

class MessageSerializer(serializers.ModelSerializer):
    sender_name = serializers.ReadOnlyField(source='sender.username')
    
    class Meta:
        model = Message
        fields = ['id', 'group', 'sender', 'sender_name', 'content', 'timestamp']
