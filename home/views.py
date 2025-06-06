from django.views.generic.base import TemplateView
from account.models import CustomUser

class HomeView(TemplateView):
    template_name = "home/home.html"