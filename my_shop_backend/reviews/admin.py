from django.contrib import admin
from .models import Comment, CommentImage, CommentVote, Question, Answer, AnswerVote


class CommentImageInline(admin.TabularInline):
    model = CommentImage
    extra = 0


@admin.register(Comment)
class CommentAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'product', 'star', 'created_at']
    list_filter = ['star']
    search_fields = ['user__username', 'text']
    inlines = [CommentImageInline]


@admin.register(CommentVote)
class CommentVoteAdmin(admin.ModelAdmin):
    list_display = ['user', 'comment', 'vote_type']


class AnswerInline(admin.TabularInline):
    model = Answer
    extra = 0


@admin.register(Question)
class QuestionAdmin(admin.ModelAdmin):
    list_display = ['id', 'user', 'product', 'created_at']
    search_fields = ['user__username', 'text']
    inlines = [AnswerInline]


@admin.register(AnswerVote)
class AnswerVoteAdmin(admin.ModelAdmin):
    list_display = ['user', 'answer', 'vote_type']
