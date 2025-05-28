from django import forms
from django.contrib.auth.forms import UserCreationForm, PasswordResetForm, PasswordChangeForm
from django.core.exceptions import ValidationError
from .country_names import COUNTRY_CHOICES
from .models import CustomUser
from dotenv import load_dotenv
import os
load_dotenv()

class SignupForm(UserCreationForm):
    CustomUser.objects.all().delete()
    username = forms.CharField(max_length=100, min_length=3, 
                               widget=forms.TextInput(attrs={'class':'form-control'}))
    email = forms.EmailField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    country = forms.ChoiceField(choices=COUNTRY_CHOICES, 
                                widget=forms.Select(attrs={'class': 'form-select'}))
    password1 = forms.CharField(max_length=255, 
                               widget=forms.PasswordInput(attrs={'class': 'form-control'}),
                               help_text="At least 8 characters, use letters & numbers.", label="Password")
    password2 = forms.CharField(max_length=255, 
                                widget=forms.PasswordInput(attrs={'class': 'form-control'}),
                                label="Confirm password")
    
    class Meta:
        model = CustomUser
        fields = ["username", "email", "country"]
     

class LoginForm(forms.Form):
    email = forms.EmailField(required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))    
    password = forms.CharField(max_length=255, 
                                widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    
class OTPForm(forms.Form):
    code = forms.CharField(max_length=os.getenv("LENGTH"), 
                           label="Enter the OTP code below")

class CustomForgetPasswordForm(PasswordResetForm):
    email = forms.EmailField(widget=forms.TextInput(attrs={'class': 'form-control'}))
    
class CustomSetPasswordForm(forms.Form):
    new_password = forms.CharField(min_length=8, max_length=255,
                                    widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    new_password2 = forms.CharField(min_length=8, max_length=255,
                                    widget=forms.PasswordInput(attrs={'class': 'form-control'}), label="Confirm password")  

    def clean(self):
        cleaned_data = super().clean()
        password1 = cleaned_data.get('new_password')
        password2 = cleaned_data.get('new_password2')
        print(cleaned_data)
        if password1 != password2:
            raise ValidationError('Password do not match')
        cleaned_data.pop('new_password2')
        return cleaned_data
    
class CustomChangePassword(forms.Form):
    old_password = forms.CharField(widget=forms.PasswordInput(attrs={'class': 'form-control'}))
    new_password1 = forms.CharField(min_length=8, max_length=255, 
                                    widget=forms.PasswordInput(attrs={'class': 'form-control'}), label="New password")
    new_password2 =forms.CharField(min_length=8, max_length=255, 
                                   widget=forms.PasswordInput(attrs={'class': 'form-control'}), label="Confirm password")
    
    def clean(self):
        cleaned_data = super().clean()
        if cleaned_data.get('new_password1') != cleaned_data.get('new_password2'):
            raise ValidationError('Password do not match.')
        cleaned_data.pop('new_password2')
        return cleaned_data