from django.urls import path
from . import views

app_name = 'account'

urlpatterns = [
    path('signup/', views.SignUpView.as_view(), name='signup'),
    path('verify-email/', views.VerifyEmailViaToken.as_view(), name="verify_email"),
    path('login/', views.LoginView.as_view(), name='login'),
    path('get_code/<str:uid>/', views.VerifyOTP.as_view(), name='get_code'),
    path('forget_password/', views.ForgetPasswordView.as_view(), name='forget_password'),
    path('password-reset', views.verify_password_reset_link),
    path('reset_password/<uuid:uid>/', views.ResetPasswordView.as_view(), name='reset_password'),
    path('change_password/', views.ChangePasswordView.as_view(), name='change_password'),
    path('logout/', views.logoutView, name='logout')
]