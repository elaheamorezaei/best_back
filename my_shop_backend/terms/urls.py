from django.urls import path
from . import views

urlpatterns = [
    path('terms/', views.TermListView.as_view(), name='term-list'),
    # static paths before parameterized to avoid URL conflicts
    path('terms/hero/', views.TermsHeroView.as_view(), name='terms-hero'),
    path('terms/wallet/', views.WalletTermsView.as_view(), name='terms-wallet'),
    path('terms/accept/', views.TermAcceptView.as_view(), name='terms-accept'),
    path('terms/<str:term_id>/', views.TermDetailView.as_view(), name='term-detail'),
]
