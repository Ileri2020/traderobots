from rest_framework import viewsets, permissions, status
from rest_framework.decorators import action
from rest_framework.response import Response
from .models import Post, Comment, ChatGroup, Message
from .serializers import PostSerializer, CommentSerializer, ChatGroupSerializer, MessageSerializer

class PostViewSet(viewsets.ModelViewSet):
    queryset = Post.objects.all().order_by('-created_at')
    serializer_class = PostSerializer
    permission_classes = [permissions.IsAuthenticatedOrReadOnly]

    def perform_create(self, serializer):
        print(f"DEBUG: User {self.request.user.username} is creating a new post")
        serializer.save(user=self.request.user)
        print(f"DEBUG: New post created by {self.request.user.username}")
    
    @action(detail=True, methods=['post'], permission_classes=[permissions.IsAuthenticated])
    def like(self, request, pk=None):
         post = self.get_object()
         print(f"DEBUG: User {request.user.username} is attempting to toggle like on post {post.id}")
         if request.user in post.likes.all():
             post.likes.remove(request.user)
             print(f"DEBUG: User {request.user.username} unliked post {post.id}")
             return Response({'status': 'unliked'}, status=status.HTTP_200_OK)
         else:
             post.likes.add(request.user)
             print(f"DEBUG: User {request.user.username} liked post {post.id}")
             return Response({'status': 'liked'}, status=status.HTTP_200_OK)

    @action(detail=False, methods=['post'], url_path='comment')
    def create_comment(self, request):
        post_id = request.data.get('post')
        content = request.data.get('content')
        print(f"DEBUG: User {request.user.username} is attempting to comment on post {post_id}")
        if not post_id or not content:
            return Response({'error': 'Post ID and content required'}, status=status.HTTP_400_BAD_REQUEST)
        
        try:
            post = Post.objects.get(id=post_id)
            comment = Comment.objects.create(post=post, user=request.user, content=content)
            print(f"DEBUG: User {request.user.username} successfully added a comment to post {post_id}")
            return Response(CommentSerializer(comment).data, status=status.HTTP_201_CREATED)
        except Post.DoesNotExist:
            print(f"DEBUG: Comment failed: Post {post_id} does not exist")
            return Response({'error': 'Post not found'}, status=status.HTTP_404_NOT_FOUND)

class ChatGroupViewSet(viewsets.ModelViewSet):
    queryset = ChatGroup.objects.all()
    serializer_class = ChatGroupSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        print(f"DEBUG: User {self.request.user.username} is creating a new chat group")
        group = serializer.save()
        group.admins.add(self.request.user)
        group.members.add(self.request.user)
        print(f"DEBUG: New chat group '{group.name}' created by {self.request.user.username}")

    @action(detail=True, methods=['post'])
    def join(self, request, pk=None):
        group = self.get_object()
        print(f"DEBUG: User {request.user.username} is joining group {group.name}")
        group.members.add(request.user)
        return Response({'status': 'joined'}, status=status.HTTP_200_OK)

class MessageViewSet(viewsets.ModelViewSet):
    queryset = Message.objects.all()
    serializer_class = MessageSerializer
    permission_classes = [permissions.IsAuthenticated]

    def perform_create(self, serializer):
        print(f"DEBUG: User {self.request.user.username} is sending a message to group {self.request.data.get('group')}")
        serializer.save(sender=self.request.user)
        print(f"DEBUG: Message successfully sent by {self.request.user.username}")

    def get_queryset(self):
        group_id = self.request.query_params.get('group_id')
        if group_id:
            return self.queryset.filter(group_id=group_id)
        return self.queryset
