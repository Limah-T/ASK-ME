from django.urls import path
from . import views

app_name = 'account'

urlpatterns = [
    path('home/', views.HomeView.as_view(), name='home'),
    path('signup/', views.SignUpView.as_view(), name='signup'),

    path('verify-email/', views.VerifyEmailViaToken.as_view(), name="verify_email")
]