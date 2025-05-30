from django.contrib import admin
from django.urls import path, include

urlpatterns = [
    path('admin/', admin.site.urls),
    path('', include('home.urls')),
    path('account/', include('account.urls')),
    path('chat/', include('chat.urls')),
    path('api/', include('api.urls')),
]

handler404 = 'api.views.customexceptionhandler'

