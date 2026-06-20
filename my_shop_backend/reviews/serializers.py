from rest_framework import serializers
from core.responses import build_absolute_image_url
from core.utils import to_persian_date
from .models import Comment, CommentVote, Question, Answer, AnswerVote


class CommentSerializer(serializers.ModelSerializer):
    userName = serializers.SerializerMethodField()
    date = serializers.SerializerMethodField()
    images = serializers.SerializerMethodField()
    likes = serializers.SerializerMethodField()
    dislikes = serializers.SerializerMethodField()
    userVote = serializers.SerializerMethodField()

    class Meta:
        model = Comment
        fields = ['id', 'userName', 'star', 'text', 'date', 'likes', 'dislikes', 'userVote', 'images']

    def get_userName(self, obj):
        return obj.user.get_full_name() or obj.user.username

    def get_date(self, obj):
        return to_persian_date(obj.created_at)

    def get_images(self, obj):
        request = self.context.get('request')
        return [build_absolute_image_url(request, img.image) for img in obj.images.all()]

    def get_likes(self, obj):
        return sum(1 for v in obj.votes.all() if v.vote_type == CommentVote.LIKE)

    def get_dislikes(self, obj):
        return sum(1 for v in obj.votes.all() if v.vote_type == CommentVote.DISLIKE)

    def get_userVote(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            vote = next((v for v in obj.votes.all() if v.user_id == request.user.id), None)
            return vote.vote_type if vote else None
        return None


class CommentCreateSerializer(serializers.ModelSerializer):
    star = serializers.IntegerField(min_value=1, max_value=5)
    text = serializers.CharField(min_length=10, max_length=2000)

    class Meta:
        model = Comment
        fields = ['star', 'text']


class AnswerSerializer(serializers.ModelSerializer):
    userName = serializers.SerializerMethodField()
    date = serializers.SerializerMethodField()
    likes = serializers.SerializerMethodField()
    dislikes = serializers.SerializerMethodField()
    userVote = serializers.SerializerMethodField()

    class Meta:
        model = Answer
        fields = ['id', 'userName', 'date', 'text', 'likes', 'dislikes', 'userVote']

    def get_userName(self, obj):
        return obj.user.get_full_name() or obj.user.username

    def get_date(self, obj):
        return to_persian_date(obj.created_at)

    def get_likes(self, obj):
        return sum(1 for v in obj.votes.all() if v.vote_type == AnswerVote.LIKE)

    def get_dislikes(self, obj):
        return sum(1 for v in obj.votes.all() if v.vote_type == AnswerVote.DISLIKE)

    def get_userVote(self, obj):
        request = self.context.get('request')
        if request and request.user.is_authenticated:
            vote = next((v for v in obj.votes.all() if v.user_id == request.user.id), None)
            return vote.vote_type if vote else None
        return None


class QuestionSerializer(serializers.ModelSerializer):
    date = serializers.SerializerMethodField()
    answerCount = serializers.SerializerMethodField()
    answers = serializers.SerializerMethodField()

    class Meta:
        model = Question
        fields = ['id', 'text', 'date', 'answerCount', 'answers']

    def get_date(self, obj):
        return to_persian_date(obj.created_at)

    def get_answerCount(self, obj):
        return len(obj.answers.all())

    def get_answers(self, obj):
        first_two = list(obj.answers.all())[:2]
        return AnswerSerializer(first_two, many=True, context=self.context).data


class QuestionCreateSerializer(serializers.ModelSerializer):
    text = serializers.CharField(min_length=10, max_length=500)

    class Meta:
        model = Question
        fields = ['text']


class AnswerCreateSerializer(serializers.ModelSerializer):
    text = serializers.CharField(min_length=5, max_length=1000)

    class Meta:
        model = Answer
        fields = ['text']
