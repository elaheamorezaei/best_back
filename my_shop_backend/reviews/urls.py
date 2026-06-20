from django.urls import path
from . import views

urlpatterns = [
    path('products/<int:product_id>/comments/', views.CommentsView.as_view(), name='product-comments'),
    path('products/<int:product_id>/questions/', views.QuestionsView.as_view(), name='product-questions'),
    path('comments/<int:pk>/helpful/', views.CommentHelpfulView.as_view(), name='comment-helpful'),
    path('questions/<int:pk>/answers/', views.AnswersView.as_view(), name='question-answers'),
    path('answers/<int:pk>/helpful/', views.AnswerHelpfulView.as_view(), name='answer-helpful'),
]
