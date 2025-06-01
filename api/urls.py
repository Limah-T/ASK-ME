from django.urls import path
from . import views

app_name = "api"
urlpatterns = [
    # Authentication routes
    path('v1/signup/', views.SignUpView.as_view()),
    path('v1/verify-email/', views.VerifyEmailView.as_view()),
    path('v1/login/', views.LoginView.as_view()),
    path('v1/verify-code/', views.VerifyOtpView.as_view()),
    path('v1/forget-password/', views.ForgetPasswordView.as_view()),
    path('v1/verify-reset-code/', views.VerifyPasswordResetToken.as_view()),
    path('v1/password-reset/', views.ResetPasswordView.as_view()),
    path('v1/change-password/', views.ChangePasswordView.as_view()),
    path('v1/logout/', views.LogoutView.as_view()),
    
    # Get new token
    path('v1/get-new-token/', views.GetNewTokenView.as_view()),

    # Chatbot Interaction routes
    path('v1/chat-question/', views.ChatCreateView.as_view()),
    path('v1/chat-history/', views.ChatListView.as_view()),
    path('v1/chat-update/', views.ChatUpdateView.as_view()),
    path('v1/chat/<pk>', views.ChatDetailView.as_view()),

]