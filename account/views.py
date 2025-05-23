from django.shortcuts import render, redirect
from django.views.generic.edit import FormView
from django.views import View
from django.urls import reverse_lazy
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.utils import timezone
from .functions import send_token_for_email_verification, decode_token
from .country_names import DEFAULT_ROLE
from .models import CustomUser, EmailOTP
from . import form

class SignUpView(FormView):
    template_name = "account/signup.html"
    form_class = form.SignupForm
    http_method_names = ["post", "get"]

    def post(self, request, *args, **kwargs):
        # CustomUser.objects.all().delete()
        form_rendered = self.get_form(self.form_class)
        if form_rendered.is_valid():
            print(form_rendered.cleaned_data)
            username = form_rendered.cleaned_data.get("username")
            email = form_rendered.cleaned_data.get('email')
            user = form_rendered.save(commit=False)
            user.role = DEFAULT_ROLE
            user.save()
            send_token_for_email_verification(user=email)
            return render(request, "account/email_alert.html", {'username': username, 'email': email})
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
        user.save()
        login(request, user=user)
        return redirect(reverse_lazy("chat:chat"))
    
class LoginView(FormView):
    template_name = "account/login.html"
    form_class = form.LoginForm
    http_method_names = ['post', 'get']

    def post(self, request, *args, **kwargs):
        form_rendered = self.get_form(form_class=self.form_class)
        if form_rendered.is_valid():
            print(form_rendered.cleaned_data)
            email = form_rendered.cleaned_data.get('email')
            password = form_rendered.cleaned_data.get('password')
            print(email, password)
            if not request.user.is_anonymous:
                request.user.token_verified = False
                request.user.save()
                logout(request)
                print("logged user out")
            user = authenticate(request, email=email, password=password)            
            if not user:
                messages.error(request, message="Email or password is incorrect!")
            else:
                user.token_verified=False
                user.save()
                EmailOTP.objects.all().delete()
                get_otp_for_user = EmailOTP.objects.create(user=user)
                get_otp_for_user.send_otp_to_email()
                form_otp = form.OTPForm()
                return render(request, "account/otp_input.html", {'form':form_otp, 'uid':user.id})
        return redirect(reverse_lazy("account:login"))
    
class VerifyOTP(FormView):
    template_name = "account/otp_input.html"
    form_class = form.OTPForm
    http_method_names = ['post', 'get']

    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['uid'] = self.kwargs.get('uid')
        return context

    def post(self, request, *args, **kwargs):
        user_id = kwargs.get('uid')
        form_rendered = self.get_form(form_class=self.form_class)
        if form_rendered.is_valid():
            print(form_rendered.cleaned_data)
            try:
                user = CustomUser.objects.get(id=user_id)
                if user.email_verified:
                    pass
            except Exception as e:
                print(e)
                pass
            code_entered = form_rendered.cleaned_data.get('code')
            if code_entered:
                try:
                    otp_exists = EmailOTP.objects.get(user=user)
                except Exception as e:
                    print(e)
                    pass
                if code_entered != otp_exists.otp_code:
                    messages.error(request, message="Invalid Code Input")
                    return redirect(reverse_lazy("account:get_code", kwargs={'uid':user_id}))
                if not otp_exists.verify_otp():
                    EmailOTP.objects.filter(user=user).delete()
                    messages.error(request, message="Token expired!")
                    return redirect(reverse_lazy("account:get_code", kwargs={'uid':user_id}))
                login(request, user)
                EmailOTP.objects.filter(user=user).delete()
                user.token_verified = True
                user.save()
                return redirect(reverse_lazy("chat:chat"))
        return redirect(reverse_lazy("account:get_code", kwargs={'uid':user_id}))
        
@login_required(login_url=reverse_lazy("account:login"))
def logoutView(request):
    user = request.user
    print(type(user))
    user.token_verified = False
    user.save()
    logout(request)
    messages.success(request, message="Successfully logged out")
    return redirect(reverse_lazy("account:login"))
