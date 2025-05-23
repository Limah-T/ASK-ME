from django import forms
from django.contrib.auth.forms import UserCreationForm
from .country_names import COUNTRY_CHOICES
from .models import CustomUser
from dotenv import load_dotenv
import os
load_dotenv()

class SignupForm(UserCreationForm):
    username = forms.CharField(max_length=100, min_length=3, required=True, 
                               widget=forms.TextInput(attrs={'class':'form-control'}))
    email = forms.EmailField(required=True, widget=forms.TextInput(attrs={'class': 'form-control'}))
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

