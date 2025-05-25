from django.urls import path
from . import views

app_name = "api"
urlpatterns = [
    path('v1/signup/', views.SignUpView.as_view()),
    path('v1/verify-email/', views.VerifyEmailView.as_view()),
    
]