from django.urls import path
from . import views

app_name = 'account'

urlpatterns = [
    path('signup/', views.SignUpView.as_view(), name='signup'),
    path('verify-email/', views.VerifyEmailViaToken.as_view(), name="verify_email"),
    path('login/', views.LoginView.as_view(), name='login'),
    path('get_code/<str:uid>/', views.VerifyOTP.as_view(), name='get_code'),
    path('logout/', views.logoutView, name='logout')
]