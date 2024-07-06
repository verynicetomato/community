# 상대경로: Django4/community/member/admin.py

from django.contrib import admin
from .models import CustomUser
# Register your models here.

admin.site.register(CustomUser)