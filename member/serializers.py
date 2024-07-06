"""
from dj_rest_auth.registration.serializers import RegisterSerializer
from allauth.account.adapter import get_adapter
from rest_framework import serializers
from .models import CustomUser

class CustomRegisterSerializer(RegisterSerializer):
    nickname = serializers.CharField(max_length=100)
    university = serializers.CharField(max_length=50)
    location = serializers.CharField(max_length=200)
    
    def get_cleaned_data(self):
        super(CustomRegisterSerializer, self).get_cleaned_data()
        return {
            'username': self.validated_data.get('username', ''),
            'password1': self.validated_data.get('password1', ''),
            'password2': self.validated_data.get('password2', ''),
            'nickname': self.validated_data.get('nickname', ''),
            'university': self.validated_data.get('university', ''),
            'location': self.validated_data.get('location', ''),
        }
    
    def save(self, request):
        adapter = get_adapter()
        user = adapter.new_user(request)
        self.cleaned_data = self.get_cleaned_data()
        user.username = self.cleaned_data.get('username')
        user.nickname = self.cleaned_data.get('nickname')
        user.university = self.cleaned_data.get('university')
        user.location = self.cleaned_data.get('location')
        user.save()
        adapter.save_user(request, user, self)
        return user

class CustomUserDetailSerializer(serializers.ModelSerializer):
    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'password', 'nickname', 'university', 'location']
"""

# 상대경로: Django4/community/member/serializers.py

from rest_framework import serializers
from .models import UserProfile, CustomUser
from django.contrib.auth.password_validation import validate_password
from rest_framework_simplejwt.tokens import RefreshToken
from rest_framework_simplejwt.serializers import TokenObtainPairSerializer

class UserProfileSerializer(serializers.ModelSerializer):
    class Meta:
        model = UserProfile
        fields = ['nickname', 'university']

class UserSerializer(serializers.ModelSerializer):
    profile = UserProfileSerializer()

    class Meta:
        model = CustomUser
        fields = ['id', 'username', 'password', 'profile']
        extra_kwargs = {
            'password': {'write_only': True}
        }

    def create(self, validated_data):
        profile_data = validated_data.pop('profile')
        password = validated_data.pop('password')
        user = CustomUser.objects.create(**validated_data)
        user.set_password(password)
        user.save()
        UserProfile.objects.create(user=user, **profile_data)
        return user

    def update(self, instance, validated_data):
        profile_data = validated_data.pop('profile')
        instance.username = validated_data.get('username', instance.username)
        if 'password' in validated_data:
            instance.set_password(validated_data['password'])
        instance.save()

        profile = instance.profile
        profile.nickname = profile_data.get('nickname', profile.nickname)
        profile.university = profile_data.get('university', profile.university)
        profile.save()

        return instance

class SignupSerializer(serializers.Serializer):
    username = serializers.CharField()
    password1 = serializers.CharField(write_only=True, validators=[validate_password])
    password2 = serializers.CharField(write_only=True)
    nickname = serializers.CharField()
    university = serializers.CharField()

    def validate(self, data):
        if data['password1'] != data['password2']:
            raise serializers.ValidationError("Passwords do not match.")
        if CustomUser.objects.filter(username=data['username']).exists():
            raise serializers.ValidationError("This username is already taken.")
        return data

    def create(self, validated_data):
        user_data = {
            'username': validated_data['username'],
            'password': validated_data['password1'],
        }
        profile_data = {
            'nickname': validated_data['nickname'],
            'university': validated_data['university'],
        }
        user = CustomUser.objects.create(username=user_data['username'])
        user.set_password(user_data['password'])
        user.save()
        UserProfile.objects.create(user=user, **profile_data)
        refresh = RefreshToken.for_user(user)
        return {
            'access': str(refresh.access_token),
            'refresh': str(refresh),
            'user': {
                'id': user.id,
                'username': user.username,
                'password': user.password,
                'nickname': profile_data['nickname'],
                'university': profile_data['university'],
            }
        }

class CustomTokenObtainPairSerializer(TokenObtainPairSerializer):

    def validate(self, attrs):
        data = super().validate(attrs)
        
        refresh = self.get_token(self.user)

        data['refresh'] = str(refresh)
        data['access'] = str(refresh.access_token)
        
        data['user'] = {
            'id': self.user.id,
            'username': self.user.username,
            'password': self.user.password,
            'nickname': self.user.profile.nickname,
            'university': self.user.profile.university
        }
        
        return data
