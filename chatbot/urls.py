from django.contrib import admin
from django.urls import path, include
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

handler404 = 'api.views.custom_exception_handler_404'
handler403 = 'api.views.custom_exception_handler_403'
handler500 = 'api.views.custom_exception_handler_500'
