# 상대경로: Django4/community/board/urls.py

from django.urls import path
from .views import PostListView, PostDetailView, CommentListView, CommentDetailView

app_name = 'board'

urlpatterns = [
    path('', PostListView.as_view(), name='post_list'),
    path('<int:pk>/', PostDetailView.as_view(), name='post_detail'),
    path('<int:post_id>/comment/', CommentListView.as_view(), name='comment_list'),
    path('<int:post_id>/comment/<int:pk>/', CommentDetailView.as_view(), name='comment_detail'),
]
