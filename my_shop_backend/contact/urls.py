from django.urls import path
from . import views

urlpatterns = [
    path('contact/submit/', views.ContactSubmitView.as_view(), name='contact-submit'),
    path('contact/info/', views.ContactInfoView.as_view(), name='contact-info'),
    path('contact/slider/', views.ContactSliderView.as_view(), name='contact-slider'),
    path('contact/subjects/', views.ContactSubjectsView.as_view(), name='contact-subjects'),
    path('contact/tickets/<str:ticket_id>/', views.ContactTicketDetailView.as_view(), name='contact-ticket'),
]
