from django.urls import path
from . import views

urlpatterns = [
    path('franchise/apply/', views.FranchiseApplyView.as_view(), name='franchise-apply'),
]
