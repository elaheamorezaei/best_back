from django.urls import path
from . import views

urlpatterns = [
    path('about/', views.AboutPageView.as_view(), name='about'),
    path('about/slider/', views.AboutSliderView.as_view(), name='about-slider'),
    path('about/story/', views.AboutStoryView.as_view(), name='about-story'),
    path('about/why-us/', views.AboutWhyUsView.as_view(), name='about-why-us'),
    path('about/branches/', views.AboutBranchesView.as_view(), name='about-branches'),
    path('about/description/', views.AboutDescriptionView.as_view(), name='about-description'),
    path('about/team/', views.AboutTeamView.as_view(), name='about-team'),
    path('about/stats/', views.AboutStatsView.as_view(), name='about-stats'),
]
