from django.shortcuts import render
from django.views.generic.base import TemplateView

# Create your views here.
class HomeView(TemplateView):
    template_name = "home/home.html"