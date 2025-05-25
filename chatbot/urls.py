from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('home/', include('home.urls')),
    path('account/', include('account.urls')),
    path('chat/', include('chat.urls')),
    path('api/', include('api.urls')),
]
