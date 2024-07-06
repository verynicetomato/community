# 상대경로: Django4/community/member/urls.py

from django.urls import path
from .views import SignupView, LogoutView, UserInfoView, UserPostsView, CustomTokenObtainPairView
from rest_framework_simplejwt.views import TokenRefreshView

app_name = 'member'

urlpatterns = [
    path('signup/', SignupView.as_view(), name='signup'),
    path('login/', CustomTokenObtainPairView.as_view(), name='login'),
    path('logout/', LogoutView.as_view(), name='logout'),
    path('info/', UserInfoView.as_view(), name='info'),
    path('post/', UserPostsView.as_view(), name='user_posts'),
    path('token/refresh/', TokenRefreshView.as_view(), name='token_refresh'),
]
