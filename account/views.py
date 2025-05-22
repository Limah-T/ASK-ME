from django.shortcuts import render, redirect
from django.views.generic.base import TemplateView
from django.views.generic.edit import FormView
from django.views import View
from django.urls import reverse_lazy
from django.contrib.auth import login, logout, authenticate
from .functions import send_token_for_email_verification, decode_token
from .country_names import DEFAULT_ROLE
from .models import CustomUser
from . import form

class SignUpView(FormView):
    template_name = "account/signup.html"
    form_class = form.SignupForm
    http_method_names = ["post", "get"]

    def post(self, request, *args, **kwargs):
        CustomUser.objects.all().delete()
        form_rendered = self.get_form(self.form_class)
        if form_rendered.is_valid():
            print(form_rendered.cleaned_data)
            username = form_rendered.cleaned_data.get("username")
            email = form_rendered.cleaned_data.get('email')
            country = form_rendered.cleaned_data.get("country")
            password = form_rendered.cleaned_data.get("password")
            CustomUser.objects.create_user(username=username, email=email, country=country, password=password, role=DEFAULT_ROLE)
            send_token_for_email_verification(user=email)
            return render(request, "account/email_alert.html", {'username': username})
        return super().post(request, *args, **kwargs)
    
class VerifyEmailViaToken(View):
    http_method_names = ["get"]
    def get(self, request, *args, **kwargs):
        token_input = request.GET.get('token')
        if not token_input:
            return render(request, "account/error_message.html")
        decoded_token = decode_token(token=token_input)
        if not decoded_token:
            return render(request, "account/failed_verification.html")
        email = decoded_token['sub']
        try:
            user = CustomUser.objects.get(email=email)
        except CustomUser.DoesNotExist:
            pass
        except CustomUser.MultipleObjectsReturned:
            pass
        except Exception as e:
            print(e)
            pass
        if user.email_verified and user.token_verified:
            return render(request, "account/error_message.html")
        user.email_verified = True
        user.token_verified = True
        login(request, user=user)
        return redirect(reverse_lazy("chat:chat"))