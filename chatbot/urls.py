from django.contrib import admin
from django.urls import path, include
from account import views
from django.contrib.auth.decorators import user_passes_test

# Decorator to allow only superusers to access admin
admin.site.login = user_passes_test(lambda u: u.is_superuser)(admin.site.login)


urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('home.urls')),
    path('account/', include('account.urls')),
    path('chat/', include('chat.urls')),
    path('api/', include('api.urls')),
]

handler404 = 'api.views.customexceptionhandler'

