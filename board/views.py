"""
from django.shortcuts import render
from .models import Board
from .serializers import BoardSerializer
## from rest_framework.decorators import api_view
from rest_framework.response import Response
from rest_framework import status
from rest_framework_simplejwt.authentication import JWTAuthentication
from rest_framework.permissions import IsAuthenticatedOrReadOnly

from rest_framework.decorators import api_view, authentication_classes, permission_classes
from .permissions import IsOwnerOrReadOnly
from rest_framework.views import APIView
from django.shortcuts import get_object_or_404
from rest_framework.generics import ListCreateAPIView
from rest_framework.generics import RetrieveUpdateDestroyAPIView
"""
'''
전체 블로그를 조회
'''
"""
@api_view(['GET', 'POST'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsAuthenticatedOrReadOnly])
def board_list(request):
	if request.method == 'GET':
		boards = Board.objects.all()
		serializer = BoardSerializer(boards, many=True)
		return Response(serializer.data, status=status.HTTP_200_OK)
	elif request.method == 'POST':
		serializer = BoardSerializer(data=request.data)
		if serializer.is_valid():
			serializer.save()
			return Response(serializer.data, status = status.HTTP_201_CREATED)
	return Response(status=status.HTTP_400_BAD_REQUEST)
"""
"""
class BoardList(APIView):
authentication_classes = [JWTAuthentication]
permission_classes = [IsAuthenticatedOrReadOnly]
def get(self, request):
    boards = Board.objects.all()
    serializer = BoardSerializer(boards, many=True)
    return Response(serializer.data)

def post(self, request):
    serializer = BoardSerializer(data=request.data)
    if serializer.is_valid(raise_exception=True):
        serializer.save(user=request.user)
        return Response(serializer.data, status=status.HTTP_201_CREATED)
    return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)
"""
""""
class BoardList(ListCreateAPIView):
    queryset = Board.objects.all()
    serializer_class = BoardSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsAuthenticatedOrReadOnly]
		
    def perform_create(self, serializer):
        user = self.request.user
        serializer.save(user = user)
"""
'''
한 블로그 조회
'''
"""
@api_view(['GET', 'PUT', 'DELETE'])
@authentication_classes([JWTAuthentication])
@permission_classes([IsOwnerOrReadOnly])
def board_detail(request, pk):
    try:
        board = Board.objects.get(pk=pk)
        if request.method == 'GET':
            serializer = BoardSerializer(board)
            return Response(serializer.data, status=status.HTTP_200_OK)
        elif request.method == 'PUT':
            serializer = BoardSerializer(board, data=request.data)
            if serializer.is_valid():
                serializer.save()
                return Response(status=status.HTTP_200_OK)
            return Response(status=status.HTTP_400_BAD_REQUEST)
        elif request.method == 'DELETE':
            board.delete()
            return Response(status=status.HTTP_204_NO_CONTENT)
    except Board.DoesNotExist:
        return Response(status=status.HTTP_404_NOT_FOUND)
"""
"""
class BoardDetail(APIView):
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsOwnerOrReadOnly]
    def get_object(self, pk):
        board = get_object_or_404(Board, pk=pk)
        return board

    def get(self, request, pk):
        board = self.get_object(pk)
        serializer = BoardSerializer(board)
        return Response(serializer.data)

    def put(self, request, pk):
        board = self.get_object(pk)
        serializer = BoardSerializer(board, data=request.data)
        if serializer.is_valid(raise_exception=True):
            serializer.save()
            return Response(serializer.data)
        return Response(serializer.errors, status=status.HTTP_400_BAD_REQUEST)

    def delete(self, request, pk):
        board = self.get_object(pk)
        board.delete()
        return Response(status=status.HTTP_204_NO_CONTENT)
"""
"""
class BoardDetail(RetrieveUpdateDestroyAPIView):
    queryset = Board.objects.all()
    serializer_class = BoardSerializer
    authentication_classes = [JWTAuthentication]
    permission_classes = [IsOwnerOrReadOnly]
"""
# 상대경로: Django4/community/board/views.py

from rest_framework import generics, permissions, status
from rest_framework.response import Response
from .models import Post, Comment
from .serializers import PostSerializer, CommentSerializer
from rest_framework.permissions import IsAuthenticated, AllowAny
from .permissions import IsOwnerOrReadOnly

class PostListView(generics.ListCreateAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated()]

    def perform_create(self, serializer):
        serializer.save(user=self.request.user)

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        response_data = serializer.data
        response_data["comments"] = []
        return Response(response_data, status=status.HTTP_201_CREATED)

    def list(self, request, *args, **kwargs):
        queryset = self.get_queryset()
        serializer = self.get_serializer(queryset, many=True)
        response_data = [
            {
                "id": post["id"],
                "user": post["user"],
                "nickname": post["nickname"],
                "title": post["title"],
                "created_at": post["created_at"]
            }
            for post in serializer.data
        ]
        return Response(response_data)

class PostDetailView(generics.RetrieveUpdateDestroyAPIView):
    queryset = Post.objects.all()
    serializer_class = PostSerializer
    lookup_field = 'pk'

    def get_permissions(self):
        if self.request.method == 'GET':
            return [permissions.AllowAny()]
        return [permissions.IsAuthenticated(), IsOwnerOrReadOnly()]

    def perform_update(self, serializer):
        serializer.save(user=self.request.user)

    def retrieve(self, request, *args, **kwargs):
        instance = self.get_object()
        serializer = self.get_serializer(instance)
        response_data = serializer.data
        response_data["comments"] = [
            {
                "id": comment.id,
                "user": comment.user.id,
                "nickname": comment.user.profile.nickname,
                "comment": comment.comment,
                "created_at": comment.created_at.strftime("%Y-%m-%d")
            }
            for comment in instance.comments.all()
        ]
        return Response(response_data)

    def update(self, request, *args, **kwargs):
        partial = kwargs.pop('partial', False)
        instance = self.get_object()
        serializer = self.get_serializer(instance, data=request.data, partial=partial)
        serializer.is_valid(raise_exception=True)
        self.perform_update(serializer)
        post = self.get_object()
        response_data = {
            "id": post.id,
            "user": post.user.id,
            "nickname": post.user.profile.nickname,
            "title": post.title,
            "body": post.body,
            "created_at": post.created_at.strftime("%Y-%m-%d"),
            "comments": [
                {
                    "id": comment.id,
                    "user": comment.user.id,
                    "nickname": comment.user.profile.nickname,
                    "comment": comment.comment,
                    "created_at": comment.created_at.strftime("%Y-%m-%d"),
                }
                for comment in post.comments.all()
            ]
        }
        return Response(response_data, status=status.HTTP_200_OK)

class CommentListView(generics.ListCreateAPIView):
    serializer_class = CommentSerializer
    permission_classes = [AllowAny]

    def get_queryset(self):
        return Comment.objects.filter(post_id=self.kwargs['post_id'])

    def perform_create(self, serializer):
        serializer.save(user=self.request.user, post_id=self.kwargs['post_id'])

    def create(self, request, *args, **kwargs):
        serializer = self.get_serializer(data=request.data)
        serializer.is_valid(raise_exception=True)
        self.perform_create(serializer)
        post = Post.objects.get(pk=self.kwargs['post_id'])
        response_data = {
            "id": post.id,
            "user": post.user.id,
            "nickname": post.user.profile.nickname,
            "title": post.title,
            "body": post.body,
            "created_at": post.created_at.strftime("%Y-%m-%d"),
            "comments": [
                {
                    "id": comment.id,
                    "user": comment.user.id,
                    "nickname": comment.user.profile.nickname,
                    "comment": comment.comment,
                    "created_at": comment.created_at.strftime("%Y-%m-%d"),
                }
                for comment in post.comments.all()
            ]
        }
        return Response(response_data, status=status.HTTP_201_CREATED)

class CommentDetailView(generics.RetrieveDestroyAPIView):
    queryset = Comment.objects.all()
    serializer_class = CommentSerializer
    permission_classes = [IsAuthenticated, IsOwnerOrReadOnly]

    def get_queryset(self):
        return super().get_queryset().filter(post_id=self.kwargs['post_id'])

    def delete(self, request, *args, **kwargs):
        instance = self.get_object()
        self.perform_destroy(instance)
        post = Post.objects.get(pk=self.kwargs['post_id'])
        response_data = {
            "id": post.id,
            "user": post.user.id,
            "nickname": post.user.profile.nickname,
            "title": post.title,
            "body": post.body,
            "created_at": post.created_at.strftime("%Y-%m-%d"),
            "comments": [
                {
                    "id": comment.id,
                    "user": comment.user.id,
                    "nickname": comment.user.profile.nickname,
                    "comment": comment.comment,
                    "created_at": comment.created_at.strftime("%Y-%m-%d"),
                }
                for comment in post.comments.all()
            ]
        }
        return Response(response_data, status=status.HTTP_200_OK)
