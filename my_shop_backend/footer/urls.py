from django.urls import path
from . import views

urlpatterns = [
    path('data/', views.FooterDataView.as_view(), name='footer-data'),
]
