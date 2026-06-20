from django.db import models
from django.conf import settings


class Comment(models.Model):
    product = models.ForeignKey(
        'products.Product', related_name='comments', on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='comments', on_delete=models.CASCADE
    )
    star = models.PositiveSmallIntegerField(default=5)
    title = models.CharField(max_length=300, blank=True)
    text = models.TextField()
    pros = models.JSONField(default=list, blank=True)
    cons = models.JSONField(default=list, blank=True)
    is_approved = models.BooleanField(default=False)
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Comment by {self.user} on {self.product}"


class CommentImage(models.Model):
    comment = models.ForeignKey(Comment, related_name='images', on_delete=models.CASCADE)
    image = models.ImageField(upload_to='comments/')

    def __str__(self):
        return f"Image for comment {self.comment_id}"


class CommentVote(models.Model):
    LIKE = 'like'
    DISLIKE = 'dislike'
    VOTE_CHOICES = [(LIKE, 'Like'), (DISLIKE, 'Dislike')]

    comment = models.ForeignKey(Comment, related_name='votes', on_delete=models.CASCADE)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='comment_votes', on_delete=models.CASCADE
    )
    vote_type = models.CharField(max_length=10, choices=VOTE_CHOICES)

    class Meta:
        unique_together = ('comment', 'user')

    def __str__(self):
        return f"{self.user} {self.vote_type} comment {self.comment_id}"


class Question(models.Model):
    product = models.ForeignKey(
        'products.Product', related_name='questions', on_delete=models.CASCADE
    )
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='questions', on_delete=models.CASCADE
    )
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['-created_at']

    def __str__(self):
        return f"Question by {self.user} on {self.product}"


class Answer(models.Model):
    question = models.ForeignKey(Question, related_name='answers', on_delete=models.CASCADE)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='answers', on_delete=models.CASCADE
    )
    text = models.TextField()
    created_at = models.DateTimeField(auto_now_add=True)

    class Meta:
        ordering = ['created_at']

    def __str__(self):
        return f"Answer by {self.user} on question {self.question_id}"


class AnswerVote(models.Model):
    LIKE = 'like'
    DISLIKE = 'dislike'
    VOTE_CHOICES = [(LIKE, 'Like'), (DISLIKE, 'Dislike')]

    answer = models.ForeignKey(Answer, related_name='votes', on_delete=models.CASCADE)
    user = models.ForeignKey(
        settings.AUTH_USER_MODEL, related_name='answer_votes', on_delete=models.CASCADE
    )
    vote_type = models.CharField(max_length=10, choices=VOTE_CHOICES)

    class Meta:
        unique_together = ('answer', 'user')

    def __str__(self):
        return f"{self.user} {self.vote_type} answer {self.answer_id}"
