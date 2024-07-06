# 상대경로: Django4/community/board/admin.py

from django.contrib import admin
## from .models import Board
from .models import Post, Comment
"""
class BoardAdmin(admin.ModelAdmin):
    readonly_fields = ('date',)

admin.site.register(Board, BoardAdmin)
"""
admin.site.register(Post)
admin.site.register(Comment)
