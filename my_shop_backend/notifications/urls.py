from django.urls import path
from . import views

urlpatterns = [
    path('profile/messages/', views.NotificationListView.as_view(), name='profile-messages'),
    # read-all must come before <message_id>/read to avoid URL conflict
    path('profile/messages/read-all/', views.MarkAllNotificationsReadView.as_view(), name='profile-messages-read-all'),
    path('profile/messages/<int:message_id>/read/', views.MarkNotificationReadView.as_view(), name='profile-message-read'),
]
