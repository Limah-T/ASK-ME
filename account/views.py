from django.shortcuts import render, redirect
from django.views.generic.edit import FormView
from django.views import View
from django.urls import reverse_lazy, reverse
from django.contrib.auth import login, logout, authenticate
from django.contrib.auth.decorators import login_required
from django.contrib import messages
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.hashers import make_password
from dotenv import load_dotenv
from .functions import send_token_for_email_verification, decode_token, send_contact_message, send_token_for_password_reset, verify_email_from_kickbox
from .country_names import DEFAULT_ROLE
from .models import CustomUser, EmailOTP, Feedback
from . import form

load_dotenv(override=True)
    
class SignUpView(FormView):
    template_name = "account/signup.html"
    form_class = form.SignupForm
    http_method_names = ["post", "get"]

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.error(request, message="You are already logged In, invalid request!")
            return redirect(reverse_lazy("chat:chat")) 
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        form_rendered = self.get_form(self.form_class)
        if form_rendered.is_valid():
            print(form_rendered.cleaned_data)
            username = form_rendered.cleaned_data.get("username")
            email = form_rendered.cleaned_data.get('email')
            valid_email = verify_email_from_kickbox(email)
            if valid_email.get("result") != "deliverable":
                messages.error(request, message="Sorry, we couldn't verify your email address, make sure you input the correct email address.")
                return redirect(reverse_lazy("account:signup"))
            user = form_rendered.save(commit=False)
            user.role = DEFAULT_ROLE
            user.save()
            if send_token_for_email_verification(email):
                return render(request, "account/email_alert.html", {'username': username, 'email': email})
            messages.error(request, message="Sorry, couldn't send for verification due to network issue or invalid credential such as email, make sure you enter the valid credential or try again later.")
            CustomUser.objects.filter(email=email).delete()
        return super().post(request, *args, **kwargs)
    
class VerifyEmailViaToken(View):
    http_method_names = ["get"]

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.error(request, message="Invalid request!")
            return redirect(reverse_lazy("chat:chat")) 
        return super().dispatch(request, *args, **kwargs)
    
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
            return render(request, "account/error_message.html")
        except CustomUser.MultipleObjectsReturned:
            return render(request, "account/error_message.html")
        except Exception as e:
            print(e)
            return render(request, "account/error_message.html")
        if user.email_verified and user.token_verified:
            return render(request, "account/error_message.html")
        user.email_verified = True
        user.token_verified = True
        user.save()
        login(request, user=user)
        messages.success(request, message="Successfully signed up")
        return redirect(reverse_lazy("chat:chat"))
    
class LoginView(FormView):
    template_name = "account/login.html"
    form_class = form.LoginForm
    http_method_names = ['post', 'get']

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.token_verified:
            messages.error(request, message="You are already logged In, invalid request!")
            return redirect(reverse_lazy("chat:chat")) 
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        form_rendered = self.get_form(form_class=self.form_class)
        if form_rendered.is_valid():
            print(form_rendered.cleaned_data)
            email = form_rendered.cleaned_data.get('email')
            password = form_rendered.cleaned_data.get('password')
            if CustomUser.objects.filter(email=email).exists():   
                user_exist = CustomUser.objects.get(email=email)
                if not user_exist.email_verified:
                    messages.error(request, message="Invalid email or password. Please try again.")
                    return redirect(reverse_lazy("account:login"))
            
            user = authenticate(request, email=email, password=password)            
            if not user:
                messages.error(request, message="Email or password is incorrect!")
            else:
                user.token_verified=False
                user.save()
                # If user has any otp generated before now
                EmailOTP.objects.filter(user=user).delete()
                get_otp_for_user = EmailOTP.objects.create(user=user)
                if get_otp_for_user.send_otp_to_email(app_name="account"):
                    form_otp = form.OTPForm()
                    print("here")
                    return render(request, "account/otp_input.html", {'form':form_otp, 'uid':user.id})
                messages.error(request, message="Sorry, the network is quite bad at the moment, please try again later.")
        return redirect(reverse_lazy("account:login"))
    
class VerifyOTP(FormView):
    template_name = "account/otp_input.html"
    form_class = form.OTPForm
    http_method_names = ['post', 'get']

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated and request.user.token_verified:
            messages.error(request, message="You are already logged In, invalid request!")
            return redirect(reverse_lazy("chat:chat")) 
        return super().dispatch(request, *args, **kwargs)

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
                messages.success(request, message="You're logged In.")
                return redirect(reverse_lazy("chat:chat"))
        return redirect(reverse_lazy("account:get_code", kwargs={'uid':user_id}))
       
class ForgetPasswordView(FormView):
    template_name = "account/forget_password.html"
    form_class = form.CustomForgetPasswordForm
    http_method_names = ['get', 'post']

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.error(request, message="You can perform such request while you are logged in!")
            return redirect(reverse_lazy("chat:chat"))
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        form_rendered = self.get_form(self.form_class)
        if form_rendered.is_valid():
            email = form_rendered.cleaned_data.get('email')
            try:
                user_exist = CustomUser.objects.get(email=email)
                user_exist.token_verified = False
                user_exist.save()
                send_token_for_password_reset(user=user_exist.email)
                return render(request, "account/email_alert.html", {'username': user_exist.username, 'email': email})
            except Exception as e:
                print("Error occured while: ", e)
                return render(request, "account/email_alert.html", {'username': '', 'email': email})         
        return super().post(request, *args, **kwargs)

def verify_password_reset_link(request):
    print(request.user)
    if request.user.is_authenticated and request.user.token_verified:
        messages.error(request, message="You can perform such request while you are logged in!")
        return redirect(reverse_lazy("chat:chat"))
    
    if request.method == 'GET':
        token = request.GET.get("token")
        print("token", token)
        if not token:
            return render(request, "account/error_message.html")
        decoded_token = decode_token(token=token)
        if not decoded_token:
            return render(request, "account/failed_verification.html")
        email = decoded_token['sub']
        try:
            user = CustomUser.objects.get(email=email)
        except Exception as e:
            print(e)
            return render(request, "account/failed_verification.html")
        if not user.email_verified:
            print("user email not verified")
            return render(request, "account/failed_verification.html")
        if user.token_verified:
            print("user token is verified already")
            return render(request, "account/failed_verification.html")
        user.token_verified = True
        user.save()
        print(user.id)
        return redirect(reverse("account:reset_password", kwargs={'uid': user.id}))
    
class ResetPasswordView(FormView):
    template_name = "account/reset_password.html"
    form_class = form.CustomSetPasswordForm
    http_method_names = ['get', 'post']
    success_url = reverse_lazy("chat:chat")

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_authenticated:
            messages.error(request, message="You can perform such request while you are logged in!")
            return redirect(reverse_lazy("chat:chat"))
        
        try:
            print(kwargs['uid'])
            self.user = CustomUser.objects.get(id=kwargs['uid'])
            print(self.user.email_verified, self.user.token_verified)
        except Exception as e:
            print("An error ocurred: ", e)
            return render(request, "account/failed_verification.html")
        
        if self.user.email_verified and self.user.token_verified:
            return super().dispatch(request, *args, **kwargs)
        return redirect(reverse_lazy("account:forget_password"))
        
    def get_context_data(self, **kwargs):
        context = super().get_context_data(**kwargs)
        context['uid'] = self.user.id
        return context
    
    def post(self, request, *args, **kwargs):
        form_rendered = self.get_form(self.form_class)
        if form_rendered.is_valid():
            new_password = form_rendered.cleaned_data.get('new_password')
            print(new_password, "password")
            same_password = authenticate(email=self.user.email, password=new_password)
            if same_password:
                messages.error(request, message="New password cannot be thesame as old password")
                return redirect(reverse_lazy('account:reset_password', kwargs={'uid': self.user.id})) 
            self.user.password = make_password(password=new_password)
            self.user.save()
            login(request, user=self.user)
            messages.success(request, message="Password changed successfully.")
            return redirect(reverse_lazy("chat:chat"))
        return super().post(request, *args, **kwargs)
    
class ChangePasswordView(LoginRequiredMixin, FormView):
    login_url = reverse_lazy("account:login")
    template_name = "account/change_password.html"
    form_class = form.CustomChangePassword
    http_method_names = ['get', 'post']

    def dispatch(self, request, *args, **kwargs):
        if request.user.is_anonymous:
            return redirect(reverse_lazy("home:home"))
        return super().dispatch(request, *args, **kwargs)

    def post(self, request, *args, **kwargs):
        form_rendered = self.get_form(self.form_class)
        if form_rendered.is_valid():
            print(form_rendered.cleaned_data)
            old_password = form_rendered.cleaned_data.get('old_password')
            new_password = form_rendered.cleaned_data.get('new_password1')
            confirm_old_password = authenticate(email=request.user.email, password=old_password)
            # checks if old password is correct
            if not confirm_old_password:
                messages.error(request, message="Your old password is incorrect.")
            else:
                same_old_password = authenticate(email=request.user.email, password=new_password)
                if same_old_password:
                    messages.error(request, message="New password cannot be thesame as old password.")
                else:
                    request.user.password = make_password(password=new_password)
                    request.user.save()
                    messages.success(request, message="Password changed successfully.")
                    login(request, request.user)
                    return redirect(reverse_lazy("chat:chat"))
        return redirect(reverse_lazy("account:change_password"))
         
@login_required(login_url=reverse_lazy("account:login"))
def logoutView(request):
    request.user.token_verified = False
    request.user.save()
    logout(request)
    messages.success(request, message="Successfully logged out")
    return redirect(reverse_lazy("account:login"))

class ContactView(FormView):
    template_name = "account/contact.html"
    form_class = form.ContactForm
    http_method_names = ["get", "post"]
    success_url = reverse_lazy("account:contact")

    def post(self, request, *args, **kwargs):
        form_rendered = self.get_form(self.form_class)
        if form_rendered.is_valid():
            name = form_rendered.cleaned_data.get("name")
            email = form_rendered.cleaned_data.get("email")
            registered_user = form_rendered.cleaned_data.get("registered_user")
            subject = form_rendered.cleaned_data.get("subject")
            message_recieved = form_rendered.cleaned_data.get("message")
            user_exist = False
            try:
                user = CustomUser.objects.get(email=email)
                user_exist = True
            except Exception as e:
                print(e)
                user_exist = False
            if registered_user == "Yes" and not user_exist:
                messages.error(request, message="This email has not be been registered, select No or create an account.")
                return redirect(reverse_lazy("account:contact"))
            if registered_user == "No" and user_exist:
                messages.error(request, message="Account already exists, select Yes to continue.")
                return redirect(reverse_lazy("account:contact"))
            if registered_user == "Yes" and user_exist:
                if not user.email_verified and not user.token_verified:
                    messages.error(request, message="This email has not be been verified, select No or create an account.")
                    return redirect(reverse_lazy("account:contact")) 
                if send_contact_message(email=user.email, name=name, sub=subject, message=message_recieved):
                    messages.success(request, message="Your message has been sent. We will get back to you shortly. Thank you!")
                    Feedback.objects.create(user=user, subject=subject, message=message_recieved)
                    return redirect(reverse_lazy("account:contact")) 
                messages.error(request, message="Sorry, couldn't send for verification due to network issue or invalid credential such as email, make sure you enter the valid credential or try again later.")
                return redirect(reverse_lazy("account:contact"))
            if registered_user == "No" and not user_exist:
                if send_contact_message(email=email, name=name, sub=subject, message=message_recieved):
                        messages.success(request, message="Your message has been sent. We will get back to you shortly. Thank you!")
                        return redirect(reverse_lazy("account:contact")) 
                messages.error(request, message="Sorry, couldn't send for verification due to network issue or invalid credential such as email, make sure you enter the valid credential or try again later.")
                return redirect(reverse_lazy("account:contact"))
        return super().post(request, *args, **kwargs)