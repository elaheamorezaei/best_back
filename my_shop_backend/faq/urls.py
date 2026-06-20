from django.urls import path
from . import views

urlpatterns = [
    path('faq/categories/', views.FAQCategoryListView.as_view(), name='faq-categories'),
    path('faq/search/', views.FAQSearchView.as_view(), name='faq-search'),
    path('faq/ask/', views.FAQAskView.as_view(), name='faq-ask'),
    path('faq/', views.FAQListView.as_view(), name='faq-list'),
    path('faq/<int:faq_id>/', views.FAQDetailView.as_view(), name='faq-detail'),
    path('faq/<int:faq_id>/helpful/', views.FAQHelpfulView.as_view(), name='faq-helpful'),
]
